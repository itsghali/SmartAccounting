"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { useCurrentDossier } from "@/hooks/use-dossier";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DataTable } from "@/components/data-table";
import { toast } from "sonner";
import type { Account } from "@/types";

export default function PlanComptablePage() {
  const queryClient = useQueryClient();
  const { dossierId } = useCurrentDossier();
  const [showForm, setShowForm] = useState(false);
  const [number, setNumber] = useState("");
  const [label, setLabel] = useState("");
  const [accountClass, setAccountClass] = useState("6");

  const { data: accounts, isLoading } = useQuery<Account[]>({
    queryKey: ["accounts", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/accounts?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const createAccount = useMutation({
    mutationFn: async (data: any) =>
      (await api.post("/accounting/accounts", data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts", dossierId] });
      setShowForm(false);
      setNumber("");
      setLabel("");
      toast.success("Compte créé");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  const columns = [
    { key: "number", header: "Numéro" },
    { key: "label", header: "Libellé" },
    { key: "account_class", header: "Classe" },
    { key: "account_type", header: "Type" },
    { key: "nature", header: "Nature" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Plan comptable</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Annuler" : "Nouveau compte"}
        </Button>
      </div>

      {showForm && (
        <div className="bg-white border rounded-lg p-4 mb-6">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createAccount.mutate({
                dossier_id: dossierId,
                number,
                label,
                account_class: parseInt(accountClass),
                nature: parseInt(accountClass) >= 6 ? "debit" : "credit",
              });
            }}
            className="grid grid-cols-4 gap-3 items-end"
          >
            <div>
              <label className="block text-sm font-medium mb-1">Numéro</label>
              <Input
                value={number}
                onChange={(e) => setNumber(e.target.value)}
                placeholder="6111"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1">Libellé</label>
              <Input
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Achats de marchandises"
              />
            </div>
            <div className="flex gap-2 items-end">
              <div className="flex-1">
                <label className="block text-sm font-medium mb-1">Classe</label>
                <select
                  value={accountClass}
                  onChange={(e) => setAccountClass(e.target.value)}
                  className="w-full h-10 border rounded-md px-2 text-sm"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
              <Button type="submit" disabled={createAccount.isPending}>
                Créer
              </Button>
            </div>
          </form>
        </div>
      )}

      <DataTable
        columns={columns}
        data={accounts ?? []}
        isLoading={isLoading}
        emptyMessage="Aucun compte — Créez votre plan comptable"
      />
    </div>
  );
}
