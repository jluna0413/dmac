const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Create a temporary directory for the minimal package
const tempDir = path.join(__dirname, 'minimal-sidebar-test');
if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
}

// Create media directory for icons
const mediaDir = path.join(tempDir, 'media');
if (!fs.existsSync(mediaDir)) {
    fs.mkdirSync(mediaDir, { recursive: true });
}

const iconsDir = path.join(mediaDir, 'icons');
if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir, { recursive: true });
}

// Create a minimal package.json
const packageJson = {
    "name": "vscode-macoder",
    "displayName": "MaCoder",
    "description": "MaCoder VS Code Extension with full sidebar UI",
    "version": "0.4.0-alpha",
    "publisher": "dmac",
    "repository": {
        "type": "git",
        "url": "https://github.com/jluna0413/dmac.git"
    },
    "engines": {
        "vscode": "^1.60.0"
    },
    "categories": [
        "Programming Languages",
        "Machine Learning",
        "Other"
    ],
    "activationEvents": [
        "onView:macoder.chat",
        "onView:macoder.codeGeneration",
        "onCommand:macoder.showInfo"
    ],
    "main": "./extension.js",
    "contributes": {
        "viewsContainers": {
            "activitybar": [
                {
                    "id": "macoder-sidebar",
                    "title": "MaCoder",
                    "icon": "media/icons/macoder-icon.svg"
                }
            ]
        },
        "views": {
            "macoder-sidebar": [
                {
                    "id": "macoder.chat",
                    "name": "Chat",
                    "contextualTitle": "MaCoder Chat"
                },
                {
                    "id": "macoder.codeGeneration",
                    "name": "Code Generation",
                    "contextualTitle": "Code Generation"
                }
            ]
        },
        "commands": [
            {
                "command": "macoder.showInfo",
                "title": "MaCoder: Show Information"
            }
        ]
    },
    "scripts": {
        "vscode:prepublish": "echo Preparing package"
    },
    "license": "MIT"
};

// Create a minimal extension.js
const extensionJs = `
const vscode = require('vscode');

/**
 * Simple view provider for the chat view
 */
class ChatViewProvider {
    constructor(extensionUri) {
        this.extensionUri = extensionUri;
    }

    resolveWebviewView(webviewView, context, _token) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };

        webviewView.webview.html = \`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>MaCoder Chat</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        padding: 10px;
                    }
                    .container {
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                    }
                    .chat-container {
                        flex: 1;
                        overflow-y: auto;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 4px;
                        padding: 10px;
                        margin-bottom: 10px;
                    }
                    .input-container {
                        display: flex;
                        flex-direction: column;
                        gap: 8px;
                    }
                    textarea {
                        resize: none;
                        padding: 8px;
                        border: 1px solid var(--vscode-input-border);
                        background-color: var(--vscode-input-background);
                        color: var(--vscode-input-foreground);
                        border-radius: 4px;
                    }
                    button {
                        align-self: flex-end;
                        padding: 6px 12px;
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="chat-container">
                        <p>Welcome to MaCoder Chat! This is a placeholder for the chat interface.</p>
                    </div>
                    <div class="input-container">
                        <textarea rows="3" placeholder="Type your message here..."></textarea>
                        <button>Send</button>
                    </div>
                </div>
            </body>
            </html>
        \`;
    }
}

/**
 * Simple view provider for the code generation view
 */
class CodeGenerationViewProvider {
    constructor(extensionUri) {
        this.extensionUri = extensionUri;
    }

    resolveWebviewView(webviewView, context, _token) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };

        webviewView.webview.html = \`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Code Generation</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        padding: 10px;
                    }
                    .container {
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                    }
                    h3 {
                        margin-top: 0;
                        margin-bottom: 8px;
                    }
                    textarea {
                        resize: vertical;
                        padding: 8px;
                        border: 1px solid var(--vscode-input-border);
                        background-color: var(--vscode-input-background);
                        color: var(--vscode-input-foreground);
                        border-radius: 4px;
                        margin-bottom: 10px;
                    }
                    select {
                        padding: 4px 8px;
                        border: 1px solid var(--vscode-dropdown-border);
                        background-color: var(--vscode-dropdown-background);
                        color: var(--vscode-dropdown-foreground);
                        border-radius: 4px;
                        margin-bottom: 10px;
                    }
                    button {
                        align-self: flex-start;
                        padding: 6px 12px;
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h3>Instructions</h3>
                    <textarea rows="5" placeholder="Describe the code you want to generate..."></textarea>
                    
                    <label for="language">Language:</label>
                    <select id="language">
                        <option value="javascript">JavaScript</option>
                        <option value="typescript">TypeScript</option>
                        <option value="python">Python</option>
                        <option value="java">Java</option>
                    </select>
                    
                    <button>Generate Code</button>
                </div>
            </body>
            </html>
        \`;
    }
}

/**
 * Activate the extension
 */
function activate(context) {
    console.log('MaCoder extension is now active!');
    
    // Register chat view provider
    const chatViewProvider = new ChatViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('macoder.chat', chatViewProvider)
    );
    
    // Register code generation view provider
    const codeGenerationViewProvider = new CodeGenerationViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('macoder.codeGeneration', codeGenerationViewProvider)
    );
    
    // Register show info command
    const showInfoCommand = vscode.commands.registerCommand('macoder.showInfo', () => {
        vscode.window.showInformationMessage('MaCoder VS Code Extension v0.4.0-alpha');
    });
    
    context.subscriptions.push(showInfoCommand);
}

/**
 * Deactivate the extension
 */
function deactivate() {}

module.exports = {
    activate,
    deactivate
};
`;

// Create a minimal icon
const iconSvg = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;

// Create a minimal README.md
const readmeContent = `# MaCoder VS Code Extension

A VS Code extension for MaCoder with a full UI in the Activity Bar.

## Features

- MaCoder integration
- Chat interface in the sidebar
- Code generation in the sidebar
- And more!

## Requirements

- VS Code 1.60.0 or higher

## Installation

1. Download the VSIX file
2. Install using VS Code's "Install from VSIX" command
`;

// Create a minimal LICENSE file
const licenseContent = `MIT License

Copyright (c) 2025 DMac

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`;

// Write the files to the temporary directory
fs.writeFileSync(path.join(tempDir, 'package.json'), JSON.stringify(packageJson, null, 2));
fs.writeFileSync(path.join(tempDir, 'extension.js'), extensionJs);
fs.writeFileSync(path.join(tempDir, 'README.md'), readmeContent);
fs.writeFileSync(path.join(tempDir, 'LICENSE'), licenseContent);
fs.writeFileSync(path.join(iconsDir, 'macoder-icon.svg'), iconSvg);

// Package the extension
try {
    console.log('Packaging minimal sidebar test extension...');
    execSync('npx vsce package --no-dependencies --no-yarn', { cwd: tempDir, stdio: 'inherit' });
    
    // Copy the VSIX file to the parent directory
    const vsixFile = fs.readdirSync(tempDir).find(file => file.endsWith('.vsix'));
    if (vsixFile) {
        fs.copyFileSync(path.join(tempDir, vsixFile), path.join(__dirname, vsixFile));
        console.log(`Successfully packaged extension: ${vsixFile}`);
    }
} catch (error) {
    console.error('Failed to package extension:', error);
}
