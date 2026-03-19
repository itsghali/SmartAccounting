"use client";

import { useCurrentDossier } from "@/hooks/use-dossier";
import { Building2 } from "lucide-react";

export function DossierSwitcher() {
  const { dossierId, setDossierId, currentDossier, dossiers } =
    useCurrentDossier();

  if (dossiers.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      <Building2 className="w-4 h-4 text-gray-500" />
      <select
        value={dossierId ?? ""}
        onChange={(e) => setDossierId(e.target.value)}
        className="text-sm border border-gray-200 rounded-md px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        {dossiers.map((d) => (
          <option key={d.id} value={d.id}>
            {d.name}
          </option>
        ))}
      </select>
    </div>
  );
}
