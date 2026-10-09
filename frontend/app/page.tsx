"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { Activity, AlertTriangle, Banknote, Gauge, ShieldAlert, Users, Wallet } from "lucide-react";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ComposedChart,
} from "recharts";
import { fetchDashboard, type RiskLevel, type RiskyEntity } from "@/lib/risk-api";


const levelVar: Record<RiskLevel, string> = {
  low: "var(--risk-low)", medium: "var(--risk-medium)", high: "var(--risk-high)", critical: "var(--risk-critical)",
};
const levelText: Record<RiskLevel, string> = {
  low: "text-risk-low", medium: "text-risk-medium", high: "text-risk-high", critical: "text-risk-critical",
};
const fmt = (n: number) => new Intl.NumberFormat("en-US").format(n);
const money = (n: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: n > 1e6 ? "compact" : "standard", maximumFractionDigits: n > 1e6 ? 1 : 0 }).format(n);
const tooltipStyle = { background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 6, fontSize: 12, color: "var(--foreground)" };
const axis = { stroke: "var(--muted-foreground)", fontSize: 11, tickLine: false, axisLine: false };

function Panel({ title, children, className = "" }: { title: string; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-lg border bg-card/80 p-4 backdrop-blur ${className}`}>
      <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-muted-foreground">{title}</h2>
      {children}
    </section>
  );
}

function LevelBadge({ level }: { level: RiskLevel }) {
  return (
    <span className={`inline-flex items-center gap-1.5 font-mono text-xs uppercase ${levelText[level]}`}>
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: levelVar[level] }} />
      {level}
    </span>
  );
}

function ScoreBar({ score, level }: { score: number; level: RiskLevel }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-muted">
        <div className="h-full rounded-full" style={{ width: `${score}%`, background: levelVar[level] }} />
      </div>
      <span className="font-mono text-xs tabular-nums">{score}</span>
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({ queryKey: ["risk-dashboard"], queryFn: fetchDashboard });
  const [entityTab, setEntityTab] = useState<"customers" | "accounts">("customers");

  if (isLoading) return <div className="grid min-h-screen place-items-center font-mono text-sm text-muted-foreground">Loading risk data…</div>;
  if (error || !data) return <div className="grid min-h-screen place-items-center font-mono text-sm text-destructive">Failed to load: {String(error)}</div>;

  const o = data.overview;
  const kpis = [
    { label: "Transactions", value: fmt(o.totalTransactions), icon: Activity },
    { label: "Volume", value: money(o.totalVolume), icon: Banknote },
    { label: "Flagged", value: fmt(o.flaggedTransactions), icon: AlertTriangle, hot: true },
    { label: "Avg risk score", value: o.avgRiskScore.toFixed(1), icon: Gauge },
    { label: "High-risk customers", value: fmt(o.highRiskCustomers), icon: Users, hot: true },
    { label: "High-risk accounts", value: fmt(o.highRiskAccounts), icon: Wallet, hot: true },
  ];
  const entities: RiskyEntity[] = data[entityTab];
  const totalLevels = data.levels.reduce((s, l) => s + l.count, 0);

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 md:px-8">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4 border-b pb-4">
        <div className="flex items-center gap-3">
          <ShieldAlert className="h-7 w-7 text-primary" />
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Risk Monitor</h1>
            <p className="text-sm text-muted-foreground">Transaction risk profiling · data warehouse overview</p>
          </div>
        </div>
        <span className={`rounded border px-2 py-1 font-mono text-xs ${data.live ? "text-risk-low" : "text-primary"}`}>
          {data.live ? "● LIVE API" : "● SAMPLE DATA"}
        </span>
      </header>

      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-lg border bg-card/80 p-4">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-xs">{k.label}</span>
              <k.icon className={`h-4 w-4 ${k.hot ? "text-destructive" : ""}`} />
            </div>
            <div className="mt-2 font-mono text-xl font-semibold tabular-nums">{k.value}</div>
          </div>
        ))}
      </div>

      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <Panel title="Risk score distribution" className="lg:col-span-2">
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={data.distribution}>
                <CartesianGrid stroke="var(--border)" vertical={false} />
                <XAxis dataKey="range" {...axis} />
                <YAxis {...axis} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--accent)" }} />
                <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                  {data.distribution.map((_, i) => {
                    const s = i * 10 + 5;
                    const lv: RiskLevel = s >= 85 ? "critical" : s >= 65 ? "high" : s >= 40 ? "medium" : "low";
                    return <Cell key={i} fill={levelVar[lv]} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Risk levels">
          <div className="relative h-48">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={data.levels} dataKey="count" nameKey="level" innerRadius={55} outerRadius={80} paddingAngle={2} stroke="none">
                  {data.levels.map((l) => <Cell key={l.level} fill={levelVar[l.level]} />)}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 grid place-items-center text-center">
              <div><div className="font-mono text-lg font-semibold">{fmt(totalLevels)}</div><div className="text-xs text-muted-foreground">profiled</div></div>
            </div>
          </div>
          <ul className="mt-2 space-y-1">
            {data.levels.map((l) => (
              <li key={l.level} className="flex justify-between text-sm">
                <LevelBadge level={l.level} />
                <span className="font-mono text-xs tabular-nums text-muted-foreground">{fmt(l.count)} · {((l.count / totalLevels) * 100).toFixed(1)}%</span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      <Panel title="Risk trend · avg score & flagged transactions" className="mb-4">
        <div className="h-56">
          <ResponsiveContainer>
            <ComposedChart data={data.trend}>
              <defs>
                <linearGradient id="flag" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--chart-4)" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="var(--chart-4)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="var(--border)" vertical={false} />
              <XAxis dataKey="date" {...axis} />
              <YAxis yAxisId="l" {...axis} />
              <YAxis yAxisId="r" orientation="right" {...axis} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area yAxisId="r" type="monotone" dataKey="flagged" stroke="var(--chart-4)" fill="url(#flag)" />
              <Line yAxisId="l" type="monotone" dataKey="avgScore" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <div className="grid gap-4 lg:grid-cols-5">
        <Panel title="Top risky transactions" className="overflow-x-auto lg:col-span-3">
          <table className="w-full text-sm">
            <thead className="text-left font-mono text-xs text-muted-foreground">
              <tr><th className="pb-2">ID</th><th className="pb-2">Customer</th><th className="pb-2">Merchant</th><th className="pb-2 text-right">Amount</th><th className="pb-2 pl-4">Score</th><th className="pb-2">Level</th></tr>
            </thead>
            <tbody>
              {data.transactions.map((t) => (
                <tr key={t.id} className="border-t hover:bg-accent/40">
                  <td className="py-2 font-mono text-xs">{t.id}</td>
                  <td className="py-2 font-mono text-xs text-muted-foreground">{t.customerId}</td>
                  <td className="py-2">{t.merchant}</td>
                  <td className="py-2 text-right font-mono tabular-nums">{money(t.amount)}</td>
                  <td className="py-2 pl-4"><ScoreBar score={t.riskScore} level={t.level} /></td>
                  <td className="py-2"><LevelBadge level={t.level} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>

        <Panel title="Top risky entities" className="lg:col-span-2">
          <div className="mb-3 flex gap-1 rounded-md bg-muted p-1">
            {(["customers", "accounts"] as const).map((t) => (
              <button key={t} onClick={() => setEntityTab(t)}
                className={`flex-1 rounded px-3 py-1 text-xs capitalize transition-colors ${entityTab === t ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                {t}
              </button>
            ))}
          </div>
          <div className="h-44">
            <ResponsiveContainer>
              <BarChart data={entities} layout="vertical" margin={{ left: 0 }}>
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis type="category" dataKey="id" width={70} {...axis} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--accent)" }} />
                <Bar dataKey="riskScore" radius={[0, 3, 3, 0]}>
                  {entities.map((e) => <Cell key={e.id} fill={levelVar[e.level]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <ul className="mt-2 divide-y">
            {entities.slice(0, 5).map((e) => (
              <li key={e.id} className="flex items-center justify-between py-2 text-sm">
                <div><div>{e.name}</div><div className="font-mono text-xs text-muted-foreground">{e.id} · {e.txCount} tx · {money(e.volume)}</div></div>
                <LevelBadge level={e.level} />
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}
