import { create } from 'zustand';
import { authService } from '../services/api';

export const useAuthStore = create((set) => ({
  user: authService.getCurrentUserSync(),
  isAuthenticated: !!authService.getCurrentUserSync(),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const { user } = await authService.login(email, password);
      set({ user, isAuthenticated: true, isLoading: false });
      return user;
    } catch (error) {
      set({ error: error.response?.data?.detail || error.message, isLoading: false });
      throw error;
    }
  },

  register: async (name, email, password, department, role) => {
    set({ isLoading: true, error: null });
    try {
      const { user } = await authService.register(name, email, password, department, role);
      set({ user, isAuthenticated: true, isLoading: false });
      return user;
    } catch (error) {
      set({ error: error.response?.data?.detail || error.message, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  clearError: () => set({ error: null }),
}));
