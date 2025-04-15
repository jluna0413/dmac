/**
 * Redux Selectors
 */
import { RootState } from '../store';

// Models selectors
export const selectModels = (state: RootState) => state.models.items;
export const selectSelectedModel = (state: RootState) => state.models.selectedModel;
export const selectModelsLoading = (state: RootState) => state.models.loading;
export const selectModelsError = (state: RootState) => state.models.error;

// Chat selectors
export const selectMessages = (state: RootState) => state.chat.messages;
export const selectChatLoading = (state: RootState) => state.chat.loading;
export const selectChatError = (state: RootState) => state.chat.error;

// UI selectors
export const selectTheme = (state: RootState) => state.ui.theme;
export const selectSidebarOpen = (state: RootState) => state.ui.sidebarOpen;
export const selectActiveView = (state: RootState) => state.ui.activeView;
export const selectNotifications = (state: RootState) => state.ui.notifications;

// Auth selectors
export const selectUser = (state: RootState) => state.auth.user;
export const selectToken = (state: RootState) => state.auth.token;
export const selectAuthLoading = (state: RootState) => state.auth.loading;
export const selectAuthError = (state: RootState) => state.auth.error;
export const selectIsAuthenticated = (state: RootState) => !!state.auth.token;
