import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check session on mount
  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    try {
      const response = await authAPI.checkSession();
      if (response.authenticated && response.user) {
        setUser(response.user);
        setIsAuthenticated(true);
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (userData) => {
    try {
      const response = await authAPI.signup(userData);
      if (response.success) {
        return { success: true, data: response };
      }
      return { success: false, error: response.error };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed';
      return { success: false, error: errorMessage, field: error.response?.data?.field };
    }
  };

  const signin = async (credentials) => {
    try {
      const response = await authAPI.signin(credentials);
      if (response.success && response.user) {
        setUser(response.user);
        setIsAuthenticated(true);
        return { success: true, data: response };
      }
      return { success: false, error: response.error };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Sign in failed';
      return { success: false, error: errorMessage };
    }
  };

  const signout = async () => {
    try {
      await authAPI.signout();
      setUser(null);
      setIsAuthenticated(false);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Sign out failed' };
    }
  };

  const isAdmin = () => {
    return user?.role === 'super_admin';
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    signup,
    signin,
    signout,
    checkSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
