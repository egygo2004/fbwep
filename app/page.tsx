import LogTable from "@/components/LogTable";
import StatsGrid from "@/components/StatsGrid";
import CommandCenter from "@/components/CommandCenter";
import { Activity, Zap } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#09090b] text-white p-6 md:p-10 font-[family-name:var(--font-geist-sans)] selection:bg-violet-500/30">

      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 via-purple-400 to-fuchsia-400 bg-clip-text text-transparent flex items-center gap-3">
            <Zap className="text-violet-400" size={28} />
            OTP Control Center
          </h1>
          <p className="text-zinc-500 mt-1">Real-time automation monitoring & control</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            System Online
          </div>
        </div>
      </header>

      {/* Remote Control */}
      <CommandCenter />

      {/* Stats Grid */}
      <StatsGrid />

      {/* Main Content */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-zinc-100">
            <Activity className="text-violet-500" />
            Live Activity Feed
          </h2>
        </div>

        <LogTable />
      </div>

    </main>
  );
}
