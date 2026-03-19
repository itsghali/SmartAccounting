"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { useCurrentDossier } from "@/hooks/use-dossier";
import { formatAmount, formatDate } from "@/lib/utils";
import type { FiscalYear, Account } from "@/types";

interface GrandLivreLine {
  date: string;
  piece_number: string;
  label: string;
  debit: string;
  credit: string;
  lettrage_code: string | null;
}

interface GrandLivreAccount {
  account_number: string;
  account_label: string;
  lines: GrandLivreLine[];
  total_debit: string;
  total_credit: string;
  solde: string;
}

export default function GrandLivrePage() {
  const { dossierId } = useCurrentDossier();
  const [fiscalYearId, setFiscalYearId] = useState("");
  const [accountFilter, setAccountFilter] = useState("");
  const [validatedOnly, setValidatedOnly] = useState(true);

  const { data: fiscalYears } = useQuery<FiscalYear[]>({
    queryKey: ["fiscal-years", dossierId],
    queryFn: async () =>
      (await api.get(`/core/fiscal-years?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const { data: accounts } = useQuery<Account[]>({
    queryKey: ["accounts", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/accounts?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const queryParams = new URLSearchParams({ dossier_id: dossierId || "" });
  if (fiscalYearId) queryParams.set("fiscal_year_id", fiscalYearId);
  if (accountFilter) queryParams.set("account_number", accountFilter);
  queryParams.set("validated_only", String(validatedOnly));

  const { data: grandLivre, isLoading } = useQuery<GrandLivreAccount[]>({
    queryKey: ["grand-livre", dossierId, fiscalYearId, accountFilter, validatedOnly],
    queryFn: async () =>
      (await api.get(`/reporting/grand-livre?${queryParams}`)).data,
    enabled: !!dossierId,
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Grand livre</h1>
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-lg p-4 mb-6 flex items-center gap-4 flex-wrap">
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
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Compte
          </label>
          <select
            value={accountFilter}
            onChange={(e) => setAccountFilter(e.target.value)}
            className="h-9 border rounded-md px-2 text-sm min-w-[250px]"
          >
            <option value="">Tous les comptes</option>
            {accounts?.map((a) => (
              <option key={a.id} value={a.number}>
                {a.number} — {a.label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2 mt-4">
          <input
            type="checkbox"
            id="validatedOnlyGL"
            checked={validatedOnly}
            onChange={(e) => setValidatedOnly(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="validatedOnlyGL" className="text-sm text-gray-600">
            Validees uniquement
          </label>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Chargement...</div>
      ) : !grandLivre || grandLivre.length === 0 ? (
        <div className="bg-white border rounded-lg p-8 text-center text-gray-500">
          Aucun mouvement comptable pour les criteres selectionnes.
        </div>
      ) : (
        <div className="space-y-6">
          {grandLivre.map((account) => (
            <div
              key={account.account_number}
              className="border rounded-lg overflow-hidden"
            >
              {/* Account header */}
              <div className="bg-brand-50 px-4 py-3 flex items-center justify-between">
                <div>
                  <span className="font-mono font-bold text-brand-700">
                    {account.account_number}
                  </span>
                  <span className="ml-3 font-medium">
                    {account.account_label}
                  </span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-500">Solde : </span>
                  <span
                    className={`font-mono font-bold ${
                      parseFloat(account.solde) >= 0
                        ? "text-blue-700"
                        : "text-red-700"
                    }`}
                  >
                    {formatAmount(account.solde)}
                  </span>
                </div>
              </div>

              {/* Lines */}
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b">
                    <th className="text-left px-4 py-2 font-medium text-gray-600">Date</th>
                    <th className="text-left px-4 py-2 font-medium text-gray-600">Piece</th>
                    <th className="text-left px-4 py-2 font-medium text-gray-600">Libelle</th>
                    <th className="text-right px-4 py-2 font-medium text-gray-600">Debit</th>
                    <th className="text-right px-4 py-2 font-medium text-gray-600">Credit</th>
                    <th className="text-center px-4 py-2 font-medium text-gray-600">Lettrage</th>
                  </tr>
                </thead>
                <tbody>
                  {account.lines.map((line, idx) => (
                    <tr
                      key={idx}
                      className="border-b last:border-0 hover:bg-gray-50"
                    >
                      <td className="px-4 py-2">{formatDate(line.date)}</td>
                      <td className="px-4 py-2 font-mono text-xs">
                        {line.piece_number}
                      </td>
                      <td className="px-4 py-2">{line.label}</td>
                      <td className="px-4 py-2 text-right font-mono">
                        {parseFloat(line.debit) > 0 ? formatAmount(line.debit) : ""}
                      </td>
                      <td className="px-4 py-2 text-right font-mono">
                        {parseFloat(line.credit) > 0 ? formatAmount(line.credit) : ""}
                      </td>
                      <td className="px-4 py-2 text-center text-xs text-gray-400">
                        {line.lettrage_code || ""}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="bg-gray-100 font-bold">
                    <td className="px-4 py-2" colSpan={3}>
                      Total
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatAmount(account.total_debit)}
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatAmount(account.total_credit)}
                    </td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
