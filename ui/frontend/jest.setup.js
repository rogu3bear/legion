import '@testing-library/jest-dom';

// Mock import.meta for Vite environment variables
Object.defineProperty(global, 'import', {
  value: {
    meta: {
      env: {
        VITE_PORTMAP_API: '5001'
      }
    }
  }
}); 