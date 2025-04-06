# Web Search Functionality

DMac now includes web search capabilities in the chat interface, allowing the AI to retrieve real-time information from the internet.

## Overview

The web search functionality enables the DMac chat interface to:

1. Detect when a query requires current information
2. Search the web for that information using DuckDuckGo
3. Process and summarize the search results
4. Provide an up-to-date response with source attribution

## How It Works

### Automatic Detection

The system automatically detects when a query might need real-time information based on:

- Keywords that indicate a need for current information (e.g., "current", "latest", "recent", "today")
- Questions about dates or times
- Specific question patterns (e.g., "what is", "who is", "how to")

### Web Search Process

When a query is detected as needing real-time information, the system:

1. Extracts a search query from the user's message
2. Searches DuckDuckGo for relevant information
3. Retrieves and processes the search results
4. Summarizes the information
5. Adds the summary to the context sent to the LLM
6. Generates a response based on the enhanced context

### User Control

Users can explicitly enable web search by clicking the Research button (magnifying glass icon) in the chat interface. This is useful when:

- The automatic detection doesn't recognize a query as needing real-time information
- The user wants to ensure the most up-to-date information is used
- The user wants to compare the LLM's knowledge with current information

### Visual Indicators

The chat interface provides visual indicators when web search is being used:

- A "Researching the web for up-to-date information" message appears when web search is activated
- A note appears below the response indicating that web search was used
- The Research button is highlighted when web search is active

## Technical Implementation

The web search functionality is implemented using:

- Beautiful Soup for web scraping
- Multiple search engines:
  - DuckDuckGo as the default, privacy-friendly search engine
  - Google as an alternative for more comprehensive results
- Search result caching to improve performance and reduce API calls
- Asynchronous HTTP requests for efficient searching
- Natural language processing for query extraction and summarization
- Source attribution with direct links to the original content

## Examples

Here are some examples of queries that benefit from web search:

- "What is the current version of React?"
- "What is the latest version of Python?"
- "Who is the current CEO of Microsoft?"
- "What is the current price of Bitcoin?"
- "What are the latest developments in AI?"

## Features

### Multiple Search Engines

Users can choose between different search engines:

- **DuckDuckGo** (Default): A privacy-focused search engine that doesn't track users
- **Google**: A comprehensive search engine with extensive coverage

To change the search engine, click the dropdown arrow next to the Research button and select the desired engine.

### Result Caching

Search results are cached to improve performance and reduce the number of API calls. This means that repeated searches for the same query will be faster and won't generate additional web traffic.

Users can clear the search cache by clicking the "Clear Search Cache" option in the Research dropdown menu.

### Source Attribution

All search results include source attribution with direct links to the original content. This allows users to verify the information and explore the sources in more detail.

### Enhanced Query Detection

The system automatically detects when a query might need real-time information based on a comprehensive set of patterns and keywords, including:

- Questions about current events, latest versions, or recent developments
- Queries containing time-sensitive keywords like "current", "latest", "recent", etc.
- Questions about dates, times, or durations

## Future Enhancements

Planned enhancements for the web search functionality include:

- Support for more search engines (Bing, Brave Search, etc.)
- Better summarization of search results using AI
- Improved relevance ranking and filtering
- Support for image and video search
- User feedback on search results
- Domain-specific search options (academic, news, etc.)
