// Re-export all types for easy importing
export * from './item';
export * from './spell';
export * from './npc';
export * from './zone';
export * from './tradeskill';
export * from './quest';
export * from './faction';
export * from './user';

// Common types used across the application
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface SearchParams {
  q?: string;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ErrorResponse {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// User-related types
export interface User {
  id: string;
  username: string;
  avatar?: string;
  email?: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  items_per_page: number;
  default_search_type: 'items' | 'spells' | 'npcs' | 'zones';
  show_tooltips: boolean;
  auto_save_searches: boolean;
}

// Navigation types
export interface NavigationItem {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  children?: NavigationItem[];
  external?: boolean;
}

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'radio' | 'textarea';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
} 