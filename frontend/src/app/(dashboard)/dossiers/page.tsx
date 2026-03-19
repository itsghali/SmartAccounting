"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import type { Dossier, Company } from "@/types";

export default function DossiersPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");

  const { data: companies } = useQuery<Company[]>({
    queryKey: ["companies"],
    queryFn: async () => (await api.get("/tenant/companies")).data,
  });

  const { data: dossiers, isLoading } = useQuery<Dossier[]>({
    queryKey: ["dossiers"],
    queryFn: async () => (await api.get("/tenant/dossiers")).data,
  });

  const createDossier = useMutation({
    mutationFn: async (data: { company_id: string; name: string }) =>
      (await api.post("/tenant/dossiers", data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dossiers"] });
      setShowForm(false);
      setName("");
      toast.success("Dossier créé");
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Erreur"),
  });

  const columns = [
    { key: "name", header: "Nom" },
    {
      key: "status",
      header: "Statut",
      render: (d: Dossier) => (
        <Badge variant={d.status === "active" ? "success" : "default"}>
          {d.status}
        </Badge>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Dossiers</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Annuler" : "Nouveau dossier"}
        </Button>
      </div>

      {showForm && companies && companies.length > 0 && (
        <div className="bg-white border rounded-lg p-4 mb-6">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (name && companies[0]) {
                createDossier.mutate({
                  company_id: companies[0].id,
                  name,
                });
              }
            }}
            className="flex gap-3 items-end"
          >
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1">
                Nom du dossier
              </label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ex: Dossier Client ABC"
              />
            </div>
            <Button type="submit" disabled={createDossier.isPending}>
              Créer
            </Button>
          </form>
        </div>
      )}

      <DataTable
        columns={columns}
        data={dossiers ?? []}
        isLoading={isLoading}
        emptyMessage="Aucun dossier"
      />
    </div>
  );
}
