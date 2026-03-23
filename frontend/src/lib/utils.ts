import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatAmount(amount: string | number): string {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat("fr-MA", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("fr-MA", {
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("fr-MA");
}

const BUSINESS_TIMEZONE = "Africa/Casablanca";

export function getTodayBusinessDateValue(now: Date = new Date()): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: BUSINESS_TIMEZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(now);

  const year = parts.find((part) => part.type === "year")?.value;
  const month = parts.find((part) => part.type === "month")?.value;
  const day = parts.find((part) => part.type === "day")?.value;

  if (!year || !month || !day) {
    throw new Error("Unable to format business date");
  }

  return `${year}-${month}-${day}`;
}

export function isPastBusinessDate(value: string): boolean {
  if (!value) return false;
  return value < getTodayBusinessDateValue();
}

export function maxDateValue(...values: string[]): string {
  return values.filter(Boolean).sort().at(-1) ?? "";
}
