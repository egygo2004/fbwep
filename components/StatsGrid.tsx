"use client";

import { useEffect, useState } from 'react';
import { databases, APPWRITE_CONFIG } from '@/lib/appwrite';
import { Query } from 'appwrite';
import StatCard from './StatCard';
import { Activity, CheckCircle, Smartphone, XCircle } from 'lucide-react';

export default function StatsGrid() {
    const [stats, setStats] = useState({
        total: 0,
        success: 0,
        failed: 0,
        active: 0,
        successRate: "0%"
    });

    const [loading, setLoading] = useState(true);

    const fetchStats = async () => {
        try {
            // Check if COLLECTION_ID is properly defined in config or use fallback
            const COLLECTION_ID = APPWRITE_CONFIG.COLLECTION_ID || 'otp_logs';
            const CMD_COLLECTION_ID = APPWRITE_CONFIG.CMD_COLLECTION_ID || 'command_queue';
            const DATABASE_ID = APPWRITE_CONFIG.DATABASE_ID;

            // Parallel requests for efficiency
            const [totalRes, successRes, failedRes, activeRes] = await Promise.all([
                // Total Processed (All logs)
                databases.listDocuments(DATABASE_ID, COLLECTION_ID, [
                    Query.limit(1) // We only need "total"
                ]),
                // Success
                databases.listDocuments(DATABASE_ID, COLLECTION_ID, [
                    Query.equal("status", "OTP_SENT"),
                    Query.limit(1)
                ]),
                // Failed (Anything not sent or pending)
                databases.listDocuments(DATABASE_ID, COLLECTION_ID, [
                    Query.equal("status", "FAILED"),
                    Query.limit(1)
                ]),
                // Active Threads (Processing in Command Queue)
                databases.listDocuments(DATABASE_ID, CMD_COLLECTION_ID, [
                    Query.equal("status", "PROCESSING"),
                    Query.limit(1)
                ])
            ]);

            const total = totalRes.total;
            const success = successRes.total;
            const failed = failedRes.total;
            const active = activeRes.total;

            const rate = total > 0 ? ((success / total) * 100).toFixed(1) : "0";

            setStats({
                total,
                success,
                failed,
                active,
                successRate: `${rate}%`
            });
        } catch (error) {
            console.error("Failed to fetch stats:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 5000); // Update every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            <StatCard
                title="Total Processed"
                value={loading ? "..." : stats.total}
                icon={Smartphone}
                color="blue"
            />
            <StatCard
                title="Success Rate"
                value={loading ? "..." : stats.successRate}
                icon={CheckCircle}
                color="green"
                trend={loading ? undefined : `${stats.success} Sent`}
                trendUp={true}
            />
            <StatCard
                title="Failed"
                value={loading ? "..." : stats.failed}
                icon={XCircle}
                color="red"
            />
            <StatCard
                title="Active Threads"
                value={loading ? "..." : stats.active}
                icon={Activity}
                color="purple"
            />
        </div>
    );
}
