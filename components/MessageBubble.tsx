
import React from 'react';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex w-full mb-8 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[85%] md:max-w-[75%] px-6 py-5 rounded-[1.5rem] shadow-lg text-[15px] leading-relaxed transition-all duration-500 border ${
          isUser
            ? 'bg-[#1e2e25] text-emerald-50 rounded-tr-none border-emerald-900/30 shadow-emerald-950/10'
            : 'bg-[#131b2e] text-slate-200 rounded-tl-none border-slate-800 shadow-black/20'
        }`}
      >
        <p className="whitespace-pre-wrap font-light tracking-wide">{message.content}</p>
        <div
          className={`text-[9px] mt-3 font-semibold opacity-30 uppercase tracking-[0.15em] ${
            isUser ? 'text-right' : 'text-left'
          }`}
        >
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
