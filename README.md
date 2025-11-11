# 🤖 Baby Manus - AI Agentic Loop

A terminal-based AI agent that can perform complex coding tasks through iterative reasoning and tool execution, inspired by advanced agents like Manus.

## 🚀 Features

- **Multi-step reasoning**: Break down complex tasks into manageable steps
- **Tool execution**: Run commands and create files in a Docker container
- **Streaming responses**: Real-time feedback as the agent thinks and acts
- **User interaction**: Ask clarifying questions when needed
- **Docker isolation**: Safe code execution in isolated containers
- **OpenAI integration**: Powered by GPT-4o-mini with function calling

## 🏗️ Architecture

The agent consists of five main components:

- **`agent.py`**: Core Agent class with the agentic loop
- **`tools.py`**: Tools for interacting with the Docker environment and git
- **`clients.py`**: OpenAI and Docker client initialization
- **`simple_ui.py`**: Terminal user interface
- **`branch_review.py`**: Host tool for reviewing and merging agent-created branches

## 📋 Prerequisites

1. **Python 3.12+**
2. **OpenAI API Key**: Set as environment variable `OPENAI_API_KEY`
3. **Docker**: For containerized code execution (optional but recommended)

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd simple-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

   Or create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## 🚀 Usage

Run the agent:
```bash
python main.py
```

The agent will start a terminal interface where you can enter requests like:
- "Create a simple Python script that prints 'Hello, World!'"
- "Write a FastAPI server with a /health endpoint"
- "Build a basic calculator in Python"
- "Create a simple web page with HTML and CSS"

## 🛠️ Available Tools

### Development Container Tools
### ToolRunCommandInDevContainer
Execute commands in a Python development container with:
- Python 3.12 installed
- Git support for version control
- Port 8888 exposed for web servers
- Project directory mounted at `/app`
- Isolated execution environment

### ToolUpsertFile
Create or update files in the development container.

### Git Management Tools
### ToolGitStatus
Check current git status and see staged/unstaged changes.

### ToolGitBranch
View current branch and available branches.

### ToolGitCreateBranch
Create a new feature branch for development work.

### ToolGitAddFiles
Stage files for commit (use '.' for all files).

### ToolGitCommit
Commit staged changes with a descriptive message.

### ToolGitPushBranch
Push the current branch to remote repository.

### ToolInteractWithUser
Ask the user for clarification or additional information.

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DOCKER_HOST`: Docker daemon host (optional)

### Docker Container
The agent automatically starts a `python-dev` container when initialized. This container:
- Runs Python 3.12 with git support
- Exposes port 8888 to the host
- Mounts the project directory at `/app` for direct file access
- Provides isolated development environment

## 🌿 Branch-Based Development Workflow

The agent follows a structured workflow to ensure safe, reviewable code changes:

### Agent Workflow
1. **Feature Branch Creation**: Agent creates a descriptive feature branch for each task
2. **Code Development**: Agent makes changes and tests them within the container
3. **Version Control**: Agent stages, commits, and pushes changes to the branch
4. **Host Review**: Agent signals completion and waits for host approval

### Host Review Process
1. **Review Changes**: Use `python branch_review.py` to examine agent-created branches
2. **Inspect Code**: Review diffs, commits, and changed files
3. **Approve/Merge**: Merge approved branches into main branch
4. **Reject/Delete**: Delete branches that don't meet requirements

### Usage Example
```bash
# Agent creates a feature branch and makes changes
# When complete, agent pushes the branch

# Host reviews the changes
python branch_review.py

# Host can then merge or reject the branch
```

This workflow ensures:
- **Isolation**: Each task gets its own branch
- **Reviewability**: Host can inspect all changes before merging
- **Safety**: Main branch remains stable
- **Traceability**: Clear commit history for each feature

## 📝 Example Interactions

### Simple Task
```
👤 You: Create a Python script that prints the current date and time

🤖 Agent: I'll create a simple Python script that prints the current date and time using the datetime module.

🔧 Using tool: ToolUpsertFile
   File: /app/datetime_script.py

✅ Tool result: File written successfully

🔧 Using tool: ToolRunCommandInDevContainer
   Command: python datetime_script.py

✅ Tool result: 2024-01-15 14:30:25.123456

The script has been created and executed successfully! The output shows the current date and time.
```

### Complex Task
```
👤 You: Build a simple REST API with FastAPI that has endpoints for creating, reading, and deleting items

🤖 Agent: I'll build a FastAPI application with CRUD operations. This will involve:
1. Creating the FastAPI app with endpoints
2. Adding data models
3. Implementing the CRUD operations
4. Running the server to test it

Let me start by creating the main application file...
```

## 🧪 Testing

Run the import test to verify everything is set up correctly:
```bash
python test_imports.py
```

The agent includes comprehensive error handling for Docker operations:
- Container startup with proper cleanup of existing containers
- Real-time status checking with `status` command
- Detailed error messages for troubleshooting
- Automatic retry logic for API failures

## 🔍 How It Works

1. **User Input**: You provide a task description
2. **Reasoning**: The agent uses OpenAI to understand and plan the task
3. **Tool Execution**: The agent calls tools to execute commands or create files
4. **Iteration**: Results are fed back to continue multi-step tasks
5. **Completion**: Final results are presented to the user

The agentic loop supports:
- **Streaming**: Real-time response generation
- **Tool Calling**: Function execution with structured parameters
- **Memory**: Conversation history maintained across steps
- **Error Handling**: Retry logic for API failures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify it for your own purposes.

## 🙏 Acknowledgments

Inspired by the tutorial "Creating your own agentic loop from scratch" and advanced AI agents like Manus. Built with OpenAI's GPT models and Docker for safe code execution.
