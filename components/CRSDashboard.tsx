import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Brain, FileText, TrendingUp, Award } from 'lucide-react';

interface CRSMetrics {
    memory_avg_crs: number;
    rag_avg_crs: number;
    memory_turn_count: number;
    rag_turn_count: number;
}

const CRSDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<CRSMetrics | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchMetrics = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/crs/metrics');
            if (!response.ok) throw new Error('Failed to fetch CRS metrics');
            const data = await response.json();
            setMetrics(data);
            setLoading(false);
        } catch (error) {
            console.error('CRS metrics error:', error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    if (loading && !metrics) {
        return <div className="p-8 text-center text-slate-500">Loading CRS metrics...</div>;
    }

    if (!metrics) {
        return <div className="p-8 text-center text-red-400">Failed to load CRS data.</div>;
    }

    const memoryScore = metrics.memory_avg_crs || 0;
    const ragScore = metrics.rag_avg_crs || 0;
    const winner = memoryScore > ragScore ? 'memory' : ragScore > memoryScore ? 'rag' : 'tie';

    return (
        <div className="p-6 md:p-10 w-full max-w-5xl mx-auto space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h2 className="text-3xl font-light text-white">Context Retention Score (CRS)</h2>
                <p className="text-slate-400">Measuring how well each system remembers user context</p>
            </div>

            {/* Explanation Card */}
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-900/50 border border-white/10 rounded-2xl p-6"
            >
                <div className="flex items-start gap-3">
                    <Activity className="text-cyan-400 mt-1" size={20} />
                    <div>
                        <h3 className="text-lg font-semibold text-white mb-2">What is CRS?</h3>
                        <p className="text-sm text-slate-300 leading-relaxed">
                            CRS measures the percentage of stored context units (name, emotions, preferences, topics)
                            that are correctly referenced in the chatbot's responses. Higher scores indicate better memory retention.
                        </p>
                        <p className="text-xs text-slate-500 mt-2">
                            Formula: CRS = (Retrieved Context Units / Total Stored Units) × 100
                        </p>
                    </div>
                </div>
            </motion.div>

            {/* Comparison Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Memory-Based System */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-slate-900/50 border border-emerald-500/30 rounded-2xl p-6 relative overflow-hidden"
                >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-teal-400"></div>

                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-3 bg-emerald-500/20 rounded-xl text-emerald-400">
                            <Brain size={24} />
                        </div>
                        <div>
                            <h3 className="text-xl font-semibold text-white">Memory-Centric</h3>
                            <p className="text-xs text-emerald-500/80 uppercase tracking-widest">With Context Retention</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {/* CRS Score */}
                        <div className="space-y-2">
                            <div className="flex justify-between items-baseline">
                                <span className="text-sm text-slate-400">Average CRS</span>
                                <span className="text-3xl font-bold text-emerald-400">{memoryScore.toFixed(1)}%</span>
                            </div>
                            <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${memoryScore}%` }}
                                    transition={{ duration: 1, ease: "easeOut" }}
                                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                                />
                            </div>
                        </div>

                        {/* Turn Count */}
                        <div className="flex justify-between items-center pt-2 border-t border-white/5">
                            <span className="text-sm text-slate-500">Conversation Turns</span>
                            <span className="text-xl font-mono text-white">{metrics.memory_turn_count}</span>
                        </div>
                    </div>
                </motion.div>

                {/* RAG-Based System */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-slate-900/50 border border-indigo-500/30 rounded-2xl p-6 relative overflow-hidden"
                >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-violet-400"></div>

                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-3 bg-indigo-500/20 rounded-xl text-indigo-400">
                            <FileText size={24} />
                        </div>
                        <div>
                            <h3 className="text-xl font-semibold text-white">RAG Baseline</h3>
                            <p className="text-xs text-indigo-500/80 uppercase tracking-widest">Stateless Retrieval</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {/* CRS Score */}
                        <div className="space-y-2">
                            <div className="flex justify-between items-baseline">
                                <span className="text-sm text-slate-400">Average CRS</span>
                                <span className="text-3xl font-bold text-indigo-400">{ragScore.toFixed(1)}%</span>
                            </div>
                            <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${ragScore}%` }}
                                    transition={{ duration: 1, ease: "easeOut" }}
                                    className="h-full bg-gradient-to-r from-indigo-500 to-violet-400 rounded-full"
                                />
                            </div>
                        </div>

                        {/* Turn Count */}
                        <div className="flex justify-between items-center pt-2 border-t border-white/5">
                            <span className="text-sm text-slate-500">Conversation Turns</span>
                            <span className="text-xl font-mono text-white">{metrics.rag_turn_count}</span>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Winner Banner */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className={`border rounded-2xl p-8 flex items-center justify-center gap-6 ${winner === 'memory'
                        ? 'bg-gradient-to-r from-emerald-900/40 to-slate-900 border-emerald-500/20'
                        : winner === 'rag'
                            ? 'bg-gradient-to-r from-indigo-900/40 to-slate-900 border-indigo-500/20'
                            : 'bg-slate-900/50 border-white/10'
                    }`}
            >
                <Award size={48} className={
                    winner === 'memory' ? 'text-emerald-400' :
                        winner === 'rag' ? 'text-indigo-400' :
                            'text-slate-400'
                } />
                <div>
                    <h3 className="text-lg text-slate-300">Performance Verdict</h3>
                    <p className="text-2xl font-bold text-white">
                        {winner === 'memory' && 'Memory-Centric System Superior'}
                        {winner === 'rag' && 'RAG System Superior'}
                        {winner === 'tie' && 'No Clear Winner Yet'}
                    </p>
                    <p className="text-sm text-slate-400 mt-1">
                        {winner === 'memory' && 'The memory-centric approach demonstrates significantly higher context retention across conversation turns.'}
                        {winner === 'rag' && 'The RAG approach shows better context retention in this session.'}
                        {winner === 'tie' && 'Both systems are performing similarly. Continue chatting to see differentiation.'}
                    </p>
                </div>
            </motion.div>

            {/* Insight Card */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="bg-slate-900/30 border border-white/5 rounded-xl p-5"
            >
                <div className="flex items-start gap-3">
                    <TrendingUp className="text-cyan-400 mt-0.5" size={18} />
                    <div className="text-sm text-slate-300">
                        <p className="font-semibold mb-1">How to Interpret CRS:</p>
                        <ul className="space-y-1 text-slate-400">
                            <li>• <strong className="text-white">90-100%:</strong> Excellent context retention</li>
                            <li>• <strong className="text-white">70-89%:</strong> Good retention with minor gaps</li>
                            <li>• <strong className="text-white">50-69%:</strong> Moderate retention</li>
                            <li>• <strong className="text-white">Below 50%:</strong> Poor context retention</li>
                        </ul>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default CRSDashboard;
