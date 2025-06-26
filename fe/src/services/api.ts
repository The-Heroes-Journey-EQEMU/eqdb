import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { toast } from 'react-hot-toast'

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api/v1'

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
})

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    // Handle different types of errors
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const responseData = error.response.data as any
      const message = responseData?.message || 'An error occurred'

      switch (status) {
        case 401:
          toast.error('Authentication required. Please log in.')
          // Redirect to login if needed
          break
        case 403:
          toast.error('Access denied. You do not have permission for this action.')
          break
        case 404:
          toast.error('Resource not found.')
          break
        case 429:
          toast.error('Too many requests. Please try again later.')
          break
        case 500:
          toast.error('Server error. Please try again later.')
          break
        default:
          toast.error(message)
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.')
    } else {
      // Other error
      toast.error('An unexpected error occurred.')
    }

    return Promise.reject(error)
  }
)

// Generic API response types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// Generic API functions
export const api = {
  get: <T>(url: string, params?: any): Promise<AxiosResponse<T>> => {
    return apiClient.get(url, { params })
  },

  post: <T>(url: string, data?: any): Promise<AxiosResponse<T>> => {
    return apiClient.post(url, data)
  },

  put: <T>(url: string, data?: any): Promise<AxiosResponse<T>> => {
    return apiClient.put(url, data)
  },

  delete: <T>(url: string): Promise<AxiosResponse<T>> => {
    return apiClient.delete(url)
  },

  patch: <T>(url: string, data?: any): Promise<AxiosResponse<T>> => {
    return apiClient.patch(url, data)
  },
}

// Error handling utilities
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return 'An unexpected error occurred'
}

// API status utilities
export const isApiError = (error: any): error is AxiosError => {
  return axios.isAxiosError(error)
}

export const getApiErrorMessage = (error: any): string => {
  if (isApiError(error)) {
    const responseData = error.response?.data as any
    return responseData?.message || error.message
  }
  return 'An unexpected error occurred'
} 