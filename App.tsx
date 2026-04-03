import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Message } from './types';
import MessageBubble from './components/MessageBubble';
import TypingIndicator from './components/TypingIndicator';
import { sendMessageToBackend, sendMessageToRag, resetSession } from './services/chatService';
import HashTableVis from './components/HashTableVis';
import GraphVis from './components/GraphVis';
import CRSDashboard from './components/CRSDashboard';
import { Brain, Sparkles, X, ChevronRight, Activity, FileText, BarChart3, RefreshCw } from 'lucide-react';

type Tab = 'memory' | 'rag' | 'crs';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('memory');

  // --- Memory Bot State ---
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: "Welcome back. I'm Serenity. I'm listening.", timestamp: new Date() },
  ]);
  const [debugData, setDebugData] = useState<any>(null);
  const [showBrain, setShowBrain] = useState(true);

  // --- RAG Bot State ---
  const [ragMessages, setRagMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: "I am the RAG Baseline. I have no memory of our past.", timestamp: new Date() },
  ]);

  // --- Shared State ---
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);
  const ragScrollRef = useRef<HTMLDivElement>(null);

  // Scroll logic
  useEffect(() => {
    if (activeTab === 'memory' && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    } else if (activeTab === 'rag' && ragScrollRef.current) {
      ragScrollRef.current.scrollTop = ragScrollRef.current.scrollHeight;
    }
  }, [messages, ragMessages, isTyping, activeTab]);

  const handleReset = useCallback(async () => {
    if (confirm("Are you sure you want to clear all memory and start a new session?")) {
      const success = await resetSession();
      if (success) {
        setMessages([{ id: Date.now().toString(), role: 'assistant', content: "Memory cleared. Hello, who are you?", timestamp: new Date() }]);
        setDebugData(null);
        setRagMessages([{ id: Date.now().toString(), role: 'assistant', content: "I am ready.", timestamp: new Date() }]);
      }
    }
  }, []);

  const handleSend = useCallback(async () => {
    if (!inputValue.trim() || isTyping) return;

    const userText = inputValue.trim();
    setInputValue('');
    setIsTyping(true);

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userText,
      timestamp: new Date(),
    };

    if (activeTab === 'memory') {
      setMessages(prev => [...prev, userMsg]);

      try {
        const response = await sendMessageToBackend(userMsg.content, messages);

        const assistMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.reply,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistMsg]);

        if (response.debug_data) {
          setDebugData(response.debug_data);
        }
      } catch (e) {
        console.error(e);
      }

    } else if (activeTab === 'rag') {
      setRagMessages(prev => [...prev, userMsg]);

      try {
        const response = await sendMessageToRag(userMsg.content);
        const assistMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.reply,
          timestamp: new Date(),
        };
        setRagMessages(prev => [...prev, assistMsg]);
      } catch (e) { console.error(e); }
    }

    setIsTyping(false);
  }, [inputValue, isTyping, messages, activeTab]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans overflow-hidden flex flex-col relative selection:bg-emerald-500/30">

      {/* Background Ambience */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-emerald-900/10 blur-[150px] rounded-full animate-pulse-slow"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-indigo-900/10 blur-[150px] rounded-full animate-pulse-slow delay-1000"></div>
        <div className="absolute top-[40%] left-[40%] w-[30%] h-[30%] bg-violet-900/5 blur-[120px] rounded-full mix-blend-screen"></div>
      </div>

      {/* Header / Nav */}
      <nav className="relative z-20 flex items-center justify-between px-8 py-4 bg-slate-900/30 border-b border-white/5 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-light tracking-tight text-white/90">Serenity</h1>
        </div>

        <div className="flex bg-slate-950/50 p-1 rounded-xl border border-white/5">
          <button
            onClick={() => setActiveTab('memory')}
            className={`px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2 ${activeTab === 'memory' ? 'bg-emerald-500/20 text-emerald-400 font-medium' : 'text-slate-500 hover:text-slate-300'}`}
          >
            <Brain size={16} /> Memory
          </button>
          <button
            onClick={() => setActiveTab('rag')}
            className={`px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2 ${activeTab === 'rag' ? 'bg-indigo-500/20 text-indigo-400 font-medium' : 'text-slate-500 hover:text-slate-300'}`}
          >
            <FileText size={16} /> RAG Baseline
          </button>
          <button
            onClick={() => setActiveTab('crs')}
            className={`px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2 ${activeTab === 'crs' ? 'bg-amber-500/20 text-amber-400 font-medium' : 'text-slate-500 hover:text-slate-300'}`}
          >
            <BarChart3 size={16} /> CRS Compare
          </button>
        </div>

        <div className="w-10">
          {/* New Session Button (Global) */}
          <button
            onClick={handleReset}
            title="New Session (Clear Memory)"
            className="p-2 ml-4 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </nav>

      {/* Main Layout Grid */}
      <main className="relative z-10 flex-1 flex p-4 md:p-6 gap-6 overflow-hidden">

        {/* --- CRS COMPARISON VIEW --- */}
        {activeTab === 'crs' && (
          <div className="w-full h-full overflow-y-auto custom-scrollbar">
            <CRSDashboard />
          </div>
        )}

        {/* --- CHAT VIEW (Memory or RAG) --- */}
        {activeTab !== 'crs' && (
          <>
            {/* Left Panel: Chat Interface */}
            <motion.div
              layout
              className={`flex flex-col h-full transition-all duration-500 ease-in-out ${showBrain && activeTab === 'memory' ? 'w-full md:w-[60%]' : 'w-full max-w-4xl mx-auto'}`}
            >
              <div className={`flex-1 backdrop-blur-2xl border rounded-[2rem] shadow-2xl flex flex-col overflow-hidden relative ${activeTab === 'memory' ? 'bg-slate-900/40 border-emerald-500/20' : 'bg-slate-900/60 border-indigo-500/20'}`}>

                {/* Chat Header */}
                <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center">
                  <div>
                    <h2 className="text-lg font-light text-white/90">
                      {activeTab === 'memory' ? 'Memory-Centric Interface' : 'Retrieval-Augmented Baseline'}
                    </h2>
                    <p className="text-xs text-slate-500 uppercase tracking-widest">
                      {activeTab === 'memory' ? 'Long-term Personalization Active' : 'Stateless Document Search'}
                    </p>
                  </div>
                  {activeTab === 'memory' && !showBrain && (
                    <button
                      onClick={() => setShowBrain(true)}
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-emerald-400 text-xs flex items-center gap-2"
                    >
                      <Brain size={14} /> View Memory
                    </button>
                  )}
                </div>

                {/* Messages */}
                <div ref={activeTab === 'memory' ? scrollRef : ragScrollRef} className="flex-1 overflow-y-auto px-6 py-8 space-y-6 scroll-smooth custom-scrollbar">
                  {(activeTab === 'memory' ? messages : ragMessages).map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                  ))}
                  {isTyping && <TypingIndicator />}
                </div>

                {/* Input Area */}
                <div className="p-6 bg-slate-950/30 border-t border-white/5">
                  <div className="relative group">
                    <textarea
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder={activeTab === 'memory' ? "Share your thoughts with Serenity..." : "Query the RAG knowledge base..."}
                      className={`w-full bg-slate-900/50 border focus:ring-1 rounded-2xl py-4 pl-6 pr-16 text-slate-200 placeholder-slate-600 resize-none outline-none transition-all shadow-inner h-16 min-h-[64px] max-h-32 ${activeTab === 'memory' ? 'border-white/10 focus:border-emerald-500/50 focus:ring-emerald-500/20' : 'border-white/10 focus:border-indigo-500/50 focus:ring-indigo-500/20'}`}
                    />
                    <button
                      onClick={handleSend}
                      disabled={!inputValue.trim() || isTyping}
                      className={`absolute right-2 top-2 bottom-2 w-12 rounded-xl flex items-center justify-center transition-all duration-300 ${!inputValue.trim() || isTyping
                        ? 'text-slate-600 bg-transparent'
                        : activeTab === 'memory'
                          ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/20 hover:scale-105 active:scale-95'
                          : 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20 hover:scale-105 active:scale-95'
                        }`}
                    >
                      <ChevronRight size={24} />
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Right Panel: Brain Internals (Only for Memory Bot) */}
            <AnimatePresence mode="wait">
              {showBrain && activeTab === 'memory' && (
                <motion.div
                  initial={{ opacity: 0, x: 50, scale: 0.95 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  exit={{ opacity: 0, x: 20, scale: 0.95, transition: { duration: 0.2 } }}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  className="hidden md:flex flex-col w-[40%] h-full gap-6"
                >
                  <div className="flex items-center justify-between px-2">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-500/20 rounded-lg">
                        <Activity className="text-emerald-400 w-5 h-5" />
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-white">Live Memory</h2>
                        <p className="text-xs text-slate-400">Real-time Backend State</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowBrain(false)}
                      className="p-2 hover:bg-white/10 rounded-full text-slate-500 hover:text-white transition-colors"
                    >
                      <X size={20} />
                    </button>
                  </div>

                  <div className="flex-1 overflow-y-auto pr-2 pb-4 space-y-6 custom-scrollbar">
                    {/* Emotion Graph */}
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }}>
                      <GraphVis data={debugData ? debugData.emotion_graph : null} />
                    </motion.div>

                    {/* Hash Table (User Profile) */}
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }}>
                      <HashTableVis data={debugData ? debugData.user_profile : null} />
                    </motion.div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </>
        )}

      </main>

      {/* Global Styles for Scrollbar */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(255, 255, 255, 0.1);
          border-radius: 20px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background-color: rgba(255, 255, 255, 0.2);
        }
        .animate-pulse-slow {
            animation: pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
    </div>
  );
};

export default App;
