"use client";

import { useState } from 'react';
import { databases, APPWRITE_CONFIG } from '@/lib/appwrite';
import { ID } from 'appwrite';
import { Send, Loader2, Upload, StopCircle, Rocket } from 'lucide-react';

export default function CommandCenter() {
    const [phones, setPhones] = useState('');
    const [loading, setLoading] = useState(false);
    const [stopping, setStopping] = useState(false);
    const [status, setStatus] = useState<string | null>(null);
    const [progress, setProgress] = useState({ sent: 0, total: 0 });

    const handleSend = async () => {
        if (!phones.trim()) return;
        setLoading(true);
        setStatus(null);

        const numberList = phones
            .split(/[\n,\s]+/)
            .map(n => n.trim())
            .filter(n => n.length > 5);

        if (numberList.length === 0) {
            setStatus("❌ No valid numbers found");
            setLoading(false);
            return;
        }

        setProgress({ sent: 0, total: numberList.length });

        try {
            const CMD_COLLECTION_ID = APPWRITE_CONFIG.CMD_COLLECTION_ID || 'command_queue';
            let successCount = 0;

            const batchSize = 10;
            for (let i = 0; i < numberList.length; i += batchSize) {
                const batch = numberList.slice(i, i + batchSize);

                await Promise.all(
                    batch.map(phone =>
                        databases.createDocument(
                            APPWRITE_CONFIG.DATABASE_ID,
                            CMD_COLLECTION_ID,
                            ID.unique(),
                            {
                                type: "TEST_NUMBER",
                                payload: phone,
                                status: "PENDING"
                            }
                        ).then(() => successCount++)
                            .catch(err => console.error(`Failed: ${phone}`, err))
                    )
                );

                setProgress({ sent: Math.min(i + batchSize, numberList.length), total: numberList.length });
            }

            setStatus(`✅ Sent ${successCount}/${numberList.length} numbers to queue!`);
            setPhones('');
        } catch (error) {
            console.error(error);
            setStatus("❌ Failed to send commands.");
        } finally {
            setLoading(false);
            setTimeout(() => setStatus(null), 10000);
        }
    };

    const handleStop = async () => {
        if (!confirm("⚠️ Are you sure you want to STOP all current operations?")) return;
        setStopping(true);
        setStatus("🛑 Sending stop signal...");

        try {
            const CMD_COLLECTION_ID = APPWRITE_CONFIG.CMD_COLLECTION_ID || 'command_queue';

            await databases.createDocument(
                APPWRITE_CONFIG.DATABASE_ID,
                CMD_COLLECTION_ID,
                ID.unique(),
                {
                    type: "STOP_WORKER",
                    payload: "USER_REQUEST",
                    status: "PENDING"
                }
            );

            setStatus("🛑 Stop command sent! Worker will halt after current task.");
        } catch (error) {
            console.error(error);
            setStatus("❌ Failed to send stop command.");
        } finally {
            setStopping(false);
            setTimeout(() => setStatus(null), 8000);
        }
    };

    const detectedCount = phones.split(/[\n,\s]+/).filter(n => n.trim().length > 5).length;

    return (
        <div className="mb-8 p-6 rounded-2xl bg-zinc-900/80 border border-zinc-800 backdrop-blur-md">
            <h2 className="text-xl font-bold mb-5 flex items-center gap-2 text-zinc-100">
                <Rocket size={22} className="text-violet-400" />
                Command Center
            </h2>

            <div className="flex flex-col gap-4">
                <textarea
                    value={phones}
                    onChange={(e) => setPhones(e.target.value)}
                    placeholder="Enter phone numbers (one per line, comma or space separated)&#10;Example:&#10;+201234567890&#10;+201234567891"
                    rows={5}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-violet-500/60 focus:ring-2 focus:ring-violet-500/20 transition-all resize-y font-mono text-sm"
                />
            </div>

            <div className="flex items-center justify-between mt-5">
                <span className="text-zinc-500 text-sm font-medium">
                    {detectedCount} number{detectedCount !== 1 ? 's' : ''} detected
                </span>

                <div className="flex gap-3">
                    {/* Stop All Button */}
                    <button
                        onClick={handleStop}
                        disabled={stopping}
                        className="flex items-center justify-center gap-2 bg-red-500/15 hover:bg-red-500/25 border border-red-500/40 text-red-400 hover:text-red-300 px-5 py-3 rounded-xl font-semibold transition-all disabled:opacity-50"
                        title="Stop All Operations"
                    >
                        {stopping ? (
                            <Loader2 className="animate-spin" size={18} />
                        ) : (
                            <StopCircle size={18} />
                        )}
                        Stop All
                    </button>

                    {/* Send Button */}
                    <button
                        onClick={handleSend}
                        disabled={loading || !phones.trim()}
                        className="flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:bg-zinc-700 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg shadow-violet-500/20 hover:shadow-violet-500/30"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="animate-spin" size={18} />
                                {progress.sent}/{progress.total}
                            </>
                        ) : (
                            <>
                                <Send size={18} />
                                Launch
                            </>
                        )}
                    </button>
                </div>
            </div>

            {status && (
                <div className={`mt-4 p-3 rounded-lg text-sm font-medium ${status.startsWith('❌') ? 'bg-red-500/10 text-red-400 border border-red-500/20' : status.startsWith('🛑') ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}`}>
                    {status}
                </div>
            )}
        </div>
    );
}
