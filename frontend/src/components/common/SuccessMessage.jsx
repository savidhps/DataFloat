import React from 'react';
import { CheckCircle } from 'lucide-react';

const SuccessMessage = ({ message, onClose }) => {
  if (!message) return null;

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-green-800">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-green-600 hover:text-green-800 transition-colors"
        >
          ×
        </button>
      )}
    </div>
  );
};

export default SuccessMessage;
