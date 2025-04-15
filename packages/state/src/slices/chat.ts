/**
 * Chat Slice
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { ModelApiClient } from '@dmac/api';

// Define message type
interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

// Define the state type
interface ChatState {
  messages: Message[];
  loading: boolean;
  error: string | null;
}

// Define the initial state
const initialState: ChatState = {
  messages: [],
  loading: false,
  error: null,
};

// Create async thunks
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ modelId, content }: { modelId: string; content: string }, { rejectWithValue }) => {
    try {
      const apiClient = new ModelApiClient('http://localhost:3000');
      const response = await apiClient.generateText(modelId, content);
      return response.text;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

// Create the slice
const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    clearMessages: (state) => {
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({
          id: Date.now().toString(),
          content: action.payload,
          sender: 'assistant',
          timestamp: new Date(),
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

// Export actions
export const { addMessage, clearMessages } = chatSlice.actions;

// Export reducer
export default chatSlice.reducer;
