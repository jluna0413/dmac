# Hot Words Functionality

DMac now includes hot word detection in the chat interface, allowing users to trigger different modes automatically by using specific words or phrases in their messages.

## Overview

The hot word functionality enables the DMac chat interface to:

1. Detect specific trigger words or phrases in user messages
2. Automatically activate the appropriate mode based on detected hot words
3. Provide visual feedback to show which mode was activated
4. Keep the buttons as a fallback and for visual indication

## How It Works

### Hot Word Categories

The system recognizes three categories of hot words:

1. **Web Search Hot Words**: Trigger web search mode to retrieve real-time information
2. **Deep Thinking Hot Words**: Trigger deep thinking mode for more thorough analysis
3. **Deep Research Hot Words**: Trigger a combination of web search and deep thinking

### Detection Process

When a user sends a message, the system:

1. Checks the message for hot words in each category
2. If hot words are detected, activates the corresponding mode
3. Shows a toast notification indicating which mode was activated
4. Updates the UI to reflect the active mode

### User Control

Users can still manually activate modes using the buttons in the interface. The hot word detection simply provides a more convenient way to trigger these modes without having to click buttons.

## Hot Word Examples

### Web Search Hot Words

These words trigger web search mode:

- search
- look up
- find
- google
- web
- internet
- current
- latest
- recent
- now
- today
- what is the
- browse
- online
- information

### Deep Thinking Hot Words

These words trigger deep thinking mode:

- think
- ponder
- analyze
- consider
- reflect
- contemplate
- deep dive
- deep thinking
- deep analysis
- carefully
- thoroughly

### Deep Research Hot Words

These words trigger both web search and deep thinking modes:

- research
- brainstorm
- investigate
- explore
- study
- deep research
- comprehensive
- extensive
- in-depth
- detailed

## Examples

Here are some examples of messages that would trigger different modes:

- "Search for the latest version of Flutter" - Triggers web search mode
- "Can you think deeply about the implications of this design?" - Triggers deep thinking mode
- "I need you to research the history of artificial intelligence" - Triggers deep research mode

## Technical Implementation

The hot word functionality is implemented using:

- JavaScript pattern matching to detect hot words
- Event-driven architecture to trigger mode changes
- Toast notifications for user feedback
- Visual indicators to show active modes

## Future Enhancements

Planned enhancements for the hot word functionality include:

- User-customizable hot words
- Context-aware hot word detection
- Multi-language support
- Learning from user behavior to improve detection
- More granular mode activation based on specific hot words
