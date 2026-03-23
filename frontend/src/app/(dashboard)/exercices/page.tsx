"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCurrentDossier } from "@/hooks/use-dossier";
import api from "@/lib/api";
import {
  formatDate,
  formatNumber,
  getTodayBusinessDateValue,
  isPastBusinessDate,
  maxDateValue,
} from "@/lib/utils";
import { toast } from "sonner";
import type { AccountingPeriod, DashboardStats, FiscalYear } from "@/types";

const FISCAL_YEAR_LABELS: Record<string, string> = {
  CREATED: "Cree",
  OPEN: "Ouvert",
  PRE_CLOSING: "Pre-cloture",
  CLOSED: "Cloture",
  REOPENED: "Reouvert",
};

const PERIOD_LABELS: Record<string, string> = {
  OPEN: "Ouverte",
  LOCKED: "Verrouillee",
  CLOSED: "Cloturee",
};

function fiscalYearVariant(
  status: string
): "default" | "success" | "warning" | "danger" {
  if (status === "OPEN" || status === "REOPENED") return "success";
  if (status === "PRE_CLOSING") return "warning";
  return "default";
}

function periodVariant(
  status: string
): "default" | "success" | "warning" | "danger" {
  if (status === "OPEN") return "success";
  if (status === "LOCKED") return "warning";
  if (status === "CLOSED") return "danger";
  return "default";
}

function defaultFiscalYearForm() {
  const today = getTodayBusinessDateValue();
  const currentYear = Number(today.slice(0, 4));
  const endOfCurrentYear = `${currentYear}-12-31`;
  const fallbackEndDate =
    endOfCurrentYear > today ? endOfCurrentYear : `${currentYear + 1}-12-31`;
  return {
    name: `Exercice ${currentYear}`,
    start_date: today,
    end_date: fallbackEndDate,
  };
}

