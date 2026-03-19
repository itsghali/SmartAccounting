"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { useCurrentDossier } from "@/hooks/use-dossier";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DataTable } from "@/components/data-table";
import { toast } from "sonner";
import type { Journal } from "@/types";

const JOURNAL_TYPES = [
  { value: "achat", label: "Achats" },
  { value: "vente", label: "Ventes" },
  { value: "tresorerie", label: "Trésorerie" },
  { value: "od", label: "Opérations diverses" },
  { value: "an", label: "À-nouveaux" },
  { value: "situation", label: "Situation" },
];

export default function JournauxPage() {
  const queryClient = useQueryClient();
  const { dossierId } = useCurrentDossier();
  const [showForm, setShowForm] = useState(false);
  const [code, setCode] = useState("");
  const [label, setLabel] = useState("");
  const [journalType, setJournalType] = useState("achat");

  const { data: journals, isLoading } = useQuery<Journal[]>({
    queryKey: ["journals", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/journals?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const createJournal = useMutation({
    mutationFn: async (data: any) =>
      (await api.post("/accounting/journals", data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["journals", dossierId] });
      setShowForm(false);
      setCode("");
      setLabel("");
      toast.success("Journal créé");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  const columns = [
    { key: "code", header: "Code" },
    { key: "label", header: "Libellé" },
    {
      key: "journal_type",
      header: "Type",
      render: (j: Journal) =>
        JOURNAL_TYPES.find((t) => t.value === j.journal_type)?.label ?? j.journal_type,
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Journaux</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Annuler" : "Nouveau journal"}
        </Button>
      </div>

      {showForm && (
        <div className="bg-white border rounded-lg p-4 mb-6">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createJournal.mutate({
                dossier_id: dossierId,
                code,
                label,
                journal_type: journalType,
              });
            }}
            className="grid grid-cols-4 gap-3 items-end"
          >
            <div>
              <label className="block text-sm font-medium mb-1">Code</label>
              <Input
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                placeholder="AC"
                maxLength={10}
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1">Libellé</label>
              <Input
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Journal des achats"
              />
            </div>
            <div className="flex gap-2 items-end">
              <div className="flex-1">
                <label className="block text-sm font-medium mb-1">Type</label>
                <select
                  value={journalType}
                  onChange={(e) => setJournalType(e.target.value)}
                  className="w-full h-10 border rounded-md px-2 text-sm"
                >
                  {JOURNAL_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
              <Button type="submit" disabled={createJournal.isPending}>
                Créer
              </Button>
            </div>
          </form>
        </div>
      )}

      <DataTable
        columns={columns}
        data={journals ?? []}
        isLoading={isLoading}
        emptyMessage="Aucun journal"
      />
    </div>
  );
}
