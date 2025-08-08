import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isDev = mode === 'development'
  const isProduction = mode === 'production'
  
  return {
    plugins: [react()],
    
    // Build optimization
    build: {
      // Target modern browsers for smaller bundles
      target: 'es2020',
      
      // Enable minification
      minify: 'terser',
      
      // Optimize CSS
      cssMinify: true,
      
      // Source maps for production debugging
      sourcemap: isDev,
      
      // Chunk splitting for better caching
      rollupOptions: {
        output: {
          manualChunks: {
            // Vendor chunk for third-party libraries
            vendor: [
              'react',
              'react-dom',
              'react-router-dom'
            ],
            
            // UI components chunk
            ui: [
              '@radix-ui/react-dialog',
              '@radix-ui/react-dropdown-menu',
              '@radix-ui/react-select',
              '@radix-ui/react-tabs',
              'lucide-react'
            ],
            
            // Charts chunk (loaded on demand)
            charts: ['recharts'],
            
            // Forms chunk
            forms: [
              'react-hook-form',
              'zod'
            ]
          },
          
          // Optimize chunk file names
          chunkFileNames: 'assets/[name]-[hash].js',
          entryFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].[ext]'
        }
      },
      
      // Terser options for better compression
      terserOptions: isProduction ? {
        compress: {
          drop_console: true, // Remove console.log in production
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info', 'console.debug']
        },
        mangle: {
          safari10: true
        }
      } : undefined,
      
      // Asset optimization
      assetsInlineLimit: 4096, // Inline assets smaller than 4kb
      
      // Chunk size warnings
      chunkSizeWarningLimit: 1000
    },
    
    // Development server
    server: {
      port: 3000,
      host: true,
      
      // Proxy API calls to backend during development
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false
        }
      }
    },
    
    // Preview server (for testing production build)
    preview: {
      port: 3001,
      host: true
    },
    
    // Path resolution
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
        '@services': fileURLToPath(new URL('./src/services', import.meta.url)),
        '@hooks': fileURLToPath(new URL('./src/hooks', import.meta.url)),
        '@utils': fileURLToPath(new URL('./src/lib', import.meta.url)),
        '@assets': fileURLToPath(new URL('./src/assets', import.meta.url))
      }
    },
    
    // Environment variables
    define: {
      __APP_VERSION__: JSON.stringify('2.0.0'),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      __DEV__: isDev,
      __PROD__: isProduction
    },
    
    // CSS optimization
    css: {
      devSourcemap: isDev,
      
      // PostCSS configuration
      postcss: {
        plugins: [
          // Tailwind CSS is configured via tailwind.config.js
        ]
      }
    },
    
    // Dependency optimization
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        'react-hook-form',
        'zod',
        'lucide-react'
      ],
      
      // Exclude large dependencies that should be loaded on demand
      exclude: [
        'recharts'
      ]
    },
    
    // Performance optimizations
    esbuild: {
      // Remove console.log in production
      drop: isProduction ? ['console', 'debugger'] : [],
      
      // Target modern browsers
      target: 'es2020'
    }
  }
})

