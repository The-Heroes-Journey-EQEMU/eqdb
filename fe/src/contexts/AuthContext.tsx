import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { apiClient } from '../services/apiClient';

// Types
export interface User {
  id: number;
  email: string;
  is_admin: boolean;
  created_at: string;
  last_login: string;
  preferences: Record<string, any>;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  updatePreferences: (preferences: Record<string, any>) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

// Initial state
const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; accessToken: string; refreshToken: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'CLEAR_ERROR' };

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
    
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (accessToken && refreshToken) {
        try {
          // Set the token for API calls
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
          
          // Verify token by getting user profile
          const response = await apiClient.get('/auth/profile');
          const user = response.data;
          
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: { user, accessToken, refreshToken },
          });
        } catch (error) {
          // Token is invalid, try to refresh
          try {
            await refreshAuth();
          } catch (refreshError) {
            // Refresh failed, clear auth state
            dispatch({ type: 'AUTH_LOGOUT' });
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            delete apiClient.defaults.headers.common['Authorization'];
          }
        }
      } else {
        dispatch({ type: 'AUTH_LOGOUT' });
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const response = await apiClient.post('/auth/login', credentials);
      const { access_token, refresh_token, user } = response.data;
      
      // Store tokens
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      
      // Set default auth header
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, accessToken: access_token, refreshToken: refresh_token },
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw new Error(errorMessage);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    delete apiClient.defaults.headers.common['Authorization'];
    dispatch({ type: 'AUTH_LOGOUT' });
  };

  // Refresh auth function
  const refreshAuth = async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await apiClient.post('/auth/refresh', {}, {
        headers: { Authorization: `Bearer ${refreshToken}` }
      });
      
      const { access_token } = response.data;
      
      // Update stored token
      localStorage.setItem('accessToken', access_token);
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get updated user data
      const userResponse = await apiClient.get('/auth/profile');
      const user = userResponse.data;
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, accessToken: access_token, refreshToken },
      });
    } catch (error: any) {
      throw new Error('Token refresh failed');
    }
  };

  // Update preferences function
  const updatePreferences = async (preferences: Record<string, any>) => {
    try {
      const response = await apiClient.put('/auth/preferences', preferences);
      const updatedUser = { ...state.user!, preferences: response.data };
      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to update preferences';
      throw new Error(errorMessage);
    }
  };

  // Change password function
  const changePassword = async (currentPassword: string, newPassword: string) => {
    try {
      await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to change password';
      throw new Error(errorMessage);
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    refreshAuth,
    updatePreferences,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 