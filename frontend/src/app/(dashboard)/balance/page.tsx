"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { useCurrentDossier } from "@/hooks/use-dossier";
import { formatAmount } from "@/lib/utils";
import type { FiscalYear } from "@/types";

interface BalanceLine {
  account_number: string;
  account_label: string;
  account_class: number;
  nature: string;
  total_debit: string;
  total_credit: string;
  solde_debiteur: string;
  solde_crediteur: string;
}

export default function BalancePage() {
  const { dossierId } = useCurrentDossier();
  const [fiscalYearId, setFiscalYearId] = useState("");
  const [validatedOnly, setValidatedOnly] = useState(true);

  const { data: fiscalYears } = useQuery<FiscalYear[]>({
    queryKey: ["fiscal-years", dossierId],
    queryFn: async () =>
      (await api.get(`/core/fiscal-years?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const queryParams = new URLSearchParams({ dossier_id: dossierId || "" });
  if (fiscalYearId) queryParams.set("fiscal_year_id", fiscalYearId);
  queryParams.set("validated_only", String(validatedOnly));

  const { data: balance, isLoading } = useQuery<BalanceLine[]>({
    queryKey: ["balance-generale", dossierId, fiscalYearId, validatedOnly],
    queryFn: async () =>
      (await api.get(`/reporting/balance-generale?${queryParams}`)).data,
    enabled: !!dossierId,
  });

  const totals = balance?.reduce(
    (acc, line) => ({
      debit: acc.debit + parseFloat(line.total_debit),
      credit: acc.credit + parseFloat(line.total_credit),
      soldeD: acc.soldeD + parseFloat(line.solde_debiteur),
      soldeC: acc.soldeC + parseFloat(line.solde_crediteur),
    }),
    { debit: 0, credit: 0, soldeD: 0, soldeC: 0 }
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Balance generale</h1>
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-lg p-4 mb-6 flex items-center gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Exercice fiscal
          </label>
          <select
            value={fiscalYearId}
            onChange={(e) => setFiscalYearId(e.target.value)}
            className="h-9 border rounded-md px-2 text-sm min-w-[200px]"
          >
            <option value="">Tous les exercices</option>
            {fiscalYears?.map((fy) => (
              <option key={fy.id} value={fy.id}>
                {fy.name} ({fy.status})
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2 mt-4">
          <input
            type="checkbox"
            id="validatedOnly"
            checked={validatedOnly}
            onChange={(e) => setValidatedOnly(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="validatedOnly" className="text-sm text-gray-600">
            Ecritures validees uniquement
          </label>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Chargement...</div>
      ) : !balance || balance.length === 0 ? (
        <div className="bg-white border rounded-lg p-8 text-center text-gray-500">
          Aucun mouvement comptable pour les criteres selectionnes.
        </div>
      ) : (
        <div className="overflow-x-auto border rounded-lg">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left px-4 py-3 font-medium text-gray-700">Compte</th>
                <th className="text-left px-4 py-3 font-medium text-gray-700">Libelle</th>
                <th className="text-right px-4 py-3 font-medium text-gray-700">Mouvement Debit</th>
                <th className="text-right px-4 py-3 font-medium text-gray-700">Mouvement Credit</th>
                <th className="text-right px-4 py-3 font-medium text-gray-700">Solde Debiteur</th>
                <th className="text-right px-4 py-3 font-medium text-gray-700">Solde Crediteur</th>
              </tr>
            </thead>
            <tbody>
              {balance.map((line) => (
                <tr
                  key={line.account_number}
                  className="border-b last:border-0 hover:bg-gray-50"
                >
                  <td className="px-4 py-2.5 font-mono font-medium">
                    {line.account_number}
                  </td>
                  <td className="px-4 py-2.5">{line.account_label}</td>
                  <td className="px-4 py-2.5 text-right font-mono">
                    {formatAmount(line.total_debit)}
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono">
                    {formatAmount(line.total_credit)}
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono">
                    {parseFloat(line.solde_debiteur) > 0
                      ? formatAmount(line.solde_debiteur)
                      : ""}
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono">
                    {parseFloat(line.solde_crediteur) > 0
                      ? formatAmount(line.solde_crediteur)
                      : ""}
                  </td>
                </tr>
              ))}
            </tbody>
            {totals && (
              <tfoot>
                <tr className="bg-gray-100 font-bold border-t-2">
                  <td className="px-4 py-3" colSpan={2}>
                    TOTAUX
                  </td>
                  <td className="px-4 py-3 text-right font-mono">
                    {formatAmount(totals.debit)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono">
                    {formatAmount(totals.credit)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono">
                    {formatAmount(totals.soldeD)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono">
                    {formatAmount(totals.soldeC)}
                  </td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      )}
    </div>
  );
}
