// Data layer for the risk dashboard.
// Set NEXT_PUBLIC_RISK_API_URL to your ETL API base URL to use live data;
// otherwise sample data is shown. Adjust ENDPOINTS to match your routes.
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface RiskOverview {
  totalTransactions: number;
  totalVolume: number;
  flaggedTransactions: number;
  avgRiskScore: number;
  highRiskCustomers: number;
  highRiskAccounts: number;
}
export interface RiskyTransaction {
  id: string; customerId: string; accountId: string; amount: number;
  merchant: string; timestamp: string; riskScore: number; level: RiskLevel;
}
export interface RiskyEntity { id: string; name: string; riskScore: number; level: RiskLevel; txCount: number; volume: number; }
export interface DistributionBucket { range: string; count: number; }
export interface LevelCount { level: RiskLevel; count: number; }
export interface TrendPoint { date: string; avgScore: number; flagged: number; }

export const ENDPOINTS = {
  overview: "/risk/overview",
  transactions: "/risk/top-transactions",
  customers: "/risk/top-customers",
  accounts: "/risk/top-accounts",
  distribution: "/risk/distribution",
  levels: "/risk/levels",
  trend: "/risk/trend",
} as const;

const levelOf = (s: number): RiskLevel => (s >= 85 ? "critical" : s >= 65 ? "high" : s >= 40 ? "medium" : "low");

function rng(seed: number) {
  return () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
}

function sample() {
  const r = rng(42);
  const merchants = ["Crypto Exch. Ltd", "Offshore Wire", "Luxury Goods SA", "Casino Royale", "Gift Cards Hub", "Electronics Mart", "Travel Agent X", "P2P Transfer"];
  const names = ["Marta Kovács", "John Reyes", "Aiko Tanaka", "Omar Haddad", "Lena Fischer", "Pavel Novak", "Sara Lindqvist", "Diego Alvarez"];
  const transactions: RiskyTransaction[] = Array.from({ length: 10 }, (_, i) => {
    const score = Math.round(99 - i * 2.4 - r() * 2);
    return {
      id: `TX-${(908231 + i * 137).toString()}`, customerId: `C-${1000 + Math.floor(r() * 900)}`,
      accountId: `AC-${20000 + Math.floor(r() * 9000)}`, amount: Math.round(5000 + r() * 95000),
      merchant: merchants[i % merchants.length] ?? "", timestamp: `2026-10-0${1 + (i % 9)} ${10 + i}:${10 + i * 3}`,
      riskScore: score, level: levelOf(score),
    };
  });
  const entity = (prefix: string, label: (i: number) => string): RiskyEntity[] =>
    Array.from({ length: 8 }, (_, i) => {
      const score = Math.round(96 - i * 4 - r() * 3);
      return { id: `${prefix}-${1000 + i * 71}`, name: label(i) ?? "", riskScore: score, level: levelOf(score), txCount: Math.round(20 + r() * 300), volume: Math.round(40000 + r() * 900000) };
    });
  const counts = [5200, 7400, 8100, 6900, 4800, 3100, 1900, 1100, 620, 280];
  return {
    overview: { totalTransactions: 1_284_553, totalVolume: 412_908_221, flaggedTransactions: 9_842, avgRiskScore: 27.4, highRiskCustomers: 312, highRiskAccounts: 487 } as RiskOverview,
    transactions,
    customers: entity("C", (i) => names[i] ?? ""),
    accounts: entity("AC", (i) => ["Checking", "Savings", "Business", "Brokerage"][i % 4] + " ••" + (4100 + i * 13)),
    distribution: counts.map((count, i) => ({ range: `${i * 10}-${i * 10 + 10}`, count })),
    levels: [
      { level: "low", count: 21500 }, { level: "medium", count: 11200 },
      { level: "high", count: 3900 }, { level: "critical", count: 900 },
    ] as LevelCount[],
    trend: Array.from({ length: 14 }, (_, i) => ({ date: `Oct ${i + 1}`, avgScore: Math.round((24 + Math.sin(i / 2) * 4 + r() * 3) * 10) / 10, flagged: Math.round(500 + r() * 400 + (i > 9 ? 250 : 0)) })),
  };
}

export type DashboardData = ReturnType<typeof sample>;

export async function fetchDashboard(): Promise<DashboardData & { live: boolean }> {
  const base = process.env.NEXT_PUBLIC_RISK_API_URL;
  if (!base) return { ...sample(), live: false };
  const get = async (p: string) => {
    const res = await fetch(base.replace(/\/$/, "") + p);
    if (!res.ok) throw new Error(`${p} → ${res.status}`);
    return res.json();
  };
  const keys = Object.keys(ENDPOINTS) as (keyof typeof ENDPOINTS)[];
  const values = await Promise.all(keys.map((k) => get(ENDPOINTS[k])));
  return { ...(Object.fromEntries(keys.map((k, i) => [k, values[i]])) as DashboardData), live: true };
}
