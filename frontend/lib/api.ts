// API configuration utility
const getApiUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side
    return process.env.API_URL || 'http://localhost:8000'
  }
  
  // Client-side
  if (process.env.NODE_ENV === 'development') {
    // In development, try different localhost ports
    return 'http://localhost:8000'
  }
  
  // Production
  return process.env.NEXT_PUBLIC_API_URL || '/api'
}

export const API_BASE_URL = getApiUrl()

// Enhanced fetch with better error handling and CORS support
export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      ...options.headers,
    },
    mode: 'cors',
    credentials: 'omit', // Don't include credentials for CORS simplicity
    ...options,
  }

  // Remove Content-Type for FormData
  if (options.body instanceof FormData) {
    delete (defaultOptions.headers as any)['Content-Type']
  }

  try {
    console.log(`API Request: ${options.method || 'GET'} ${url}`)
    const response = await fetch(url, defaultOptions)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    }
    
    return await response.text()
  } catch (error) {
    console.error(`API Request failed for ${url}:`, error)
    throw error
  }
}

// Specific API functions
export const api = {
  get: (endpoint: string) => apiRequest(endpoint, { method: 'GET' }),
  post: (endpoint: string, data?: any) => 
    apiRequest(endpoint, { 
      method: 'POST', 
      body: data instanceof FormData ? data : JSON.stringify(data) 
    }),
  delete: (endpoint: string) => apiRequest(endpoint, { method: 'DELETE' }),
}