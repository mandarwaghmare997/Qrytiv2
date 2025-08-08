/**
 * Optimized Loading Spinner Component
 * Lightweight loading indicator for serverless applications
 */

import React from 'react';
import { cn } from '../lib/utils';

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'primary', 
  className,
  text,
  fullScreen = false 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colorClasses = {
    primary: 'border-blue-600',
    secondary: 'border-gray-600',
    white: 'border-white',
    success: 'border-green-600',
    warning: 'border-yellow-600',
    error: 'border-red-600'
  };

  const spinner = (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-t-transparent',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      role="status"
      aria-label="Loading"
    />
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="flex flex-col items-center gap-3">
          {spinner}
          {text && (
            <p className="text-sm text-gray-600 animate-pulse">{text}</p>
          )}
        </div>
      </div>
    );
  }

  if (text) {
    return (
      <div className="flex items-center gap-2">
        {spinner}
        <span className="text-sm text-gray-600">{text}</span>
      </div>
    );
  }

  return spinner;
};

// Skeleton loading component for better UX
export const SkeletonLoader = ({ className, children }) => (
  <div className={cn('animate-pulse', className)}>
    {children || <div className="bg-gray-200 rounded h-4 w-full" />}
  </div>
);

// Card skeleton
export const CardSkeleton = () => (
  <div className="border rounded-lg p-6 space-y-4">
    <SkeletonLoader className="h-6 w-3/4 bg-gray-200 rounded" />
    <SkeletonLoader className="h-4 w-full bg-gray-200 rounded" />
    <SkeletonLoader className="h-4 w-2/3 bg-gray-200 rounded" />
  </div>
);

// Table skeleton
export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <div className="space-y-3">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex gap-4">
        {Array.from({ length: columns }).map((_, j) => (
          <SkeletonLoader 
            key={j} 
            className="h-4 flex-1 bg-gray-200 rounded" 
          />
        ))}
      </div>
    ))}
  </div>
);

export default LoadingSpinner;

