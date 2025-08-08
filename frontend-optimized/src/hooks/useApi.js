/**
 * Optimized API Hook for React Components
 * Provides loading states, error handling, and caching for API calls
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import apiService from '../services/api.js';
import config from '../config.js';

// Custom hook for API calls with loading and error states
export const useApi = (apiCall, dependencies = [], options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const mountedRef = useRef(true);

  const {
    immediate = true,
    onSuccess,
    onError,
    transform,
    skipCache = false
  } = options;

  const execute = useCallback(async (...args) => {
    if (!mountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const result = await apiCall(...args);
      
      if (!mountedRef.current) return;

      const transformedData = transform ? transform(result) : result;
      setData(transformedData);
      
      if (onSuccess) {
        onSuccess(transformedData);
      }

      return transformedData;
    } catch (err) {
      if (!mountedRef.current) return;

      setError(err);
      
      if (onError) {
        onError(err);
      } else {
        console.error('API Error:', err);
      }
      
      throw err;
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [apiCall, transform, onSuccess, onError]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, dependencies);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    refetch: execute
  };
};

// Hook for authentication state
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = apiService.getAuthToken();
        if (!token) {
          setLoading(false);
          return;
        }

        const isValid = await apiService.verifyToken();
        if (isValid) {
          const profileData = localStorage.getItem(config.storage.keys.userProfile);
          if (profileData) {
            const userData = JSON.parse(profileData);
            setUser(userData);
            setIsAuthenticated(true);
          }
        } else {
          apiService.logout();
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        apiService.logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await apiService.login(email, password);
      if (response.success) {
        setUser(response.data.user);
        setIsAuthenticated(true);
        return response;
      }
      throw new Error(response.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const response = await apiService.register(userData);
      if (response.success) {
        setUser(response.data.user);
        setIsAuthenticated(true);
        return response;
      }
      throw new Error(response.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    apiService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (profileData) => {
    const response = await apiService.updateUserProfile(profileData);
    if (response.success) {
      setUser(response.data);
    }
    return response;
  };

  return {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile
  };
};

// Hook for clients data
export const useClients = (options = {}) => {
  return useApi(
    () => apiService.getClients(),
    [],
    {
      transform: (response) => response.data || [],
      ...options
    }
  );
};

// Hook for models data
export const useModels = (filters = {}, options = {}) => {
  return useApi(
    () => apiService.getModels(filters),
    [JSON.stringify(filters)],
    {
      transform: (response) => response.data || {},
      ...options
    }
  );
};

// Hook for reports data
export const useReports = (options = {}) => {
  return useApi(
    () => apiService.getReports(),
    [],
    {
      transform: (response) => response.data || [],
      ...options
    }
  );
};

// Hook for form submissions
export const useSubmit = (submitFunction, options = {}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const { onSuccess, onError, resetOnSubmit = true } = options;

  const submit = useCallback(async (data) => {
    if (resetOnSubmit) {
      setError(null);
      setSuccess(false);
    }
    
    setLoading(true);

    try {
      const result = await submitFunction(data);
      setSuccess(true);
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      return result;
    } catch (err) {
      setError(err);
      
      if (onError) {
        onError(err);
      }
      
      throw err;
    } finally {
      setLoading(false);
    }
  }, [submitFunction, onSuccess, onError, resetOnSubmit]);

  const reset = useCallback(() => {
    setError(null);
    setSuccess(false);
    setLoading(false);
  }, []);

  return {
    submit,
    loading,
    error,
    success,
    reset
  };
};

// Hook for pagination
export const usePagination = (data = [], pageSize = config.performance.pagination.defaultPageSize) => {
  const [currentPage, setCurrentPage] = useState(1);
  
  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentData = data.slice(startIndex, endIndex);

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const nextPage = () => {
    goToPage(currentPage + 1);
  };

  const prevPage = () => {
    goToPage(currentPage - 1);
  };

  const reset = () => {
    setCurrentPage(1);
  };

  return {
    currentPage,
    totalPages,
    currentData,
    goToPage,
    nextPage,
    prevPage,
    reset,
    hasNext: currentPage < totalPages,
    hasPrev: currentPage > 1
  };
};

// Hook for debounced values (useful for search)
export const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Hook for local storage
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
};

