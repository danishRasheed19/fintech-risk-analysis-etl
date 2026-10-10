"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  Banknote,
  ShieldAlert,
  Users,
  Wallet,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchDashboard } from "@/lib/risk-api";

type Row = Record<string, unknown>;
type RiskLevel = "low" | "medium" | "high" | "critical";
type EntityTab = "customers" | "accounts";

const levelColor: Record<RiskLevel, string> = {
  low: "var(--risk-low)",
  medium: "var(--risk-medium)",
  high: "var(--risk-high)",
  critical: "var(--risk-critical)",
};

const tooltipStyle = {
  background: "var(--popover)",
  border: "1px solid var(--border)",
  borderRadius: 6,
  fontSize: 12,
  color: "var(--foreground)",
};

const axis = {
  stroke: "var(--muted-foreground)",
  fontSize: 11,
  tickLine: false,
  axisLine: false,
} as const;

function numberValue(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }

  return 0;
}

function textValue(value: unknown, fallback = "—"): string {
  return value === null || value === undefined || value === ""
    ? fallback
    : String(value);
}

function get(row: Row, ...keys: string[]): unknown {
  for (const key of keys) {
    if (row[key] !== undefined && row[key] !== null) {
      return row[key];
    }
  }

  return undefined;
}

function asRows(value: unknown): Row[] {
  return Array.isArray(value)
    ? value.filter(
        (item): item is Row =>
          item !== null &&
          typeof item === "object" &&
          !Array.isArray(item),
      )
    : [];
}

function normaliseLevel(value: unknown): RiskLevel {
  const level = String(value ?? "").toLowerCase();

  if (level.includes("critical")) return "critical";
  if (level.includes("high")) return "high";
  if (level.includes("medium") || level.includes("moderate")) {
    return "medium";
  }
  if (level.includes("low")) return "low";

  return "low";
}

const fmt = (value: unknown) =>
  new Intl.NumberFormat("en-US").format(numberValue(value));

const money = (value: unknown) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(numberValue(value));

