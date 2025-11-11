"""
Core agent implementation for the Baby Manus agentic loop.
This module contains the Agent class and event handling for streaming responses.
"""

from typing import AsyncGenerator, List, Dict, Any, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed
from dataclasses import dataclass, field
from pydantic import BaseModel
import json

from clients import openai_client


# Event classes for streaming API
class AgentEvent:
    """Base class for agent events"""
    pass


class EventText(AgentEvent):
    """Event for text content"""
    def __init__(self, text: str):
        self.text = text


class EventInputJson(AgentEvent):
    """Event for partial JSON input"""
    def __init__(self, partial_json: str):
        self.partial_json = partial_json


class EventToolUse(AgentEvent):
    """Event for tool usage"""
    def __init__(self, tool):
        self.tool = tool


class EventToolResult(AgentEvent):
    """Event for tool execution result"""
    def __init__(self, tool, result: str):
        self.tool = tool
        self.result = result


@dataclass
class Agent:
    """
    Agent class that orchestrates the agentic loop with OpenAI.
    Supports multi-step reasoning and tool execution.
    """

    system_prompt: str
    model: str
    tools: List[BaseModel]
    messages: List[ChatCompletionMessageParam] = field(default_factory=list)
    available_tools: List[ChatCompletionToolParam] = field(default_factory=list)

    def __post_init__(self):
        # Convert tools to OpenAI format
        self.available_tools = []
        for tool_class in self.tools:
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool_class.__name__,
                    "description": tool_class.__doc__ or "",
                    "parameters": tool_class.model_json_schema(),
                }
            }
            self.available_tools.append(tool_schema)

    def add_user_message(self, message: str):
        """Add a user message to the conversation history."""
        self.messages.append({"role": "user", "content": message})

    async def agentic_loop(self) -> AsyncGenerator[AgentEvent, None]:
        """
        Main agentic loop that streams responses from OpenAI and executes tools.
        Supports recursive tool calling for multi-step reasoning.
        """
        if openai_client is None:
            yield EventText(text="Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            return

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3), wait=wait_fixed(3)
        ):
            with attempt:
                # Prepare messages for OpenAI
                openai_messages = []
                if self.system_prompt:
                    openai_messages.append({"role": "system", "content": self.system_prompt})
                openai_messages.extend(self.messages)

                # Create streaming request
                stream = openai_client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    tools=self.available_tools,
                    stream=True,
                    max_tokens=8000,
                )

                accumulated_content = ""
                accumulated_tool_calls = {}

                for chunk in stream:
                    delta = chunk.choices[0].delta

                    # Handle text content
                    if delta.content:
                        accumulated_content += delta.content
                        yield EventText(text=delta.content)

                    # Handle tool calls
                    if delta.tool_calls:
                        for tool_call_delta in delta.tool_calls:
                            index = tool_call_delta.index
                            tool_call_id = tool_call_delta.id

                            # Use index as the key since it's consistent across chunks
                            key = f"index_{index}"

                            if key not in accumulated_tool_calls:
                                accumulated_tool_calls[key] = {
                                    "id": tool_call_id or f"call_{index}",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                }

                            # Update the ID if we get it
                            if tool_call_id:
                                accumulated_tool_calls[key]["id"] = tool_call_id

                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    accumulated_tool_calls[key]["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    accumulated_tool_calls[key]["function"]["arguments"] += tool_call_delta.function.arguments

                                # Yield partial JSON for function arguments
                                yield EventInputJson(partial_json=accumulated_tool_calls[key]["function"]["arguments"])

                # Execute tool calls if any
                tool_calls_executed = False
                if accumulated_tool_calls:
                    for tool_call in accumulated_tool_calls.values():
                        tool_name = tool_call["function"]["name"]
                        tool_args_str = tool_call["function"]["arguments"]

                        # Parse tool arguments with error handling
                        try:
                            tool_args = json.loads(tool_args_str)
                        except json.JSONDecodeError as e:
                            error_msg = f"Failed to parse tool arguments as JSON: {e}. Arguments: {tool_args_str}"
                            yield EventText(text=f"Error: {error_msg}")
                            # Clear accumulated tool calls to prevent infinite retry
                            accumulated_tool_calls.clear()
                            break

                        # Find and execute the tool
                        for tool_class in self.tools:
                            if tool_class.__name__ == tool_name:
                                # Create tool instance with arguments
                                tool_instance = tool_class(**tool_args)

                                # Execute tool
                                yield EventToolUse(tool=tool_instance)
                                result = await tool_instance()

                                yield EventToolResult(tool=tool_instance, result=result)

                                # Add tool result to conversation
                                self.messages.append({
                                    "role": "assistant",
                                    "content": accumulated_content,
                                    "tool_calls": [tool_call]
                                })

                                self.messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "content": result
                                })

                                tool_calls_executed = True
                                break

                    # If we had tool calls and they were executed successfully, recursively continue the loop
                    if tool_calls_executed:
                        async for event in self.agentic_loop():
                            yield event