"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Dossier } from "@/types";

const DOSSIER_KEY = "ea_current_dossier";

/* ── Standalone hook (no context needed) ── */

export function useDossiers() {
  return useQuery<Dossier[]>({
    queryKey: ["dossiers"],
    queryFn: async () => {
      const { data } = await api.get("/tenant/dossiers");
      return data;
    },
  });
}

/* ── Context ── */

interface DossierContextValue {
  dossierId: string | null;
  setDossierId: (id: string) => void;
  currentDossier: Dossier | null;
  dossiers: Dossier[];
}

const DossierContext = createContext<DossierContextValue | null>(null);

/* ── Provider — mount once in the layout ── */

export function DossierProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const { data: dossiers } = useDossiers();

  const [dossierId, setDossierIdState] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(DOSSIER_KEY);
    }
    return null;
  });

  // Ensure the stored dossier still belongs to the current tenant/session.
  useEffect(() => {
    if (!dossiers) return;

    if (dossiers.length === 0) {
      setDossierIdState(null);
      localStorage.removeItem(DOSSIER_KEY);
      return;
    }

    const storedDossier = dossiers.find((d) => d.id === dossierId);
    if (!storedDossier) {
      setDossierIdState(dossiers[0].id);
      localStorage.setItem(DOSSIER_KEY, dossiers[0].id);
    }
  }, [dossierId, dossiers]);

  const setDossierId = useCallback(
    (id: string) => {
      setDossierIdState(id);
      localStorage.setItem(DOSSIER_KEY, id);
      // Invalidate ALL dossier-dependent queries so pages refetch immediately
      queryClient.invalidateQueries();
    },
    [queryClient],
  );

  const currentDossier = dossiers?.find((d) => d.id === dossierId) ?? null;
  const effectiveDossierId = currentDossier?.id ?? null;

  return (
    <DossierContext.Provider
      value={{
        dossierId: effectiveDossierId,
        setDossierId,
        currentDossier,
        dossiers: dossiers ?? [],
      }}
    >
      {children}
    </DossierContext.Provider>
  );
}

/* ── Consumer hook ── */

export function useCurrentDossier(): DossierContextValue {
  const ctx = useContext(DossierContext);
  if (!ctx) {
    throw new Error(
      "useCurrentDossier must be used inside <DossierProvider>",
    );
  }
  return ctx;
}
