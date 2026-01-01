import { defineStore } from 'pinia';
import { ref } from 'vue';
import { authApi } from '../api';

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'));

  const login = async (credentials: any) => {
    try {
      const response = await authApi.login(credentials);
      const newToken = response.data.access_token;
      token.value = newToken;
      localStorage.setItem('access_token', newToken);
      return true;
    } catch (error) {
      console.error('Login failed', error);
      return false;
    }
  };

  const register = async (credentials: any) => {
    try {
      await authApi.register(credentials);
      return true;
    } catch (error) {
      console.error('Registration failed', error);
      return false;
    }
  };

  const logout = () => {
    token.value = null;
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

  const isAuthenticated = () => !!token.value;

  return {
    token,
    login,
    register,
    logout,
    isAuthenticated,
  };
});

