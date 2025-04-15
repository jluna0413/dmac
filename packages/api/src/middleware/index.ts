/**
 * API Middleware
 */
import { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

/**
 * Adds logging middleware to an Axios instance
 * @param client The Axios instance
 * @returns The Axios instance with logging middleware
 */
export function addLoggingMiddleware(client: AxiosInstance): AxiosInstance {
  client.interceptors.request.use(
    (config) => {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('[API] Request Error:', error);
      return Promise.reject(error);
    }
  );
  
  client.interceptors.response.use(
    (response) => {
      console.log(`[API] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
      return response;
    },
    (error) => {
      if (error.response) {
        console.error(`[API] ${error.response.status} ${error.config.method?.toUpperCase()} ${error.config.url}`);
      } else {
        console.error('[API] Response Error:', error);
      }
      return Promise.reject(error);
    }
  );
  
  return client;
}

/**
 * Adds authentication middleware to an Axios instance
 * @param client The Axios instance
 * @param getToken A function that returns the authentication token
 * @returns The Axios instance with authentication middleware
 */
export function addAuthMiddleware(
  client: AxiosInstance,
  getToken: () => string | null
): AxiosInstance {
  client.interceptors.request.use(
    (config) => {
      const token = getToken();
      if (token) {
        config.headers = config.headers || {};
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
  
  return client;
}

/**
 * Adds retry middleware to an Axios instance
 * @param client The Axios instance
 * @param maxRetries The maximum number of retries
 * @param retryDelay The delay between retries in milliseconds
 * @returns The Axios instance with retry middleware
 */
export function addRetryMiddleware(
  client: AxiosInstance,
  maxRetries = 3,
  retryDelay = 1000
): AxiosInstance {
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const config = error.config as AxiosRequestConfig & { _retryCount?: number };
      
      if (!config) {
        return Promise.reject(error);
      }
      
      config._retryCount = config._retryCount || 0;
      
      if (config._retryCount >= maxRetries) {
        return Promise.reject(error);
      }
      
      config._retryCount += 1;
      
      return new Promise((resolve) => {
        setTimeout(() => resolve(client(config)), retryDelay);
      });
    }
  );
  
  return client;
}
