import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Share2, Activity } from 'lucide-react';

interface GraphVisProps {
    data: any;
}

const GraphVis: React.FC<GraphVisProps> = ({ data }) => {
    const [nodes, setNodes] = useState<any[]>([]);
    const [links, setLinks] = useState<any[]>([]);

    useEffect(() => {
        if (!data) return;

        const adjList = data.adj_list || {};
        const current = data.current_emotion || 'neutral';

        // Simple layout algorithm (circular)
        const emotionKeys = Object.keys(adjList);
        // Add current if not present in keys (startup edge case)
        if (!emotionKeys.includes(current)) emotionKeys.push(current);

        const count = emotionKeys.length;
        const radius = 80;
        const centerX = 150;
        const centerY = 150;

        const newNodes = emotionKeys.map((key, i) => {
            const angle = (i / count) * 2 * Math.PI;
            return {
                id: key,
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle),
                active: key === current
            };
        });

        const newLinks: any[] = [];
        emotionKeys.forEach((source) => {
            const targets = adjList[source] || {};
            Object.keys(targets).forEach((target) => {
                const sourceNode = newNodes.find(n => n.id === source);
                const targetNode = newNodes.find(n => n.id === target);
                if (sourceNode && targetNode) {
                    newLinks.push({
                        source: sourceNode,
                        target: targetNode,
                        weight: targets[target]
                    });
                }
            });
        });

        setNodes(newNodes);
        setLinks(newLinks);

    }, [data]);

    return (
        <div className="w-full bg-slate-900/50 backdrop-blur-md rounded-2xl border border-white/10 p-6 shadow-xl relative overflow-hidden min-h-[300px]">
            <div className="flex items-center gap-3 mb-4 absolute top-6 left-6 z-10">
                <div className="p-2 bg-indigo-500/20 rounded-lg">
                    <Share2 className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-slate-100">Emotion Graph</h3>
                    <p className="text-xs text-slate-400 font-mono">Weighted Directed Graph</p>
                </div>
            </div>

            <svg className="w-full h-full min-h-[250px] mt-8" viewBox="0 0 300 300">
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="28" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" opacity="0.5" />
                    </marker>
                </defs>

                {/* Links */}
                {links.map((link, i) => (
                    <motion.line
                        key={`${link.source.id}-${link.target.id}`}
                        initial={{ pathLength: 0, opacity: 0 }}
                        animate={{ pathLength: 1, opacity: 0.5 }}
                        x1={link.source.x}
                        y1={link.source.y}
                        x2={link.target.x}
                        y2={link.target.y}
                        stroke="#64748b"
                        strokeWidth={Math.min(link.weight, 5)}
                        markerEnd="url(#arrowhead)"
                    />
                ))}

                {/* Nodes */}
                {nodes.map((node) => (
                    <g key={node.id}>
                        <motion.circle
                            cx={node.x}
                            cy={node.y}
                            r={node.active ? 25 : 18}
                            fill={node.active ? '#10b981' : '#1e293b'}
                            stroke={node.active ? '#34d399' : '#475569'}
                            strokeWidth={2}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", stiffness: 200, damping: 15 }}
                        />
                        {node.active && (
                            <motion.circle
                                cx={node.x}
                                cy={node.y}
                                r={35}
                                stroke="#34d399"
                                strokeWidth={1}
                                fill="none"
                                initial={{ scale: 0.8, opacity: 1 }}
                                animate={{ scale: 1.5, opacity: 0 }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            />
                        )}
                        <text
                            x={node.x}
                            y={node.y + 4}
                            textAnchor="middle"
                            fill="white"
                            fontSize="10"
                            fontWeight="bold"
                            pointerEvents="none"
                        >
                            {node.id.substring(0, 4)}
                        </text>
                    </g>
                ))}
            </svg>

            <div className="absolute bottom-4 right-4 text-[10px] text-slate-500 font-mono">
                Active Node: {data?.current_emotion}
            </div>
        </div>
    );
};

export default GraphVis;
