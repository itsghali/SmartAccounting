"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { useCurrentDossier } from "@/hooks/use-dossier";
import { formatAmount } from "@/lib/utils";
import type { FiscalYear } from "@/types";

interface CPCEntry {
  account_number: string;
  account_label: string;
  montant: string;
}

interface CPCData {
  produits_exploitation: CPCEntry[];
  charges_exploitation: CPCEntry[];
  total_produits_exploitation: string;
  total_charges_exploitation: string;
  resultat_exploitation: string;
  produits_financiers: CPCEntry[];
  charges_financieres: CPCEntry[];
  total_produits_financiers: string;
  total_charges_financieres: string;
  resultat_financier: string;
  resultat_courant: string;
  produits_non_courants: CPCEntry[];
  charges_non_courantes: CPCEntry[];
  total_produits_non_courants: string;
  total_charges_non_courantes: string;
  resultat_non_courant: string;
  impots_sur_resultats: string;
  resultat_avant_impots: string;
  resultat_net: string;
}

function CPCSection({
  title,
  entries,
  total,
  type,
}: {
  title: string;
  entries: CPCEntry[];
  total: string;
  type: "produit" | "charge";
}) {
  if (entries.length === 0 && parseFloat(total) === 0) return null;
  const bg = type === "produit" ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800";
  return (
    <div className="mb-2">
      <div className={`px-4 py-2 font-semibold text-xs uppercase tracking-wide ${bg}`}>
        {title}
      </div>
      {entries.map((e) => (
        <div
          key={e.account_number}
          className="flex justify-between px-4 py-1.5 text-sm border-b border-gray-100"
        >
          <span>
            <span className="font-mono text-gray-400 mr-2 text-xs">{e.account_number}</span>
            {e.account_label}
          </span>
          <span className="font-mono">{formatAmount(e.montant)}</span>
        </div>
      ))}
      <div className="flex justify-between px-4 py-2 font-bold text-sm bg-gray-50">
        <span>Total</span>
        <span className="font-mono">{formatAmount(total)}</span>
      </div>
    </div>
  );
}

function ResultRow({
  label,
  value,
  size = "normal",
}: {
  label: string;
  value: string;
  size?: "normal" | "large";
}) {
  const isPositive = parseFloat(value) >= 0;
  return (
    <div
      className={`flex justify-between px-4 py-3 font-bold border-t-2 ${
        size === "large" ? "bg-brand-50 text-lg" : "bg-gray-100"
      }`}
    >
      <span>{label}</span>
      <span
        className={`font-mono ${isPositive ? "text-green-700" : "text-red-700"}`}
      >
        {formatAmount(value)}
      </span>
    </div>
  );
}

export default function CPCPage() {
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

  const { data: cpc, isLoading } = useQuery<CPCData>({
    queryKey: ["cpc", dossierId, fiscalYearId],
    queryFn: async () =>
      (await api.get(`/reporting/cpc?${queryParams}`)).data,
    enabled: !!dossierId,
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Compte de Produits et Charges (CPC)</h1>
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
      ) : !cpc ? (
        <div className="bg-white border rounded-lg p-8 text-center text-gray-500">
          Aucune donnee disponible.
        </div>
      ) : (
        <div className="bg-white border rounded-lg overflow-hidden">
          {/* I — Exploitation */}
          <div className="bg-brand-900 text-white px-4 py-2 font-bold text-sm uppercase tracking-wider">
            I — Resultat d'exploitation
          </div>
          <CPCSection
            title="Produits d'exploitation"
            entries={cpc.produits_exploitation}
            total={cpc.total_produits_exploitation}
            type="produit"
          />
          <CPCSection
            title="Charges d'exploitation"
            entries={cpc.charges_exploitation}
            total={cpc.total_charges_exploitation}
            type="charge"
          />
          <ResultRow label="RESULTAT D'EXPLOITATION" value={cpc.resultat_exploitation} />

          {/* II — Financier */}
          <div className="bg-brand-900 text-white px-4 py-2 font-bold text-sm uppercase tracking-wider mt-2">
            II — Resultat financier
          </div>
          <CPCSection
            title="Produits financiers"
            entries={cpc.produits_financiers}
            total={cpc.total_produits_financiers}
            type="produit"
          />
          <CPCSection
            title="Charges financieres"
            entries={cpc.charges_financieres}
            total={cpc.total_charges_financieres}
            type="charge"
          />
          <ResultRow label="RESULTAT FINANCIER" value={cpc.resultat_financier} />

          {/* III — Courant */}
          <ResultRow label="RESULTAT COURANT" value={cpc.resultat_courant} />

          {/* IV — Non courant */}
          <div className="bg-brand-900 text-white px-4 py-2 font-bold text-sm uppercase tracking-wider mt-2">
            IV — Resultat non courant
          </div>
          <CPCSection
            title="Produits non courants"
            entries={cpc.produits_non_courants}
            total={cpc.total_produits_non_courants}
            type="produit"
          />
          <CPCSection
            title="Charges non courantes"
            entries={cpc.charges_non_courantes}
            total={cpc.total_charges_non_courantes}
            type="charge"
          />
          <ResultRow label="RESULTAT NON COURANT" value={cpc.resultat_non_courant} />

          {/* V — Impots + Resultat net */}
          <div className="mt-2">
            <ResultRow label="RESULTAT AVANT IMPOTS" value={cpc.resultat_avant_impots} />
            <div className="flex justify-between px-4 py-2 text-sm bg-gray-50">
              <span>Impots sur les resultats</span>
              <span className="font-mono">{formatAmount(cpc.impots_sur_resultats)}</span>
            </div>
            <ResultRow label="RESULTAT NET DE L'EXERCICE" value={cpc.resultat_net} size="large" />
          </div>
        </div>
      )}
    </div>
  );
}
