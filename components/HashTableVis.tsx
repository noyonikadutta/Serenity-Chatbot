import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, User, Heart, Mic } from 'lucide-react';

interface HashTableVisProps {
    data: any;
}

const HashTableVis: React.FC<HashTableVisProps> = ({ data }) => {
    if (!data) return null;

    const { name, age, preferences, important_facts } = data.profile || data;

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, x: -20 },
        show: { opacity: 1, x: 0 }
    };

    return (
        <div className="w-full bg-slate-900/50 backdrop-blur-md rounded-2xl border border-white/10 p-6 shadow-xl overflow-hidden relative">
            <div className="flex items-center gap-3 mb-6 border-b border-white/5 pb-3">
                <div className="p-2 bg-emerald-500/20 rounded-lg">
                    <Database className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-slate-100">User Profile</h3>
                    <p className="text-xs text-slate-400 font-mono">Hash Table (Key-Value Store)</p>
                </div>
            </div>

            <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="space-y-3 font-mono text-sm"
            >
                <KeyValueRow label="Name" value={name || 'Unknown'} icon={<User size={14} />} />
                <KeyValueRow label="Age" value={age || 'Unknown'} icon={<User size={14} />} />

                <div className="mt-4">
                    <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider font-semibold">Preferences (Array)</p>
                    <div className="flex flex-wrap gap-2">
                        <AnimatePresence>
                            {preferences?.map((pref: string, i: number) => (
                                <motion.span
                                    key={pref}
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    exit={{ scale: 0 }}
                                    className="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-3 py-1 rounded-full text-xs"
                                >
                                    {pref}
                                </motion.span>
                            ))}
                            {(!preferences || preferences.length === 0) && <span className="text-slate-600 text-xs italic">No preferences learned yet.</span>}
                        </AnimatePresence>
                    </div>
                </div>

            </motion.div>
        </div>
    );
};

const KeyValueRow = ({ label, value, icon }: { label: string, value: string, icon: any }) => (
    <motion.div
        layout
        className="flex items-center justify-between p-3 bg-slate-800/40 rounded-xl border border-white/5 hover:border-emerald-500/30 transition-colors group"
    >
        <div className="flex items-center gap-3 text-slate-400">
            {icon}
            <span>{label}</span>
        </div>
        <span className="text-emerald-400 font-medium group-hover:text-emerald-300">{value}</span>
    </motion.div>
);

export default HashTableVis;
