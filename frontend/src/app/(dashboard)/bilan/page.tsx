"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { useCurrentDossier } from "@/hooks/use-dossier";
import { formatAmount } from "@/lib/utils";
import type { FiscalYear } from "@/types";

interface BilanEntry {
  account_number: string;
  account_label: string;
  montant: string;
}

interface BilanSide {
  actif_immobilise?: BilanEntry[];
  actif_circulant?: BilanEntry[];
  tresorerie_actif?: BilanEntry[];
  financement_permanent?: BilanEntry[];
  passif_circulant?: BilanEntry[];
  tresorerie_passif?: BilanEntry[];
  total_actif_immobilise?: string;
  total_actif_circulant?: string;
  total_tresorerie_actif?: string;
  total_actif?: string;
  total_financement_permanent?: string;
  total_passif_circulant?: string;
  total_tresorerie_passif?: string;
  total_passif?: string;
}

interface BilanData {
  actif: BilanSide;
  passif: BilanSide;
}

function BilanSection({
  title,
  entries,
  total,
  bgClass = "",
}: {
  title: string;
  entries: BilanEntry[];
  total: string;
  bgClass?: string;
}) {
  return (
    <div className="mb-4">
      <div className={`px-4 py-2 font-bold text-sm uppercase tracking-wide ${bgClass}`}>
        {title}
      </div>
      {entries.map((e) => (
        <div
          key={e.account_number}
          className="flex justify-between px-4 py-1.5 text-sm border-b border-gray-100"
        >
          <span>
            <span className="font-mono text-gray-500 mr-2">{e.account_number}</span>
            {e.account_label}
          </span>
          <span className="font-mono">{formatAmount(e.montant)}</span>
        </div>
      ))}
      <div className="flex justify-between px-4 py-2 font-bold text-sm bg-gray-50">
        <span>Total {title}</span>
        <span className="font-mono">{formatAmount(total)}</span>
      </div>
    </div>
  );
}

export default function BilanPage() {
  const { dossierId } = useCurrentDossier();
  const [fiscalYearId, setFiscalYearId] = useState("");

  const { data: fiscalYears } = useQuery<FiscalYear[]>({
    queryKey: ["fiscal-years", dossierId],
    queryFn: async () =>
      (await api.get(`/core/fiscal-years?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const queryParams = new URLSearchParams({ dossier_id: dossierId || "" });
  if (fiscalYearId) queryParams.set("fiscal_year_id", fiscalYearId);

  const { data: bilan, isLoading } = useQuery<BilanData>({
    queryKey: ["bilan", dossierId, fiscalYearId],
    queryFn: async () =>
      (await api.get(`/reporting/bilan?${queryParams}`)).data,
    enabled: !!dossierId,
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Bilan</h1>
      </div>

      {/* Filter */}
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
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Chargement...</div>
      ) : !bilan ? (
        <div className="bg-white border rounded-lg p-8 text-center text-gray-500">
          Aucune donnee disponible.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ACTIF */}
          <div className="bg-white border rounded-lg overflow-hidden">
            <div className="bg-blue-600 text-white px-4 py-3 text-center font-bold uppercase tracking-wider">
              Actif
            </div>
            <BilanSection
              title="Actif immobilise"
              entries={bilan.actif.actif_immobilise || []}
              total={bilan.actif.total_actif_immobilise || "0"}
              bgClass="bg-blue-50 text-blue-800"
            />
            <BilanSection
              title="Actif circulant"
              entries={bilan.actif.actif_circulant || []}
              total={bilan.actif.total_actif_circulant || "0"}
              bgClass="bg-blue-50 text-blue-800"
            />
            <BilanSection
              title="Tresorerie - Actif"
              entries={bilan.actif.tresorerie_actif || []}
              total={bilan.actif.total_tresorerie_actif || "0"}
              bgClass="bg-blue-50 text-blue-800"
            />
            <div className="flex justify-between px-4 py-3 font-bold bg-blue-100 text-blue-900">
              <span>TOTAL ACTIF</span>
              <span className="font-mono">{formatAmount(bilan.actif.total_actif || "0")}</span>
            </div>
          </div>

          {/* PASSIF */}
          <div className="bg-white border rounded-lg overflow-hidden">
            <div className="bg-green-700 text-white px-4 py-3 text-center font-bold uppercase tracking-wider">
              Passif
            </div>
            <BilanSection
              title="Financement permanent"
              entries={bilan.passif.financement_permanent || []}
              total={bilan.passif.total_financement_permanent || "0"}
              bgClass="bg-green-50 text-green-800"
            />
            <BilanSection
              title="Passif circulant"
              entries={bilan.passif.passif_circulant || []}
              total={bilan.passif.total_passif_circulant || "0"}
              bgClass="bg-green-50 text-green-800"
            />
            <BilanSection
              title="Tresorerie - Passif"
              entries={bilan.passif.tresorerie_passif || []}
              total={bilan.passif.total_tresorerie_passif || "0"}
              bgClass="bg-green-50 text-green-800"
            />
            <div className="flex justify-between px-4 py-3 font-bold bg-green-100 text-green-900">
              <span>TOTAL PASSIF</span>
              <span className="font-mono">{formatAmount(bilan.passif.total_passif || "0")}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
