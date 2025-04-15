/**
 * UI Slice
 */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Define the state type
interface UiState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeView: string;
  notifications: {
    id: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
  }[];
}

// Define the initial state
const initialState: UiState = {
  theme: 'light',
  sidebarOpen: true,
  activeView: 'chat',
  notifications: [],
};

// Create the slice
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setActiveView: (state, action: PayloadAction<string>) => {
      state.activeView = action.payload;
    },
    addNotification: (state, action: PayloadAction<{
      message: string;
      type: 'info' | 'success' | 'warning' | 'error';
    }>) => {
      const id = Date.now().toString();
      state.notifications.push({
        id,
        ...action.payload,
      });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
  },
});

// Export actions
export const {
  setTheme,
  toggleSidebar,
  setSidebarOpen,
  setActiveView,
  addNotification,
  removeNotification,
  clearNotifications,
} = uiSlice.actions;

// Export reducer
export default uiSlice.reducer;
