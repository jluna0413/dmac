# OpenCanvas Integration

## Overview
This document details the implementation of a flexible container layout for the Langchain OpenCanvas feature, allowing it to open beside the chat window instead of in a new tab.

## Changes Made

### 1. Created OpenCanvas CSS
- Created a new CSS file `opencanvas.css` with styles for the flexible container layout
- Implemented responsive design for different screen sizes
- Added styling for the OpenCanvas header, content, and tools

### 2. Updated Chat Template
- Added the OpenCanvas container to the chat.html template
- Added OpenCanvas CSS link to the head section
- Added OpenCanvas tools (New, Save, Run buttons)
- Added a close button to the OpenCanvas header

### 3. Enhanced OpenCanvas JavaScript
- Updated the `openCanvas()` method to open the canvas in a flexible container
- Added a `closeCanvas()` method to handle closing the canvas
- Added a `loadOpenCanvasFrame()` method to load the OpenCanvas in an iframe
- Implemented event handlers for the OpenCanvas tools

### 4. Implemented Flexible Layout
- Used CSS flexbox to create a responsive layout
- Added classes to toggle the flexible layout when OpenCanvas is opened/closed
- Ensured the layout works well on different screen sizes

## Files Changed
- `dashboard/static/css/opencanvas.css`: New file with OpenCanvas styles
- `dashboard/templates/chat.html`: Updated to include OpenCanvas container
- `dashboard/static/js/unified-input.js`: Enhanced OpenCanvas methods

## Implementation Details

### Flexible Container Layout
The implementation uses a flexible container layout with the following features:
- When OpenCanvas is closed, the chat window takes up the full width
- When OpenCanvas is opened, the chat window and OpenCanvas share the space
- On desktop, they appear side by side
- On mobile, they stack vertically

### OpenCanvas Container
The OpenCanvas container includes:
- A header with a title and close button
- A tools section with New, Save, and Run buttons
- A content area that loads the OpenCanvas in an iframe

### JavaScript Methods
- `openCanvas()`: Opens the OpenCanvas in the flexible container
- `closeCanvas()`: Closes the OpenCanvas container
- `loadOpenCanvasFrame()`: Loads the OpenCanvas URL in an iframe

## User Experience
- Users can now see both the chat and OpenCanvas at the same time
- They can interact with both without switching tabs
- The layout is responsive and works well on different screen sizes
- The OpenCanvas can be easily closed when not needed

## Future Improvements
- Add drag handle to resize the containers
- Implement local storage to remember the user's preferred layout
- Add more OpenCanvas tools and features
- Implement real-time collaboration features
- Add ability to save and load OpenCanvas workflows
