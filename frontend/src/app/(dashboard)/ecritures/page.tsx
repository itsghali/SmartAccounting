"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { useCurrentDossier } from "@/hooks/use-dossier";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/data-table";
import { formatAmount, formatDate } from "@/lib/utils";
import { toast } from "sonner";
import type { JournalEntry, Journal, Account, FiscalYear, AccountingPeriod } from "@/types";

interface EntryLineForm {
  account_id: string;
  label: string;
  debit: string;
  credit: string;
}

export default function EcrituresPage() {
  const queryClient = useQueryClient();
  const { dossierId } = useCurrentDossier();
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [journalId, setJournalId] = useState("");
  const [periodId, setPeriodId] = useState("");
  const [entryDate, setEntryDate] = useState("");
  const [entryLabel, setEntryLabel] = useState("");
  const [lines, setLines] = useState<EntryLineForm[]>([
    { account_id: "", label: "", debit: "", credit: "" },
    { account_id: "", label: "", debit: "", credit: "" },
  ]);

  // Queries
  const { data: entries, isLoading } = useQuery<JournalEntry[]>({
    queryKey: ["entries", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/entries?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const { data: journals } = useQuery<Journal[]>({
    queryKey: ["journals", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/journals?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const { data: accounts } = useQuery<Account[]>({
    queryKey: ["accounts", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/accounts?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const { data: fiscalYears } = useQuery<FiscalYear[]>({
    queryKey: ["fiscal-years", dossierId],
    queryFn: async () =>
      (await api.get(`/core/fiscal-years?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const activeFyId = fiscalYears?.find((fy) => fy.status === "OPEN")?.id;

  const { data: periods } = useQuery<AccountingPeriod[]>({
    queryKey: ["periods", activeFyId],
    queryFn: async () =>
      (await api.get(`/core/fiscal-years/${activeFyId}/periods`)).data,
    enabled: !!activeFyId,
  });

  // Mutations
  const createEntry = useMutation({
    mutationFn: async (data: any) =>
      (await api.post("/accounting/entries", data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["entries", dossierId] });
      resetForm();
      toast.success("Écriture créée en brouillard");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  const validateEntry = useMutation({
    mutationFn: async (entryId: string) =>
      (await api.post(`/accounting/entries/${entryId}/validate`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["entries", dossierId] });
      toast.success("Écriture validée");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  const reverseEntry = useMutation({
    mutationFn: async (entryId: string) =>
      (await api.post(`/accounting/entries/${entryId}/reverse`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["entries", dossierId] });
      toast.success("Contrepassation créée");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  function resetForm() {
    setShowForm(false);
    setJournalId("");
    setPeriodId("");
    setEntryDate("");
    setEntryLabel("");
    setLines([
      { account_id: "", label: "", debit: "", credit: "" },
      { account_id: "", label: "", debit: "", credit: "" },
    ]);
  }

  function updateLine(index: number, field: keyof EntryLineForm, value: string) {
    const updated = [...lines];
    updated[index] = { ...updated[index], [field]: value };
    setLines(updated);
  }

  function addLine() {
    setLines([...lines, { account_id: "", label: "", debit: "", credit: "" }]);
  }

  function removeLine(index: number) {
    if (lines.length <= 2) return;
    setLines(lines.filter((_, i) => i !== index));
  }

  const totalDebit = lines.reduce((sum, l) => sum + (parseFloat(l.debit) || 0), 0);
  const totalCredit = lines.reduce((sum, l) => sum + (parseFloat(l.credit) || 0), 0);
  const isBalanced = Math.abs(totalDebit - totalCredit) < 0.005 && totalDebit > 0;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    createEntry.mutate({
      dossier_id: dossierId,
      journal_id: journalId,
      period_id: periodId,
      entry_date: entryDate,
      label: entryLabel,
      lines: lines
        .filter((l) => l.account_id)
        .map((l) => ({
          account_id: l.account_id,
          label: l.label || entryLabel,
          debit: l.debit || "0.00",
          credit: l.credit || "0.00",
        })),
    });
  }

  const columns = [
    { key: "entry_date", header: "Date", render: (e: JournalEntry) => formatDate(e.entry_date) },
    { key: "piece_number", header: "Pièce" },
    { key: "label", header: "Libellé" },
    {
      key: "total_debit",
      header: "Débit",
      render: (e: JournalEntry) => (
        <span className="font-mono">{formatAmount(e.total_debit)}</span>
      ),
    },
    {
      key: "total_credit",
      header: "Crédit",
      render: (e: JournalEntry) => (
        <span className="font-mono">{formatAmount(e.total_credit)}</span>
      ),
    },
    {
      key: "status",
      header: "Statut",
      render: (e: JournalEntry) => (
        <Badge variant={e.status === "VALIDATED" ? "success" : "warning"}>
          {e.status === "DRAFT" ? "Brouillard" : "Validée"}
        </Badge>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (e: JournalEntry) => (
        <div className="flex gap-1">
          {e.status === "DRAFT" && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => validateEntry.mutate(e.id)}
            >
              Valider
            </Button>
          )}
          {e.status === "VALIDATED" && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => reverseEntry.mutate(e.id)}
            >
              Contrepasser
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Écritures comptables</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Annuler" : "Nouvelle écriture"}
        </Button>
      </div>

      {showForm && (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-1">Journal</label>
                <select
                  value={journalId}
                  onChange={(e) => setJournalId(e.target.value)}
                  className="w-full h-10 border rounded-md px-2 text-sm"
                  required
                >
                  <option value="">Sélectionner</option>
                  {journals?.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.code} — {j.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Période</label>
                <select
                  value={periodId}
                  onChange={(e) => setPeriodId(e.target.value)}
                  className="w-full h-10 border rounded-md px-2 text-sm"
                  required
                >
                  <option value="">Sélectionner</option>
                  {periods
                    ?.filter((p) => p.status === "OPEN")
                    .map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Date</label>
                <Input
                  type="date"
                  value={entryDate}
                  onChange={(e) => setEntryDate(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Libellé</label>
                <Input
                  value={entryLabel}
                  onChange={(e) => setEntryLabel(e.target.value)}
                  placeholder="Libellé de l'écriture"
                  required
                />
              </div>
            </div>

            {/* Lines */}
            <div className="mb-4">
              <div className="grid grid-cols-12 gap-2 text-xs font-medium text-gray-500 mb-2 px-1">
                <div className="col-span-4">Compte</div>
                <div className="col-span-3">Libellé</div>
                <div className="col-span-2 text-right">Débit</div>
                <div className="col-span-2 text-right">Crédit</div>
                <div className="col-span-1"></div>
              </div>

              {lines.map((line, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 mb-2">
                  <div className="col-span-4">
                    <select
                      value={line.account_id}
                      onChange={(e) => updateLine(idx, "account_id", e.target.value)}
                      className="w-full h-9 border rounded-md px-2 text-sm"
                    >
                      <option value="">Compte...</option>
                      {accounts?.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.number} — {a.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="col-span-3">
                    <Input
                      value={line.label}
                      onChange={(e) => updateLine(idx, "label", e.target.value)}
                      placeholder="Libellé ligne"
                      className="h-9"
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={line.debit}
                      onChange={(e) => updateLine(idx, "debit", e.target.value)}
                      placeholder="0.00"
                      className="h-9 text-right font-mono"
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={line.credit}
                      onChange={(e) => updateLine(idx, "credit", e.target.value)}
                      placeholder="0.00"
                      className="h-9 text-right font-mono"
                    />
                  </div>
                  <div className="col-span-1 flex items-center">
                    {lines.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeLine(idx)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              ))}

              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={addLine}
                className="mt-1"
              >
                + Ajouter une ligne
              </Button>
            </div>

            {/* Totals */}
            <div className="flex items-center justify-between border-t pt-4">
              <div className="flex gap-6 text-sm">
                <span>
                  Total Débit :{" "}
                  <strong className="font-mono">{formatAmount(totalDebit)}</strong>
                </span>
                <span>
                  Total Crédit :{" "}
                  <strong className="font-mono">{formatAmount(totalCredit)}</strong>
                </span>
                <span>
                  Écart :{" "}
                  <strong
                    className={`font-mono ${isBalanced ? "text-green-600" : "text-red-600"}`}
                  >
                    {formatAmount(Math.abs(totalDebit - totalCredit))}
                  </strong>
                </span>
              </div>
              <Button type="submit" disabled={!isBalanced || createEntry.isPending}>
                {createEntry.isPending ? "Enregistrement..." : "Enregistrer (Brouillard)"}
              </Button>
            </div>
          </form>
        </div>
      )}

      <DataTable
        columns={columns}
        data={entries ?? []}
        isLoading={isLoading}
        emptyMessage="Aucune écriture — Créez un exercice fiscal d'abord"
      />
    </div>
  );
}
