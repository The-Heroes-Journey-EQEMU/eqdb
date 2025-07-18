import { api } from './apiClient';
import { 
  User, 
  UserPreferences, 
  WeightSet, 
  CreateWeightSetRequest, 
  UpdateWeightSetRequest 
} from '../types/user';

export const userService = {
  // Authentication
  login: async (email: string, password: string) => {
    const response = await api.post<{
      access_token: string;
      refresh_token: string;
      user: User;
    }>('/auth/login', { email, password });
    return response;
  },

  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Ignore logout errors
    }
    // Clear local storage
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  },

  refreshToken: async () => {
    const response = await api.post<{
      access_token: string;
    }>('/auth/refresh');
    return response;
  },

  getCurrentUser: async () => {
    const response = await api.get<User>('/auth/me');
    return response;
  },

  // User management
  updateProfile: async (data: Partial<User>) => {
    const response = await api.put<User>('/auth/profile', data);
    return response;
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response;
  },

  // Weight Sets
  getWeightSets: async () => {
    const response = await api.get<{ weight_sets: WeightSet[] }>('/user/weight-sets');
    return response.weight_sets;
  },

  getWeightSet: async (id: number) => {
    const response = await api.get<WeightSet>(`/user/weight-sets/${id}`);
    return response;
  },

  createWeightSet: async (data: CreateWeightSetRequest) => {
    const response = await api.post<WeightSet>('/user/weight-sets', data);
    return response;
  },

  updateWeightSet: async (id: number, data: UpdateWeightSetRequest) => {
    const response = await api.put<WeightSet>(`/user/weight-sets/${id}`, data);
    return response;
  },

  deleteWeightSet: async (id: number) => {
    const response = await api.delete(`/user/weight-sets/${id}`);
    return response;
  },

  // User preferences
  getPreferences: async (): Promise<UserPreferences> => {
    const user = await userService.getCurrentUser();
    try {
      return JSON.parse(user.preferences);
    } catch {
      return {
        theme: 'auto',
        items_per_page: 25,
        default_search_type: 'items',
        show_tooltips: true,
        auto_save_searches: false
      };
    }
  },

  updatePreferences: async (preferences: Partial<UserPreferences>) => {
    const currentPrefs = await userService.getPreferences();
    const updatedPrefs = { ...currentPrefs, ...preferences };
    const response = await api.put<User>('/auth/profile', {
      preferences: JSON.stringify(updatedPrefs)
    });
    return response;
  }
}; 