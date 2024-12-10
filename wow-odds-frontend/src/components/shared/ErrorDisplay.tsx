// src/components/shared/ErrorDisplay.tsx
import React from 'react';

interface ErrorDisplayProps {
  message: string;
}

export const ErrorDisplay = ({ message }: ErrorDisplayProps) => (
  <div className="bg-red-900/50 border border-red-900 text-red-300 p-4 rounded">
    <p>{message}</p>
  </div>
);

export default ErrorDisplay;
