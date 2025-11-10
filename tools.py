
class ToolSearchAndReplace(Tool):
    """
    Search and replace a specific pattern in files across the project.
    """

    pattern: str = Field(description="The text pattern to search for")
    replacement: str = Field(description="The text to replace the found pattern with")
    directory: str = Field(description="The directory in which to perform the search and replace")

    def _run(self) -> str:
        if docker_client is None:
            return "Error: Docker client not available. Please ensure Docker is running."

        try:
            # Searching in the specified directory
            search_path = Path(self.directory)
            if not search_path.is_dir():
                return f"Error: The specified directory '{self.directory}' does not exist."

            # Walk through the directory
            for root, _, files in os.walk(search_path):
                for file in files:
                    file_path = Path(root) / file
                    # Read file content
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Replace content
                    new_content = content.replace(self.pattern, self.replacement)

                    # If modified, write it back
                    if content != new_content:
                        with open(file_path, 'w') as f:
                            f.write(new_content)

            return "Search and replace completed successfully."
        except Exception as e:
            return f"Error during search and replace: {e}" 
