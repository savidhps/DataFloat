/**
 * Keep-Alive Utility
 * Pings the backend periodically to prevent Render free tier from sleeping
 */

const PING_INTERVAL = 10 * 60 * 1000; // 10 minutes in milliseconds
const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

/**
 * Start the keep-alive mechanism
 * Pings backend health endpoint every 10 minutes
 */
export const startKeepAlive = () => {
  // Only run in production (when deployed)
  if (import.meta.env.DEV) {
    console.log('Keep-alive disabled in development mode');
    return;
  }

  console.log('Starting keep-alive pings...');
  
  // Ping immediately on start
  pingBackend();
  
  // Then ping every 10 minutes
  const intervalId = setInterval(pingBackend, PING_INTERVAL);
  
  // Return cleanup function
  return () => clearInterval(intervalId);
};

/**
 * Ping the backend health endpoint
 */
const pingBackend = async () => {
  try {
    const startTime = Date.now();
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      cache: 'no-cache',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const duration = Date.now() - startTime;
    
    if (response.ok) {
      const data = await response.json();
      console.log(`✅ Backend keep-alive successful (${duration}ms)`, data);
    } else {
      console.warn(`⚠️ Backend keep-alive returned ${response.status}`);
    }
  } catch (error) {
    console.warn('❌ Backend keep-alive failed:', error.message);
  }
};

/**
 * Check if backend is ready (useful for initial load)
 * @returns {Promise<boolean>} True if backend is ready
 */
export const checkBackendHealth = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      cache: 'no-cache',
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.status === 'healthy';
    }
    
    return false;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

/**
 * Wait for backend to be ready (with retries)
 * Useful during cold starts
 * @param {number} maxRetries - Maximum number of retry attempts
 * @param {number} retryDelay - Delay between retries in ms
 * @returns {Promise<boolean>} True if backend becomes ready
 */
export const waitForBackend = async (maxRetries = 12, retryDelay = 5000) => {
  for (let i = 0; i < maxRetries; i++) {
    const isReady = await checkBackendHealth();
    
    if (isReady) {
      console.log(`✅ Backend is ready (attempt ${i + 1}/${maxRetries})`);
      return true;
    }
    
    console.log(`⏳ Waiting for backend... (attempt ${i + 1}/${maxRetries})`);
    
    // Wait before next retry
    if (i < maxRetries - 1) {
      await new Promise(resolve => setTimeout(resolve, retryDelay));
    }
  }
  
  console.error('❌ Backend failed to become ready');
  return false;
};
