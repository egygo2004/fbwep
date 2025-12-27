"use client";

import { useEffect, useState } from 'react';
import { client, databases, APPWRITE_CONFIG } from '@/lib/appwrite';
import { Query } from 'appwrite';
import StatusBadge from './StatusBadge';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, RefreshCw, Smartphone, Globe, Activity } from 'lucide-react';

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

        // Real-time subscription
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
                        <th className="p-4 font-medium text-center">Open Page</th>
                        <th className="p-4 font-medium text-center">Input Phone</th>
                        <th className="p-4 font-medium text-center">Search</th>
                        <th className="p-4 font-medium text-center">Result</th>
                        <th className="p-4 font-medium text-center">SMS</th>
                        <th className="p-4 font-medium text-center">Verify</th>
                        <th className="p-4 font-medium text-center">Status</th>
                        <th className="p-4 font-medium text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    <AnimatePresence initial={false}>
                        {logs.map((log) => (
                            <motion.tr
                                key={log.$id}
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className="group hover:bg-white/5 transition-colors"
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
                                <td className="p-4 text-center"><StatusBadge status={log.step_1} /></td>
                                <td className="p-4 text-center"><StatusBadge status={log.step_2} /></td>
                                <td className="p-4 text-center"><StatusBadge status={log.step_3} /></td>
                                <td className="p-4 text-center"><StatusBadge status={log.step_4} /></td>
                                <td className="p-4 text-center"><StatusBadge status={log.step_5} /></td>
                                <td className="p-4 text-center"><StatusBadge status={log.step_6} pulse={log.status === 'RUNNING'} /></td>
                                <td className="p-4 text-center">
                                    <StatusBadge status={log.status} />
                                </td>
                                <td className="p-4 text-right">
                                    {log.otp_url && (
                                        <a
                                            href={log.otp_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 text-xs font-bold text-blue-400 hover:text-blue-300 bg-blue-500/10 px-3 py-1.5 rounded-lg border border-blue-500/20 hover:bg-blue-500/20 transition-all"
                                        >
                                            OTP LINK <ExternalLink size={12} />
                                        </a>
                                    )}
                                </td>
                            </motion.tr>
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
