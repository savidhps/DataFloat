import React from 'react';
import { Loader2 } from 'lucide-react';

const Loading = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
};

export default Loading;