function Panel({
  title,
  children,
  className = "",
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-lg border bg-card/80 p-4 backdrop-blur ${className}`}
    >
      <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-muted-foreground">
        {title}
      </h2>
      {children}
    </section>
  );
}

function LevelBadge({ level }: { level: RiskLevel }) {
  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-xs uppercase">
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ background: levelColor[level] }}
      />
      <span style={{ color: levelColor[level] }}>{level}</span>
    </span>
  );
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["risk-dashboard"],
    queryFn: fetchDashboard,
  });

  const [entityTab, setEntityTab] = useState<EntityTab>("customers");

  if (isLoading) {
    return (
      <div className="grid min-h-screen place-items-center font-mono text-sm text-muted-foreground">
        Loading risk data…
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="grid min-h-screen place-items-center px-4 text-center font-mono text-sm text-destructive">
        Failed to load risk data:{" "}
        {error instanceof Error
          ? error.message
          : String(error ?? "No data returned")}
      </div>
    );
  }

  const overview = data.overview as unknown as Row;
  const distributionResponse = data.distribution as unknown as Row;
  const analysisResponse = data.analysis as unknown as Row;
  const accountResponse = data.accountRisk as unknown as Row;
  const customerResponse = data.customerRisk as unknown as Row;

  // Transaction risk distribution
  const riskDistribution = asRows(
    get(distributionResponse, "transaction_distribution"),
  ).map((row) => {
    const level = normaliseLevel(
      get(row, "risk_level", "risk_category", "level", "risk"),
    );

    return {
      level,
      label: level.toUpperCase(),
      count: numberValue(get(row, "count", "transaction_count", "total")),
      fill: levelColor[level],
    };
  });

  // Risk by country
  const countryRisk = asRows(
    get(analysisResponse, "risk_by_country"),
  ).map((row) => ({
    label: textValue(
      get(row, "country", "country_name", "country_code"),
    ),
    averageRisk: numberValue(
      get(row, "average_risk_score", "avg_risk_score", "risk_score"),
    ),
    count: numberValue(
      get(row, "transaction_count", "count", "total_transactions"),
    ),
  }));

  // Use the intended array for each API response.
  const customerRows = asRows(
    get(customerResponse, "riskiest_customers"),
  );

  const accountRows = asRows(
    get(accountResponse, "riskiest_accounts", "riskiest_accounts_by_amount"),
  );

  const entities =
    entityTab === "customers" ? customerRows : accountRows;

  // Overview KPIs
  const kpis = [
    {
      label: "Total transactions",
      value: fmt(get(overview, "total_transaction_count")),
      icon: Activity,
    },
    {
      label: "Transaction volume",
      value: money(get(overview, "total_transaction_amount")),
      icon: Banknote,
    },
    {
      label: "Total customers",
      value: fmt(get(overview, "total_customer_count")),
      icon: Users,
    },
    {
      label: "Total accounts",
      value: fmt(get(overview, "total_account_count")),
      icon: Wallet,
    },
    {
      label: "High-risk transactions",
      value: fmt(get(overview, "high_risk_transactions")),
      icon: AlertTriangle,
      hot: true,
    },
    {
      label: "Critical-risk transactions",
      value: fmt(get(overview, "critical_risk_transactions")),
      icon: ShieldAlert,
      hot: true,
    },
    {
      label: "High-risk customers",
      value: fmt(get(overview, "high_risk_customers")),
      icon: Users,
      hot: true,
    },
    {
      label: "High-risk accounts",
      value: fmt(get(overview, "high_risk_accounts")),
      icon: Wallet,
      hot: true,
    },
  ];

  const totalDistributed = riskDistribution.reduce(
    (sum, item) => sum + item.count,
    0,
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 md:px-8">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4 border-b pb-4">
        <div className="flex items-center gap-3">
          <ShieldAlert className="h-7 w-7 text-primary" />
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              Risk Monitor
            </h1>
            <p className="text-sm text-muted-foreground">
              Transaction risk profiling · live analytics API
            </p>
          </div>
        </div>

        <span className="rounded border px-2 py-1 font-mono text-xs text-risk-low">
          ● LIVE API
        </span>
      </header>

      {/* Overview cards */}
      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="rounded-lg border bg-card/80 p-4">
            <div className="flex items-center justify-between gap-2 text-muted-foreground">
              <span className="text-xs">{kpi.label}</span>
              <kpi.icon
                className={`h-4 w-4 shrink-0 ${
                  kpi.hot ? "text-destructive" : ""
                }`}
              />
            </div>
            <div className="mt-2 font-mono text-xl font-semibold tabular-nums">
              {kpi.value}
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="mb-4 grid gap-4 lg:grid-cols-2">
        <Panel title="Transaction risk distribution">
          {riskDistribution.length === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">
              No transaction distribution data returned by the API.
            </p>
          ) : (
            <>
              <div className="h-64">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      dataKey="count"
                      nameKey="label"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={2}
                      stroke="none"
                    >
                      {riskDistribution.map((item) => (
                        <Cell key={item.level} fill={item.fill} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={tooltipStyle} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <ul className="space-y-2">
                {riskDistribution.map((item) => (
                  <li
                    key={item.level}
                    className="flex items-center justify-between text-sm"
                  >
                    <LevelBadge level={item.level} />
                    <span className="font-mono text-xs tabular-nums text-muted-foreground">
                      {fmt(item.count)}
                      {totalDistributed > 0
                        ? ` · ${((item.count / totalDistributed) * 100).toFixed(1)}%`
                        : ""}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </Panel>

        <Panel title="Average risk by country">
          {countryRisk.length === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">
              No country risk data returned by the API.
            </p>
          ) : (
            <div className="h-80">
              <ResponsiveContainer>
                <BarChart data={countryRisk} margin={{ bottom: 8 }}>
                  <CartesianGrid stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="label" {...axis} />
                  <YAxis {...axis} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar
                    dataKey="averageRisk"
                    name="Average risk score"
                    fill="var(--chart-1)"
                    radius={[3, 3, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Panel>
      </div>

      {/* Customer/account risk table */}
      <Panel title="Highest-risk customers and accounts">
        <div className="mb-3 flex gap-1 rounded-md bg-muted p-1">
          {(["customers", "accounts"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setEntityTab(tab)}
              className={`flex-1 rounded px-3 py-2 text-xs capitalize transition-colors ${
                entityTab === tab
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {entities.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No {entityTab} risk records returned by the API.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left font-mono text-xs text-muted-foreground">
                <tr>
                  <th className="pb-2 pr-4">ID</th>
                  <th className="pb-2 pr-4">Average risk</th>
                  <th className="pb-2 pr-4">Max risk</th>
                  <th className="pb-2 pr-4">Risk level</th>
                  <th className="pb-2 pr-4 text-right">
                    {entityTab === "customers"
                      ? "Accounts"
                      : "Transactions"}
                  </th>
                  <th className="pb-2 pr-4 text-right">Critical</th>
                  <th className="pb-2 pr-4 text-right">High risk</th>
                  <th className="pb-2 pr-4 text-right">Risk ratio</th>
                  <th className="pb-2 text-right">Transaction amount</th>
                </tr>
              </thead>

              <tbody>
                {entities.slice(0, 10).map((row, index) => {
                  /*
                   * Customer and account responses have different schemas.
                   * Map each one explicitly instead of guessing field names.
                   */
                  const isCustomer = entityTab === "customers";

                  const id = textValue(
                    isCustomer ? row.customer_id : row.account_id,
                    `Record ${index + 1}`,
                  );

                  const score = numberValue(
                    isCustomer
                      ? row.average_account_risk
                      : row.average_risk_score,
                  );

                  const maxScore = numberValue(
                    isCustomer
                      ? row.max_account_risk_score
                      : row.max_risk_score,
                  );

                  const level = normaliseLevel(
                    isCustomer
                      ? row.customer_risk_level
                      : row.account_risk_level,
                  );

                  const count = numberValue(
                    isCustomer ? row.account_count : row.transaction_count,
                  );

                  const criticalCount = numberValue(
                    isCustomer
                      ? row.critical_accounts
                      : row.critical_risk_count,
                  );

                  const highRiskCount = numberValue(
                    isCustomer
                      ? row.high_risk_accounts
                      : row.high_risk_count,
                  );

                  const riskRatio = numberValue(
                    isCustomer
                      ? row.risky_account_ratio
                      : row.risk_transaction_ratio,
                  );

                  const amount = numberValue(
                    row.total_transaction_amount,
                  );

                  return (
                    <tr
                      key={`${id}-${index}`}
                      className="border-t hover:bg-accent/40"
                    >
                      <td className="py-3 pr-4 font-mono text-xs">
                        {id}
                      </td>

                      <td className="py-3 pr-4 font-mono tabular-nums">
                        {score.toFixed(2)}
                      </td>

                      <td className="py-3 pr-4 font-mono tabular-nums">
                        {fmt(maxScore)}
                      </td>

                      <td className="py-3 pr-4">
                        <LevelBadge level={level} />
                      </td>

                      <td className="py-3 pr-4 text-right font-mono tabular-nums">
                        {fmt(count)}
                      </td>

                      <td className="py-3 pr-4 text-right font-mono tabular-nums">
                        {fmt(criticalCount)}
                      </td>

                      <td className="py-3 pr-4 text-right font-mono tabular-nums">
                        {fmt(highRiskCount)}
                      </td>

                      <td className="py-3 pr-4 text-right font-mono tabular-nums">
                        {(riskRatio * 100).toFixed(1)}%
                      </td>

                      <td className="py-3 text-right font-mono tabular-nums">
                        {money(amount)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}
