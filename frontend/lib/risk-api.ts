export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

// 1. Overview

export interface RiskOverview {
  total_transaction_count: number;
  total_transaction_amount: number;
  total_customer_count: number;
  total_account_count: number;
  high_risk_transactions: number;
  high_risk_customers: number;
  high_risk_accounts: number;
  critical_risk_transactions: number;
  critical_risk_customers: number;
  critical_risk_accounts: number;
}

// 2. Risk distribution

export interface TransactionDistribution {
  risk_level: RiskLevel;
  count: number;
}

export interface AccountDistribution {
  account_risk_level: RiskLevel;
  count: number;
}

export interface CustomerDistribution {
  customer_risk_level: RiskLevel;
  count: number;
}

export interface RiskDistribution {
  transaction_distribution: TransactionDistribution[];
  account_distribution: AccountDistribution[];
  customer_distribution: CustomerDistribution[];
}

// 3. Risk analysis

export interface RiskByCountry {
  transaction_country: string;
  country_name: string;
  transaction_count: number;
  high_risk_count: number;
  critical_risk_count: number;
  average_risk_score: number;
}

export interface RiskByMerchantCategory {
  merchant_category: string;
  transaction_count: number;
  high_risk_count: number;
  critical_risk_count: number;
  average_risk_score: number;
}

export interface RiskByTransactionType {
  transaction_type: string;
  transaction_count: number;
  high_risk_count: number;
  critical_risk_count: number;
  avg_risk_score: number;
}

export interface RiskByPaymentMethod {
  payment_method: string;
  transaction_count: number;
  high_risk_count: number;
  critical_risk_count: number;
  avg_risk_score: number;
}

export interface RiskByTime {
  time_period: string;
  transaction_count: number;
  high_risk_count: number;
  critical_risk_count: number;
  average_risk_score: number;
  risky_transaction_ratio: number;
}

export interface RiskAnalysis {
  risk_by_country: RiskByCountry[];
  risk_by_merchant_category: RiskByMerchantCategory[];
  risk_by_transaction_type: RiskByTransactionType[];
  risk_by_payment_method: RiskByPaymentMethod[];
  risk_by_time: RiskByTime[];
}

// 4. Account risk

export interface RiskiestAccount {
  account_id: string;
  account_risk_level: RiskLevel;
  average_risk_score: number;
  max_risk_score: number;
  risk_transaction_ratio: number;
  high_risk_count: number;
  critical_risk_count: number;
  transaction_count: number;
  total_transaction_amount: number;
}

export interface RiskiestAccountByAmount {
  account_id: string;
  transaction_count: number;
  total_transaction_amount: number;
  average_risk_score: number;
  risk_transaction_ratio: number;
  account_risk_level: RiskLevel;
  critical_risk_count: number;
  high_risk_count: number;
}

export interface AccountRisk {
  riskiest_accounts: RiskiestAccount[];
  riskiest_accounts_by_amount: RiskiestAccountByAmount[];
}

// 5. Customer risk

export interface RiskiestCustomer {
  customer_id: string;
  account_count: number;
  customer_risk_level: RiskLevel;
  critical_accounts: number;
  high_risk_accounts: number;
  risky_account_ratio: number;
  average_account_risk: number;
  max_account_risk_score: number;
  total_transaction_amount: number;
}

export interface RiskyCustomerByAmount {
  customer_id: string;
  customer_risk_level: RiskLevel;
  account_count: number;
  transaction_count: number;
  total_transaction_amount: number;
  average_account_risk: number;
  critical_accounts: number;
  high_risk_accounts: number;
}

export interface RiskyCustomerByCriticalCount {
  customer_id: string;
  customer_risk_level: RiskLevel;
  account_count: number;
  transaction_count: number;
  total_transaction_amount: number;
  average_account_risk: number;
  max_account_risk_score: number;
  critical_accounts: number;
  high_risk_accounts: number;
  risky_account_ratio: number;
}

export interface CustomerRisk {
  riskiest_customers: RiskiestCustomer[];
  risky_customer_by_amount: RiskyCustomerByAmount[];
  risky_customer_by_critical_count: RiskyCustomerByCriticalCount[];
}

// 6. API endpoint paths

export const ENDPOINTS = {
  overview: "/api/risk/get_overview",
  distribution: "/api/risk/get_risk_distributions",
  analysis: "/api/risk/get_transaction_analysis",
  accountRisk: "/api/risk/get_account_analysis",
  customerRisk: "/api/risk/get_customer_analysis",
} as const;

// 7. Combined dashboard data

export interface DashboardData {
  overview: RiskOverview;
  distribution: RiskDistribution;
  analysis: RiskAnalysis;
  accountRisk: AccountRisk;
  customerRisk: CustomerRisk;
}

// 8. Fetch helpers

async function fetchJson<T>(path: string): Promise<T> {
  const base = process.env.NEXT_PUBLIC_RISK_API_URL;

  if (!base) {
    throw new Error(
      "NEXT_PUBLIC_RISK_API_URL is not configured."
    );
  }

  const url = base.replace(/\/+$/, "") + path;

  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `API request failed: ${path} (${response.status})`
    );
  }

  return response.json() as Promise<T>;
}

// 9. Fetch all dashboard data

export async function fetchDashboard(): Promise<
  DashboardData & { live: true }
> {
  const [
    overview,
    distribution,
    analysis,
    accountRisk,
    customerRisk,
  ] = await Promise.all([
    fetchJson<RiskOverview>(ENDPOINTS.overview),
    fetchJson<RiskDistribution>(ENDPOINTS.distribution),
    fetchJson<RiskAnalysis>(ENDPOINTS.analysis),
    fetchJson<AccountRisk>(ENDPOINTS.accountRisk),
    fetchJson<CustomerRisk>(ENDPOINTS.customerRisk),
  ]);

  return {
    overview,
    distribution,
    analysis,
    accountRisk,
    customerRisk,
    live: true,
  };
}
