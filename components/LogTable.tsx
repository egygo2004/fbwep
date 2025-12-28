"use client";

import { useEffect, useState } from 'react';
import { client, databases, APPWRITE_CONFIG } from '@/lib/appwrite';
import { Query } from 'appwrite';
import StatusBadge from './StatusBadge';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, RefreshCw, Smartphone, Globe, Activity, ChevronDown, ChevronUp, ImageIcon } from 'lucide-react';

interface Log {
    $id: string;
    phone: string;
    ip: string;
    step_1: string;
    step_2: string;
    step_3: string;
    step_4: string;
    step_5: string;
    step_6: string;
    status: string;
    otp_url?: string;
    logs?: string;
    $createdAt: string;
}

export default function LogTable() {
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(true);
    const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

    const fetchLogs = async () => {
        try {
            const res = await databases.listDocuments(
                APPWRITE_CONFIG.DATABASE_ID,
                APPWRITE_CONFIG.COLLECTION_ID,
                [Query.orderDesc('$createdAt'), Query.limit(50)]
            );
            setLogs(res.documents as unknown as Log[]);
        } catch (error) {
            console.error("Failed to fetch logs:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();

        const unsubscribe = client.subscribe(
            `databases.${APPWRITE_CONFIG.DATABASE_ID}.collections.${APPWRITE_CONFIG.COLLECTION_ID}.documents`,
            (response) => {
                const payload = response.payload as Log;

                if (response.events.includes('databases.*.collections.*.documents.*.create')) {
                    setLogs((prev) => [payload, ...prev]);
                } else if (response.events.includes('databases.*.collections.*.documents.*.update')) {
                    setLogs((prev) => prev.map((log) => log.$id === payload.$id ? payload : log));
                }
            }
        );

        return () => {
            unsubscribe();
        };
    }, []);

    const toggleExpand = (id: string) => {
        setExpandedLogId(expandedLogId === id ? null : id);
    };

    const parseLogEntry = (entry: string) => {
        // Regex to find [IMAGE](url)
        const imageRegex = /\[IMAGE\]\((.*?)\)/;
        const match = entry.match(imageRegex);

        let text = entry;
        let imageUrl = null;

        if (match) {
            imageUrl = match[1];
            text = entry.replace(match[0], '').trim();
        }

        return { text, imageUrl };
    };

    if (loading) {
        return <div className="p-10 text-center text-gray-500 animate-pulse">Loading logs...</div>;
    }

    return (
        <div className="overflow-x-auto rounded-xl border border-white/5 bg-white/5 backdrop-blur-md shadow-2xl">
            <table className="w-full text-left text-sm text-gray-300">
                <thead className="bg-black/40 text-xs uppercase tracking-wider text-gray-400">
                    <tr>
                        <th className="p-4 font-medium">Time</th>
                        <th className="p-4 font-medium">Phone & IP</th>
                        <th className="p-4 font-medium text-center hidden md:table-cell">Open Page</th>
                        <th className="p-4 font-medium text-center hidden md:table-cell">Input Phone</th>
                        <th className="p-4 font-medium text-center hidden md:table-cell">Search</th>
                        <th className="p-4 font-medium text-center">Status</th>
                        <th className="p-4 font-medium text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    <AnimatePresence initial={false}>
                        {logs.map((log) => (
                            <>
                                <motion.tr
                                    key={log.$id}
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="group hover:bg-white/5 transition-colors cursor-pointer"
                                    onClick={() => toggleExpand(log.$id)}
                                >
                                    <td className="p-4 whitespace-nowrap text-xs text-gray-500">
                                        {new Date(log.$createdAt).toLocaleTimeString()}
                                    </td>
                                    <td className="p-4">
                                        <div className="flex flex-col gap-1">
                                            <div className="flex items-center gap-2 font-mono font-medium text-white">
                                                <Smartphone size={14} className="text-blue-400" />
                                                {log.phone}
                                            </div>
                                            <div className="flex items-center gap-2 text-xs text-gray-500">
                                                <Globe size={12} />
                                                {log.ip}
                                            </div>
                                        </div>
                                    </td>
                                    {/* Consolidated Steps for cleaner mobile view, detailed in expand */}
                                    <td className="p-4 text-center hidden md:table-cell"><StatusBadge status={log.step_1} /></td>
                                    <td className="p-4 text-center hidden md:table-cell"><StatusBadge status={log.step_2} /></td>
                                    <td className="p-4 text-center hidden md:table-cell"><StatusBadge status={log.step_3} /></td>

                                    <td className="p-4 text-center">
                                        <StatusBadge status={log.status} />
                                    </td>
                                    <td className="p-4 text-right flex items-center justify-end gap-2">
                                        {log.otp_url && (
                                            <a
                                                href={log.otp_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="p-2 text-blue-400 bg-blue-500/10 rounded-lg hover:bg-blue-500/20"
                                                onClick={(e) => e.stopPropagation()}
                                            >
                                                <ExternalLink size={16} />
                                            </a>
                                        )}
                                        <button
                                            onClick={(e) => { e.stopPropagation(); toggleExpand(log.$id); }}
                                            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/10"
                                        >
                                            {expandedLogId === log.$id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                        </button>
                                    </td>
                                </motion.tr>

                                {expandedLogId === log.$id && (
                                    <motion.tr
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="bg-black/20"
                                    >
                                        <td colSpan={7} className="p-4 md:p-6">
                                            <div className="space-y-4">
                                                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 flex items-center gap-2">
                                                    <Activity size={14} /> Detailed Execution Log
                                                </h3>
                                                <div className="space-y-3">
                                                    {log.logs?.split('\n').map((entry, index) => {
                                                        const { text, imageUrl } = parseLogEntry(entry);
                                                        return (
                                                            <div key={index} className="flex flex-col gap-2 p-3 rounded-lg bg-white/5 border border-white/5">
                                                                <div className="text-sm font-mono text-gray-300 border-l-2 border-violet-500 pl-3">
                                                                    {text}
                                                                </div>
                                                                {imageUrl && (
                                                                    <div className="mt-2 relative group overflow-hidden rounded-lg border border-white/10 w-full md:w-64">
                                                                        <img
                                                                            src={imageUrl}
                                                                            alt={`Step Snapshot ${index}`}
                                                                            className="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-105"
                                                                        />
                                                                        <div className="absolute top-2 right-2 bg-black/60 px-2 py-1 rounded text-[10px] flex items-center gap-1 backdrop-blur-sm">
                                                                            <ImageIcon size={10} /> SNAPSHOT
                                                                        </div>
                                                                        <a
                                                                            href={imageUrl}
                                                                            target="_blank"
                                                                            rel="noreferrer"
                                                                            className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity"
                                                                        >
                                                                            <ExternalLink className="text-white drop-shadow-lg" />
                                                                        </a>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        );
                                                    })}
                                                    {!log.logs && <div className="text-gray-500 text-sm italic">No detailed logs available.</div>}
                                                </div>
                                            </div>
                                        </td>
                                    </motion.tr>
                                )}
                            </>
                        ))}
                    </AnimatePresence>
                </tbody>
            </table>

            {logs.length === 0 && (
                <div className="p-12 text-center text-gray-500">
                    <div className="inline-flex p-4 rounded-full bg-white/5 mb-4">
                        <Activity size={32} />
                    </div>
                    <p>No activity logs yet. Waiting for bot...</p>
                </div>
            )}
        </div>
    );
}
