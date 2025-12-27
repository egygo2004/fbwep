import clsx from 'clsx';
import { CheckCircle, XCircle, Clock, Search, AlertTriangle, ArrowRight } from 'lucide-react';

type StatusType = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'OK' | 'NOT_FOUND' | 'TRY_ANOTHER_WAY';

interface StatusBadgeProps {
    status: string;
    pulse?: boolean;
}

export default function StatusBadge({ status, pulse = false }: StatusBadgeProps) {
    const cleanStatus = status?.toUpperCase() || 'UNKNOWN';

    let colorClass = 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    let Icon = Clock;

    if (cleanStatus === 'SUCCESS' || cleanStatus === 'OTP_SENT' || cleanStatus === 'FOUND') {
        colorClass = 'bg-green-500/20 text-green-400 border-green-500/30';
        Icon = CheckCircle;
    } else if (cleanStatus === 'FAILED' || cleanStatus.includes('ERROR')) {
        colorClass = 'bg-red-500/20 text-red-400 border-red-500/30';
        Icon = XCircle;
    } else if (cleanStatus === 'RUNNING') {
        colorClass = 'bg-blue-500/20 text-blue-400 border-blue-500/30';
        Icon = Search;
    } else if (cleanStatus === 'OK') {
        colorClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20';
        Icon = CheckCircle;
    } else if (cleanStatus === 'PENDING') {
        colorClass = 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
        Icon = Clock;
    } else if (cleanStatus === 'NOT_FOUND') {
        colorClass = 'bg-orange-500/20 text-orange-400 border-orange-500/30';
        Icon = AlertTriangle;
    }

    return (
        <div className={clsx(
            "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border backdrop-blur-sm transition-all",
            colorClass,
            pulse && "animate-pulse"
        )}>
            <Icon size={12} className={clsx(pulse && "animate-spin")} />
            <span>{status}</span>
        </div>
    );
}
