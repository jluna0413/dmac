import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/auth_service.dart';
import 'package:dmac_app/src/widgets/dmac_app_bar.dart';
import 'package:dmac_app/src/widgets/chat/voice_input_button.dart';
import 'package:dmac_app/src/widgets/chat/file_upload_button.dart';
import 'package:dmac_app/src/widgets/chat/deep_research_button.dart';
import 'package:dmac_app/src/widgets/chat/think_button.dart';
import 'package:dmac_app/src/utils/app_theme.dart';

/// Chat screen with OpenCanvas integration
class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage() {
    if (_messageController.text.trim().isEmpty) return;

    final message = _messageController.text.trim();
    _addMessage(ChatMessage(
      text: message,
      isUser: true,
      timestamp: DateTime.now(),
    ));

    // Clear the input field
    _messageController.clear();

    // Simulate typing indicator
    setState(() {
      _isTyping = true;
    });

    // Simulate response after a delay
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _isTyping = false;
        });
        _addMessage(ChatMessage(
          text: 'This is a simulated response to: "$message"',
          isUser: false,
          timestamp: DateTime.now(),
        ));
      }
    });
  }

  void _addMessage(ChatMessage message) {
    setState(() {
      _messages.add(message);
    });

    // Scroll to the bottom
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const DMacAppBar(
        title: 'Chat',
      ),
      body: Column(
        children: [
          Expanded(
            child: _messages.isEmpty
                ? _buildWelcomeMessage()
                : _buildChatMessages(),
          ),
          if (_isTyping) _buildTypingIndicator(),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildWelcomeMessage() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 64,
            color: Theme.of(context).colorScheme.primary.withOpacity(0.5),
          ),
          const SizedBox(height: 16),
          Text(
            'Welcome to DMac Chat',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 32),
            child: Text(
              'Start a conversation with the AI agent swarm. You can ask questions, request tasks, or just chat.',
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              _messageController.text = 'Hello, how can you help me today?';
              _sendMessage();
            },
            icon: const Icon(Icons.send),
            label: const Text('Start Conversation'),
          ),
        ],
      ),
    );
  }

  Widget _buildChatMessages() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        return _buildMessageBubble(message);
      },
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.isUser;
    final bubbleColor = isUser
        ? Theme.of(context).colorScheme.primary
        : Theme.of(context).colorScheme.surface;
    final textColor = isUser
        ? Theme.of(context).colorScheme.onPrimary
        : Theme.of(context).colorScheme.onSurface;
    final alignment = isUser ? Alignment.centerRight : Alignment.centerLeft;
    final borderRadius = isUser
        ? const BorderRadius.only(
            topLeft: Radius.circular(16),
            topRight: Radius.circular(16),
            bottomLeft: Radius.circular(16),
          )
        : const BorderRadius.only(
            topLeft: Radius.circular(16),
            topRight: Radius.circular(16),
            bottomRight: Radius.circular(16),
          );

    return Align(
      alignment: alignment,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: bubbleColor,
          borderRadius: borderRadius,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.text,
              style: TextStyle(color: textColor),
            ),
            const SizedBox(height: 4),
            Text(
              _formatTimestamp(message.timestamp),
              style: TextStyle(
                color: textColor.withOpacity(0.7),
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final messageDate = DateTime(
      timestamp.year,
      timestamp.month,
      timestamp.day,
    );

    final time = '${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';

    if (messageDate == today) {
      return 'Today, $time';
    } else if (messageDate == today.subtract(const Duration(days: 1))) {
      return 'Yesterday, $time';
    } else {
      return '${timestamp.day}/${timestamp.month}/${timestamp.year}, $time';
    }
  }

  Widget _buildTypingIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      alignment: Alignment.centerLeft,
      child: Row(
        children: [
          const SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            'AI is typing...',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Voice input button
          VoiceInputButton(
            onVoiceInput: (text) {
              _messageController.text = text;
            },
          ),
          
          // File upload button
          FileUploadButton(
            onFileSelected: (file) {
              // Handle file upload
              _addMessage(ChatMessage(
                text: 'Uploaded file: ${file.name}',
                isUser: true,
                timestamp: DateTime.now(),
              ));
            },
          ),
          
          // Text input field
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: 'Type a message...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Theme.of(context).colorScheme.surface,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
              ),
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          
          const SizedBox(width: 8),
          
          // Deep research button
          DeepResearchButton(
            onResearchRequested: () {
              // Handle deep research
              _addMessage(ChatMessage(
                text: 'Starting deep research on: ${_messageController.text}',
                isUser: true,
                timestamp: DateTime.now(),
              ));
            },
          ),
          
          // Think button
          ThinkButton(
            onThinkRequested: () {
              // Handle deep thinking
              _addMessage(ChatMessage(
                text: 'Thinking deeply about: ${_messageController.text}',
                isUser: true,
                timestamp: DateTime.now(),
              ));
            },
          ),
          
          // Send button
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: _sendMessage,
            color: Theme.of(context).colorScheme.primary,
          ),
        ],
      ),
    );
  }
}

/// Model class for chat messages
class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
  });
}
