const API_BASE_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000';

// Helper to construct full URLs for media/static content
export const getFullMediaUrl = (path: string): string => {
  if (!path) return '';
  
  // If already an absolute URL, return as is
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.substring(1) : path;
  
  // Construct full URL with port
  return `${API_BASE_URL}/${cleanPath}`;
};