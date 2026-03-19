"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  BookOpen,
  Calendar,
  CheckCircle2,
  Clock3,
  FileText,
  PenLine,
  TriangleAlert,
  TrendingUp,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useCurrentUser } from "@/hooks/use-auth";
import { useCurrentDossier } from "@/hooks/use-dossier";
import api from "@/lib/api";
import { formatAmount, formatDate, formatNumber } from "@/lib/utils";
import type { AuditLog, DashboardStats } from "@/types";

const ACTION_LABELS: Record<string, string> = {
  CREATE: "Creation",
  VALIDATE: "Validation",
  REVERSE: "Contrepassation",
  UPDATE: "Modification",
  DELETE: "Suppression",
};

const ENTITY_LABELS: Record<string, string> = {
  JournalEntry: "Ecriture",
  Account: "Compte",
  Journal: "Journal",
  FiscalYear: "Exercice",
  ThirdParty: "Tiers",
};

function getErrorMessage(error: unknown): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof (error as { response?: { data?: { detail?: string } } }).response ===
      "object"
  ) {
    return (
      (error as { response?: { data?: { detail?: string } } }).response?.data
        ?.detail ?? "Impossible de charger les indicateurs du dossier."
    );
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Impossible de charger les indicateurs du dossier.";
}

export default function DashboardPage() {
  const { data: user } = useCurrentUser();
  const { dossierId, currentDossier } = useCurrentDossier();

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats", dossierId],
    queryFn: async () =>
      (await api.get(`/accounting/dashboard-stats?dossier_id=${dossierId}`)).data,
    enabled: !!dossierId,
  });

  const { data: auditLogs, isLoading: auditLoading } = useQuery<AuditLog[]>({
    queryKey: ["audit-logs-recent", dossierId],
    queryFn: async () => (await api.get("/core/audit-logs?limit=10")).data,
    enabled: !!dossierId,
  });

  const kpiErrorMessage = statsError ? getErrorMessage(statsError) : null;

  function renderMetric(
    value: number | string,
    options?: { amount?: boolean }
  ) {
    if (statsLoading) {
      return (
        <span className="inline-block h-8 w-16 rounded bg-gray-100 animate-pulse" />
      );
    }
    if (!dossierId) {
      return <span className="text-sm text-gray-400">Aucun dossier</span>;
    }
    if (kpiErrorMessage) {
      return <span className="text-sm font-medium text-red-600">Erreur</span>;
    }

    if (options?.amount) {
      return formatAmount(value);
    }

    return formatNumber(Number(value));
  }

  const mainCards = [
    {
      label: "Plan de comptes",
      icon: BookOpen,
      value: stats?.accounts_count ?? 0,
      href: "/plan-comptable",
      color: "bg-blue-50 text-blue-600",
      subtitle: stats
        ? `${formatNumber(stats.accounts_count)} compte(s) disponibles`
        : undefined,
    },
    {
      label: "Journaux",
      icon: FileText,
      value: stats?.journals_count ?? 0,
      href: "/journaux",
      color: "bg-purple-50 text-purple-600",
      subtitle: stats
        ? `${formatNumber(stats.journals_count)} journal(aux) configures`
        : undefined,
    },
    {
      label: "Ecritures",
      icon: PenLine,
      value: stats?.entries_count ?? 0,
      href: "/ecritures",
      color: "bg-amber-50 text-amber-600",
      subtitle: stats
        ? `${formatNumber(stats.draft_entries_count)} brouillard / ${formatNumber(
            stats.validated_entries_count
          )} validee(s)`
        : undefined,
    },
    {
      label: "Exercices",
      icon: Calendar,
      value: stats?.fiscal_years_count ?? 0,
      href: "/exercices",
      color: "bg-green-50 text-green-600",
      subtitle: stats
        ? `${formatNumber(stats.open_fiscal_years_count)} ouvert(s) / ${formatNumber(
            stats.open_periods_count
          )} periode(s) ouverte(s)`
        : undefined,
    },
  ];

  const secondaryCards = [
    {
      label: "Tiers",
      icon: Users,
      value: stats?.third_parties_count ?? 0,
      color: "bg-slate-50 text-slate-600",
    },
    {
      label: "Periodes ouvertes",
      icon: CheckCircle2,
      value: stats?.open_periods_count ?? 0,
      color: "bg-emerald-50 text-emerald-600",
    },
    {
      label: "Brouillards",
      icon: Clock3,
      value: stats?.draft_entries_count ?? 0,
      color: "bg-orange-50 text-orange-600",
    },
    {
      label: "Mouvements valides",
      icon: TrendingUp,
      value: stats?.total_debit ?? "0",
      color: "bg-indigo-50 text-indigo-600",
      isAmount: true,
    },
  ];

  const readinessItems = [
    {
      label: "Plan comptable initialise",
      ready: (stats?.accounts_count ?? 0) > 0,
      detail: `${formatNumber(stats?.accounts_count ?? 0)} compte(s)`,
    },
    {
      label: "Journaux configures",
      ready: (stats?.journals_count ?? 0) > 0,
      detail: `${formatNumber(stats?.journals_count ?? 0)} journal(aux)`,
    },
    {
      label: "Exercice actif",
      ready: (stats?.open_fiscal_years_count ?? 0) > 0,
      detail: `${formatNumber(stats?.open_fiscal_years_count ?? 0)} ouvert(s)`,
    },
    {
      label: "Periodes disponibles",
      ready: (stats?.open_periods_count ?? 0) > 0,
      detail: `${formatNumber(stats?.open_periods_count ?? 0)} ouverte(s) / ${formatNumber(
        stats?.periods_count ?? 0
      )}`,
    },
  ];

  const attentionItems = [
    (stats?.accounts_count ?? 0) === 0
      ? {
          title: "Le plan comptable n'est pas initialise",
          description:
            "Sans comptes CGNC utilisables, la saisie comptable reste bloquee.",
          href: "/plan-comptable",
        }
      : null,
    (stats?.journals_count ?? 0) === 0
      ? {
          title: "Aucun journal n'est configure",
          description:
            "Ajoutez au minimum les journaux d'achats, ventes, tresorerie et OD.",
          href: "/journaux",
        }
      : null,
    (stats?.fiscal_years_count ?? 0) === 0
      ? {
          title: "Aucun exercice n'est encore ouvert",
          description:
            "Creez votre exercice fiscal pour generer les periodes comptables.",
          href: "/exercices",
        }
      : null,
    (stats?.fiscal_years_count ?? 0) > 0 && (stats?.open_periods_count ?? 0) === 0
      ? {
          title: "Aucune periode ouverte",
          description:
            "Le dossier a besoin d'au moins une periode ouverte pour accepter de nouvelles ecritures.",
          href: "/exercices",
        }
      : null,
    (stats?.entries_count ?? 0) === 0
      ? {
          title: "Aucune ecriture saisie",
          description:
            "Le dashboard n'apporte pas encore de pilotage metier tant que le dossier n'a pas de mouvements.",
          href: "/ecritures",
        }
      : null,
    (stats?.draft_entries_count ?? 0) > 0
      ? {
          title: `${formatNumber(stats?.draft_entries_count ?? 0)} brouillard(s) a valider`,
          description:
            "Les ecritures en brouillard ne remontent pas encore dans les editions et les montants valides.",
          href: "/ecritures",
        }
      : null,
  ].filter(Boolean) as {
    title: string;
    description: string;
    href: string;
  }[];

  const quickActions = [
    {
      title: "Gerer les exercices",
      description:
        "Creer un exercice, suivre les periodes et verrouiller les mois clos.",
      href: "/exercices",
    },
    {
      title: "Completer le plan comptable",
      description:
        "Verifier la couverture CGNC et enrichir les comptes detailles utiles.",
      href: "/plan-comptable",
    },
    {
      title: "Saisir des ecritures",
      description: "Passer vos premiers brouillards puis les valider.",
      href: "/ecritures",
    },
    {
      title: "Controler la balance",
      description: "Verifier les soldes avant les editions officielles.",
      href: "/balance",
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Bonjour, {user?.first_name ?? ""}</h1>
        {currentDossier && (
          <p className="text-gray-500 mt-1">Dossier actif : {currentDossier.name}</p>
        )}
      </div>

      {!dossierId && (
        <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Selectionnez ou creez un dossier pour charger de vraies metriques.
        </div>
      )}

      {kpiErrorMessage && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Le dashboard n'a pas pu charger ses indicateurs : {kpiErrorMessage}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {mainCards.map((card) => (
          <Link
            key={card.label}
            href={card.href}
            className="bg-white rounded-xl border p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg ${card.color}`}>
                <card.icon className="w-5 h-5" />
              </div>
              <span className="text-sm font-medium text-gray-600">{card.label}</span>
            </div>
            <p className="text-2xl font-bold">{renderMetric(card.value)}</p>
            {card.subtitle && (
              <p className="text-xs text-gray-400 mt-1">{card.subtitle}</p>
            )}
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {secondaryCards.map((card) => (
          <div key={card.label} className="bg-white rounded-xl border p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className={`p-1.5 rounded ${card.color}`}>
                <card.icon className="w-4 h-4" />
              </div>
              <span className="text-xs font-medium text-gray-500">{card.label}</span>
            </div>
            <p className={`text-lg font-bold ${card.isAmount ? "font-mono" : ""}`}>
              {renderMetric(card.value, { amount: card.isAmount })}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr] gap-6 mb-8">
        <div className="bg-white rounded-xl border p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold">Etat du dossier</h2>
              <p className="text-sm text-gray-500">
                Le dashboard doit piloter la mise en exploitation du dossier, pas
                seulement afficher des cartes.
              </p>
            </div>
            {stats && !kpiErrorMessage && (
              <Badge variant={attentionItems.length > 0 ? "warning" : "success"}>
                {attentionItems.length > 0
                  ? `${formatNumber(attentionItems.length)} point(s) d'attention`
                  : "Dossier exploitable"}
              </Badge>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
            {readinessItems.map((item) => (
              <div
                key={item.label}
                className={`rounded-lg border px-4 py-3 ${
                  item.ready
                    ? "border-green-200 bg-green-50"
                    : "border-gray-200 bg-gray-50"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium">{item.label}</p>
                    <p className="text-xs text-gray-500 mt-1">{item.detail}</p>
                  </div>
                  <Badge variant={item.ready ? "success" : "default"}>
                    {item.ready ? "OK" : "A faire"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>

          {attentionItems.length === 0 ? (
            <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
              Les fondations comptables visibles dans le dashboard sont en place.
              La prochaine etape consiste a densifier les workflows metier.
            </div>
          ) : (
            <div className="space-y-3">
              {attentionItems.map((item) => (
                <div
                  key={item.title}
                  className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3"
                >
                  <div className="flex items-start gap-3">
                    <TriangleAlert className="w-5 h-5 text-amber-600 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-amber-900">
                        {item.title}
                      </p>
                      <p className="text-sm text-amber-800 mt-1">
                        {item.description}
                      </p>
                    </div>
                    <Link
                      href={item.href}
                      className="text-sm font-medium text-amber-900 hover:underline"
                    >
                      Ouvrir
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border p-6">
          <h2 className="text-lg font-semibold mb-1">Actions prioritaires</h2>
          <p className="text-sm text-gray-500 mb-4">
            Raccourcis visibles pour transformer ce shell en vrai ecran de
            pilotage ERP.
          </p>
          <div className="space-y-3">
            {quickActions.map((action) => (
              <Link
                key={action.title}
                href={action.href}
                className="flex items-start justify-between gap-3 rounded-lg border px-4 py-3 hover:bg-gray-50"
              >
                <div>
                  <p className="text-sm font-medium">{action.title}</p>
                  <p className="text-xs text-gray-500 mt-1">{action.description}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-400 mt-1" />
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-lg font-semibold mb-4">Activite recente</h2>
        {auditLoading ? (
          <div className="space-y-3">
            {[0, 1, 2].map((idx) => (
              <div key={idx} className="h-12 rounded bg-gray-100 animate-pulse" />
            ))}
          </div>
        ) : !auditLogs || auditLogs.length === 0 ? (
          <p className="text-gray-500 text-sm">
            Commencez par creer un exercice fiscal et saisir vos premieres
            ecritures.
          </p>
        ) : (
          <div className="space-y-3">
            {auditLogs.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between py-2 border-b last:border-b-0"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      log.action === "CREATE"
                        ? "bg-green-500"
                        : log.action === "VALIDATE"
                          ? "bg-blue-500"
                          : log.action === "REVERSE"
                            ? "bg-orange-500"
                            : "bg-gray-400"
                    }`}
                  />
                  <div>
                    <p className="text-sm font-medium">
                      {ACTION_LABELS[log.action] ?? log.action}{" "}
                      {ENTITY_LABELS[log.entity_type] ?? log.entity_type}
                    </p>
                    {log.new_values && (
                      <p className="text-xs text-gray-400">
                        {log.new_values.piece_number
                          ? `Piece ${log.new_values.piece_number}`
                          : log.new_values.label
                            ? String(log.new_values.label)
                            : log.new_values.status
                              ? `Statut -> ${log.new_values.status}`
                              : ""}
                      </p>
                    )}
                  </div>
                </div>
                <span className="text-xs text-gray-400">
                  {formatDate(log.created_at)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