export default function ExercicesPage() {
  const queryClient = useQueryClient();
  const { dossierId, currentDossier } = useCurrentDossier();
  const todayDate = getTodayBusinessDateValue();
  const [showForm, setShowForm] = useState(false);
  const [selectedFyId, setSelectedFyId] = useState("");
  const [form, setForm] = useState(defaultFiscalYearForm);

  const { data: stats } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/dashboard-stats?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const { data: fiscalYears, isLoading: fiscalYearsLoading } = useQuery<FiscalYear[]>({
    queryKey: ["fiscal-years", dossierId],
    queryFn: async () =>
      (await api.get(`/core/fiscal-years?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  useEffect(() => {
    if (!selectedFyId && fiscalYears && fiscalYears.length > 0) {
      const activeFiscalYear =
        fiscalYears.find((fy) => fy.status === "OPEN" || fy.status === "REOPENED") ??
        fiscalYears[0];
      setSelectedFyId(activeFiscalYear.id);
    }
  }, [selectedFyId, fiscalYears]);

  useEffect(() => {
    if (!showForm) {
      setForm(defaultFiscalYearForm());
    }
  }, [showForm]);

  const { data: periods, isLoading: periodsLoading } = useQuery<AccountingPeriod[]>({
    queryKey: ["periods", selectedFyId],
    queryFn: async () =>
      (await api.get(`/core/fiscal-years/${selectedFyId}/periods`)).data,
    enabled: !!selectedFyId,
  });

  const createFiscalYear = useMutation({
    mutationFn: async (payload: typeof form) =>
      (
        await api.post("/core/fiscal-years", {
          dossier_id: dossierId,
          ...payload,
        })
      ).data as FiscalYear,
    onSuccess: (createdFiscalYear) => {
      queryClient.invalidateQueries({ queryKey: ["fiscal-years", dossierId] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats", dossierId] });
      setSelectedFyId(createdFiscalYear.id);
      setShowForm(false);
      setForm(defaultFiscalYearForm());
      toast.success("Exercice cree");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  const lockPeriod = useMutation({
    mutationFn: async (periodId: string) =>
      (await api.post(`/core/periods/${periodId}/lock`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["periods", selectedFyId] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats", dossierId] });
      toast.success("Periode verrouillee");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  const openPeriods = periods?.filter((period) => period.status === "OPEN").length ?? 0;
  const lockedPeriods =
    periods?.filter((period) => period.status === "LOCKED").length ?? 0;

  return (
    <div>
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold">Exercices et periodes</h1>
          {currentDossier && (
            <p className="text-gray-500 mt-1">Dossier actif : {currentDossier.name}</p>
          )}
        </div>
        <Button onClick={() => setShowForm((prev) => !prev)}>
          {showForm ? "Annuler" : "Nouvel exercice"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border p-4">
          <p className="text-sm text-gray-500 mb-1">Exercices</p>
          <p className="text-2xl font-bold">
            {formatNumber(stats?.fiscal_years_count ?? 0)}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {formatNumber(stats?.open_fiscal_years_count ?? 0)} ouvert(s)
          </p>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <p className="text-sm text-gray-500 mb-1">Periodes ouvertes</p>
          <p className="text-2xl font-bold">
            {formatNumber(stats?.open_periods_count ?? 0)}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            sur {formatNumber(stats?.periods_count ?? 0)} periode(s)
          </p>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <p className="text-sm text-gray-500 mb-1">Periodes verrouillees</p>
          <p className="text-2xl font-bold">
            {formatNumber(stats?.locked_periods_count ?? 0)}
          </p>
          <p className="text-xs text-gray-400 mt-1">pilotage mensuel du dossier</p>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Creer un exercice fiscal</h2>
          <form
            className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end"
            onSubmit={(event) => {
              event.preventDefault();
              if (isPastBusinessDate(form.start_date)) {
                toast.error("La date de debut ne peut pas etre anterieure a la date du jour.");
                return;
              }
              if (isPastBusinessDate(form.end_date)) {
                toast.error("La date de fin ne peut pas etre anterieure a la date du jour.");
                return;
              }
              if (form.end_date <= form.start_date) {
                toast.error("La date de fin doit etre posterieure a la date de debut.");
                return;
              }
              createFiscalYear.mutate(form);
            }}
          >
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-1">Libelle</label>
              <Input
                value={form.name}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, name: event.target.value }))
                }
                placeholder="Exercice 2026"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date debut</label>
              <Input
                type="date"
                value={form.start_date}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, start_date: event.target.value }))
                }
                min={todayDate}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date fin</label>
              <Input
                type="date"
                value={form.end_date}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, end_date: event.target.value }))
                }
                min={maxDateValue(todayDate, form.start_date)}
                required
              />
            </div>
            <div className="md:col-span-4 text-xs text-gray-500">
              La creation genere automatiquement les periodes mensuelles ainsi qu'une
              periode OD.
            </div>
            <div className="md:col-span-4 flex justify-end">
              <Button type="submit" disabled={createFiscalYear.isPending || !dossierId}>
                {createFiscalYear.isPending ? "Creation..." : "Creer l'exercice"}
              </Button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-[0.95fr_1.05fr] gap-6">
        <div className="bg-white rounded-xl border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Exercices</h2>
            <Badge variant="default">
              {formatNumber(fiscalYears?.length ?? 0)} total
            </Badge>
          </div>

          {fiscalYearsLoading ? (
            <div className="space-y-3">
              {[0, 1, 2].map((idx) => (
                <div key={idx} className="h-20 rounded bg-gray-100 animate-pulse" />
              ))}
            </div>
          ) : !fiscalYears || fiscalYears.length === 0 ? (
            <div className="rounded-lg border border-dashed px-4 py-8 text-center text-gray-500">
              Aucun exercice pour ce dossier. Creez-en un pour ouvrir les periodes
              comptables.
            </div>
          ) : (
            <div className="space-y-3">
              {fiscalYears.map((fiscalYear) => (
                <button
                  type="button"
                  key={fiscalYear.id}
                  onClick={() => setSelectedFyId(fiscalYear.id)}
                  className={`w-full rounded-lg border px-4 py-4 text-left transition-colors ${
                    selectedFyId === fiscalYear.id
                      ? "border-brand-500 bg-brand-50"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-medium">{fiscalYear.name}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        {formatDate(fiscalYear.start_date)} - {formatDate(fiscalYear.end_date)}
                      </p>
                    </div>
                    <Badge variant={fiscalYearVariant(fiscalYear.status)}>
                      {FISCAL_YEAR_LABELS[fiscalYear.status] ?? fiscalYear.status}
                    </Badge>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold">Periodes de l'exercice</h2>
              <p className="text-sm text-gray-500">
                Verrouillez les mois finalises pour securiser la tenue comptable.
              </p>
            </div>
            <div className="text-right text-sm">
              <p className="font-medium">{formatNumber(openPeriods)} ouverte(s)</p>
              <p className="text-gray-500">{formatNumber(lockedPeriods)} verrouillee(s)</p>
            </div>
          </div>

          {!selectedFyId ? (
            <div className="rounded-lg border border-dashed px-4 py-8 text-center text-gray-500">
              Selectionnez un exercice pour consulter ses periodes.
            </div>
          ) : periodsLoading ? (
            <div className="space-y-3">
              {[0, 1, 2, 3].map((idx) => (
                <div key={idx} className="h-12 rounded bg-gray-100 animate-pulse" />
              ))}
            </div>
          ) : !periods || periods.length === 0 ? (
            <div className="rounded-lg border border-dashed px-4 py-8 text-center text-gray-500">
              Aucune periode generee pour cet exercice.
            </div>
          ) : (
            <div className="overflow-x-auto border rounded-lg">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b">
                    <th className="text-left px-4 py-3 font-medium text-gray-700">
                      Periode
                    </th>
                    <th className="text-left px-4 py-3 font-medium text-gray-700">
                      Debut
                    </th>
                    <th className="text-left px-4 py-3 font-medium text-gray-700">
                      Fin
                    </th>
                    <th className="text-left px-4 py-3 font-medium text-gray-700">
                      Statut
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-700">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {periods.map((period) => (
                    <tr key={period.id} className="border-b last:border-0">
                      <td className="px-4 py-3 font-medium">{period.name}</td>
                      <td className="px-4 py-3 text-gray-600">
                        {formatDate(period.start_date)}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {formatDate(period.end_date)}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={periodVariant(period.status)}>
                          {PERIOD_LABELS[period.status] ?? period.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {period.status === "OPEN" ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => lockPeriod.mutate(period.id)}
                            disabled={lockPeriod.isPending}
                          >
                            Verrouiller
                          </Button>
                        ) : (
                          <span className="text-xs text-gray-400">Aucune action</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
