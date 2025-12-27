import { LucideIcon } from 'lucide-react';

interface StatCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    trend?: string;
    trendUp?: boolean;
    color?: string;
}

export default function StatCard({ title, value, icon: Icon, trend, trendUp, color = "blue" }: StatCardProps) {
    const colorStyles = {
        blue: "from-blue-500/20 to-cyan-500/5 border-blue-500/20 text-blue-400",
        green: "from-emerald-500/20 to-teal-500/5 border-emerald-500/20 text-emerald-400",
        red: "from-red-500/20 to-orange-500/5 border-red-500/20 text-red-400",
        purple: "from-purple-500/20 to-pink-500/5 border-purple-500/20 text-purple-400",
    };

    const activeColor = colorStyles[color as keyof typeof colorStyles] || colorStyles.blue;

    return (
        <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${activeColor} border p-6 shadow-lg backdrop-blur-xl`}>
            <div className="absolute -right-4 -top-4 opacity-10">
                <Icon size={100} />
            </div>

            <div className="relative z-10 flex flex-col gap-1">
                <div className="flex items-center gap-2 mb-2">
                    <div className="p-2 rounded-lg bg-black/20 w-fit">
                        <Icon size={20} />
                    </div>
                    <span className="text-sm font-medium opacity-80 uppercase tracking-wider">{title}</span>
                </div>

                <h3 className="text-3xl font-bold tracking-tight text-white/90">{value}</h3>

                {trend && (
                    <div className={`text-xs font-medium mt-1 ${trendUp ? 'text-green-400' : 'text-red-400'}`}>
                        {trend}
                    </div>
                )}
            </div>
        </div>
    );
}
