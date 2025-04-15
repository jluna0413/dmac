# MaCoder VS Code Extension User Guide

This guide will help you get started with the MaCoder VS Code Extension.

## Installation

### From VSIX File

1. Download the `vscode-macoder-0.3.0-alpha.vsix` file
2. Open VS Code
3. Go to the Extensions view (Ctrl+Shift+X)
4. Click on the "..." menu in the top-right corner
5. Select "Install from VSIX..."
6. Navigate to the downloaded VSIX file and select it
7. Click "Install"

## Features

### Chat with MaCoder

The MaCoder chat interface allows you to interact with the AI assistant directly.

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "MaCoder: Start Chat"
3. A chat panel will open
4. Type your message in the input field and press Enter or click Send
5. MaCoder will respond to your message

### Generate Code

MaCoder can generate code based on your instructions.

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "MaCoder: Generate Code"
3. Enter your instructions for code generation
4. MaCoder will generate code and open it in a new document

Example instructions:
- "Create a function to calculate the Fibonacci sequence"
- "Write a class for managing a shopping cart"
- "Generate a REST API endpoint for user authentication"

### Explain Code

MaCoder can explain code to help you understand it better.

1. Open a code file
2. (Optional) Select the specific code you want explained
3. Open the Command Palette (Ctrl+Shift+P) or right-click on the selected code
4. Type "MaCoder: Explain Code" or select it from the context menu
5. MaCoder will explain the code and open the explanation in a new document

### Refactor Code

MaCoder can help you refactor your code based on your instructions.

1. Open a code file
2. (Optional) Select the specific code you want to refactor
3. Open the Command Palette (Ctrl+Shift+P) or right-click on the selected code
4. Type "MaCoder: Refactor Code" or select it from the context menu
5. Enter your refactoring instructions
6. MaCoder will refactor the code and open it in a new document

Example refactoring instructions:
- "Improve performance"
- "Add comments"
- "Convert to async/await"
- "Split into smaller functions"

## Tips and Best Practices

### For Better Code Generation

- Be specific in your instructions
- Include details about the programming language, frameworks, or libraries you're using
- Specify any naming conventions or coding standards you want to follow

### For Better Code Explanation

- Select only the specific code you want explained
- For large files, select smaller sections for more detailed explanations

### For Better Code Refactoring

- Clearly state what aspects of the code you want to improve
- Mention any specific patterns or techniques you want to use
- Specify any constraints or requirements that must be maintained

## Troubleshooting

### Extension Not Working

If the extension is not working as expected:

1. Check that the extension is installed and enabled
2. Restart VS Code
3. Check the Output panel for any error messages (View > Output, then select "MaCoder" from the dropdown)

### Slow Response Times

If you're experiencing slow response times:

1. Try with smaller code snippets
2. Check your internet connection
3. Restart VS Code

## Feedback and Support

If you have any feedback or need support, please:

1. Open an issue on the GitHub repository
2. Include detailed information about the problem
3. Attach screenshots or code examples if applicable

## Future Updates

Stay tuned for future updates that will include:

- Integration with more model providers
- Deep research and web search capabilities
- Enhanced UI/UX
- Full activity bar view implementation
