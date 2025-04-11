# MaCoder VS Code Extension Test Plan

This document outlines the test plan for the MaCoder VS Code Extension.

## Test Environment

- VS Code Stable
- VS Code Insiders
- Windows 10/11

## Test Cases

### Basic Functionality

#### TC-001: Extension Activation

1. Open VS Code
2. Verify that the extension is listed in the Extensions view
3. Verify that the extension is activated (check Output panel for "MaCoder extension is now active!" message)

**Expected Result**: The extension is listed and activated without errors.

#### TC-002: Show Information Command

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "MaCoder: Show Information"
3. Execute the command

**Expected Result**: An information message is displayed showing "MaCoder VS Code Extension v0.3.0-alpha".

### Chat Functionality

#### TC-003: Start Chat

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "MaCoder: Start Chat"
3. Execute the command

**Expected Result**: A chat panel opens with a welcome message.

#### TC-004: Send Message in Chat

1. Open the chat panel using the "MaCoder: Start Chat" command
2. Type a message in the input field
3. Click the Send button or press Enter

**Expected Result**: The message is displayed in the chat panel and a response is generated.

### Code Generation

#### TC-005: Generate Code

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "MaCoder: Generate Code"
3. Enter instructions for code generation
4. Execute the command

**Expected Result**: A new document is opened with the generated code.

### Code Explanation

#### TC-006: Explain Code (No Selection)

1. Open a code file
2. Open the Command Palette (Ctrl+Shift+P)
3. Type "MaCoder: Explain Code"
4. Execute the command

**Expected Result**: A new document is opened with an explanation of the entire file.

#### TC-007: Explain Code (With Selection)

1. Open a code file
2. Select a portion of code
3. Open the Command Palette (Ctrl+Shift+P)
4. Type "MaCoder: Explain Code"
5. Execute the command

**Expected Result**: A new document is opened with an explanation of the selected code.

#### TC-008: Explain Code from Context Menu

1. Open a code file
2. Select a portion of code
3. Right-click to open the context menu
4. Select "MaCoder: Explain Code"

**Expected Result**: A new document is opened with an explanation of the selected code.

### Code Refactoring

#### TC-009: Refactor Code (No Selection)

1. Open a code file
2. Open the Command Palette (Ctrl+Shift+P)
3. Type "MaCoder: Refactor Code"
4. Enter refactoring instructions
5. Execute the command

**Expected Result**: A new document is opened with the refactored code.

#### TC-010: Refactor Code (With Selection)

1. Open a code file
2. Select a portion of code
3. Open the Command Palette (Ctrl+Shift+P)
4. Type "MaCoder: Refactor Code"
5. Enter refactoring instructions
6. Execute the command

**Expected Result**: A new document is opened with the refactored code.

#### TC-011: Refactor Code from Context Menu

1. Open a code file
2. Select a portion of code
3. Right-click to open the context menu
4. Select "MaCoder: Refactor Code"
5. Enter refactoring instructions

**Expected Result**: A new document is opened with the refactored code.

## Edge Cases

### TC-012: Empty Input

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "MaCoder: Generate Code"
3. Leave the input empty or cancel the input
4. Execute the command

**Expected Result**: The command should gracefully handle empty input and not crash.

### TC-013: Large Files

1. Open a large code file (>1000 lines)
2. Open the Command Palette (Ctrl+Shift+P)
3. Type "MaCoder: Explain Code"
4. Execute the command

**Expected Result**: The extension should handle large files without crashing or freezing.

### TC-014: Multiple Instances

1. Open multiple VS Code windows
2. Start the chat in each window

**Expected Result**: Each window should have its own independent chat session.

## Performance Testing

### TC-015: Response Time

1. Measure the time it takes to get a response from the chat
2. Measure the time it takes to generate code
3. Measure the time it takes to explain code
4. Measure the time it takes to refactor code

**Expected Result**: Response times should be reasonable (within a few seconds).

## Compatibility Testing

### TC-016: Different Languages

Test the extension with different programming languages:
- JavaScript
- TypeScript
- Python
- Java
- C#
- Go
- Ruby

**Expected Result**: The extension should work with all supported languages.

### TC-017: Different Themes

Test the extension with different VS Code themes:
- Light theme
- Dark theme
- High contrast theme

**Expected Result**: The UI should be readable and usable in all themes.

## Test Results

| Test Case | VS Code Stable | VS Code Insiders | Notes |
|-----------|---------------|-----------------|-------|
| TC-001    |               |                 |       |
| TC-002    |               |                 |       |
| TC-003    |               |                 |       |
| TC-004    |               |                 |       |
| TC-005    |               |                 |       |
| TC-006    |               |                 |       |
| TC-007    |               |                 |       |
| TC-008    |               |                 |       |
| TC-009    |               |                 |       |
| TC-010    |               |                 |       |
| TC-011    |               |                 |       |
| TC-012    |               |                 |       |
| TC-013    |               |                 |       |
| TC-014    |               |                 |       |
| TC-015    |               |                 |       |
| TC-016    |               |                 |       |
| TC-017    |               |                 |       |
