/**
 * Chat Components
 */
import React from 'react';
import { Box, Paper, TextField, Typography } from '@mui/material';
import { ActionButton } from '../buttons';

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

export interface ChatMessageProps {
  message: Message;
}

/**
 * Chat message component
 */
export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '70%',
          borderRadius: 2,
          backgroundColor: isUser ? 'primary.light' : 'grey.100',
        }}
      >
        <Typography variant="body1">{message.content}</Typography>
        <Typography variant="caption" color="text.secondary">
          {message.timestamp.toLocaleTimeString()}
        </Typography>
      </Paper>
    </Box>
  );
};

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
}

/**
 * Chat input component
 */
export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage }) => {
  const [message, setMessage] = React.useState('');
  
  const handleSendMessage = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <TextField
        fullWidth
        multiline
        maxRows={4}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type a message..."
        variant="outlined"
        size="small"
      />
      <ActionButton onClick={handleSendMessage} disabled={!message.trim()}>
        Send
      </ActionButton>
    </Box>
  );
};
