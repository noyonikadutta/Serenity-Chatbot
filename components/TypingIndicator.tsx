
import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start mb-8">
      <div className="bg-[#131b2e] border border-slate-800 px-6 py-5 rounded-[1.5rem] rounded-tl-none shadow-lg flex space-x-1.5 items-center">
        <div className="w-1.5 h-1.5 bg-slate-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-1.5 h-1.5 bg-slate-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-1.5 h-1.5 bg-slate-600 rounded-full animate-bounce"></div>
      </div>
    </div>
  );
};

export default TypingIndicator;
