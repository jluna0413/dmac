/**
 * Redux Middleware
 */
import { Middleware } from 'redux';
import { RootState } from '../store';

/**
 * Logger middleware
 */
export const loggerMiddleware: Middleware<{}, RootState> = (store) => (next) => (action) => {
  console.log('dispatching', action);
  const result = next(action);
  console.log('next state', store.getState());
  return result;
};

/**
 * Local storage middleware
 */
export const localStorageMiddleware: Middleware<{}, RootState> = (store) => (next) => (action) => {
  const result = next(action);
  
  // Save specific parts of the state to local storage
  const state = store.getState();
  
  // Save auth state
  localStorage.setItem('auth', JSON.stringify({
    token: state.auth.token,
    user: state.auth.user,
  }));
  
  // Save UI preferences
  localStorage.setItem('ui', JSON.stringify({
    theme: state.ui.theme,
    sidebarOpen: state.ui.sidebarOpen,
  }));
  
  return result;
};

/**
 * API error middleware
 */
export const apiErrorMiddleware: Middleware<{}, RootState> = (store) => (next) => (action) => {
  const result = next(action);
  
  // Check if the action is a rejected API call
  if (action.type.endsWith('/rejected') && action.payload) {
    // Dispatch a notification action
    store.dispatch({
      type: 'ui/addNotification',
      payload: {
        message: `API Error: ${action.payload}`,
        type: 'error',
      },
    });
  }
  
  return result;
};
