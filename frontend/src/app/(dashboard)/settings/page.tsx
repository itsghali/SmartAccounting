"use client";

import { useEffect, useState, type ElementType, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Building2,
  Lock,
  Settings2,
  Shield,
  Trash2,
  User,
  Users,
} from "lucide-react";
import { useCurrentUser } from "@/hooks/use-auth";
import api from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import type { Company, Dossier, Role, User as AppUser } from "@/types";

interface FullCompany extends Company {
  patente: string | null;
  cnss_employer: string | null;
  address: string | null;
  city: string | null;
  phone: string | null;
  email: string | null;
}

type Tab = "societe" | "profil" | "securite" | "administration";

function FormField({
  label,
  name,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  name: string;
  value: string;
  onChange: (name: string, value: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <Input
        type={type}
        value={value}
        onChange={(e) => onChange(name, e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("societe");
  const { data: currentUser } = useCurrentUser();

  const canManageAdministration =
    currentUser?.roles.some(
      (role) => role === "Administrateur" || role === "Responsable"
    ) ?? false;
  const canAssignElevatedRoles =
    currentUser?.roles.includes("Administrateur") ?? false;

  const tabs: { key: Tab; label: string; icon: ElementType }[] = [
    { key: "societe", label: "Societe", icon: Building2 },
    { key: "profil", label: "Profil", icon: User },
    { key: "securite", label: "Securite", icon: Lock },
    ...(canManageAdministration
      ? [{ key: "administration" as Tab, label: "Administration", icon: Shield }]
      : []),
  ];

  useEffect(() => {
    if (activeTab === "administration" && !canManageAdministration) {
      setActiveTab("societe");
    }
  }, [activeTab, canManageAdministration]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Parametres</h1>

      <div className="flex gap-2 mb-6 border-b flex-wrap">
        {tabs.map((tab) => (
          <button
            type="button"
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${
              activeTab === tab.key
                ? "border-brand-600 text-brand-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "societe" && <CompanyTab />}
      {activeTab === "profil" && <ProfileTab />}
      {activeTab === "securite" && <SecurityTab />}
      {activeTab === "administration" && canManageAdministration && (
        <AdministrationTab canAssignElevatedRoles={canAssignElevatedRoles} />
      )}
    </div>
  );
}

function CompanyTab() {
  const queryClient = useQueryClient();
  const { data: companies, isLoading } = useQuery<FullCompany[]>({
    queryKey: ["companies"],
    queryFn: async () => (await api.get("/tenant/companies")).data,
  });

  const company = companies?.[0];

  const [form, setForm] = useState({
    name: "",
    legal_form: "",
    ice: "",
    if_number: "",
    rc: "",
    patente: "",
    cnss_employer: "",
    address: "",
    city: "",
    phone: "",
    email: "",
  });

  useEffect(() => {
    if (company) {
      setForm({
        name: company.name || "",
        legal_form: company.legal_form || "",
        ice: company.ice || "",
        if_number: company.if_number || "",
        rc: company.rc || "",
        patente: company.patente || "",
        cnss_employer: company.cnss_employer || "",
        address: company.address || "",
        city: company.city || "",
        phone: company.phone || "",
        email: company.email || "",
      });
    }
  }, [company]);

  const updateCompany = useMutation({
    mutationFn: async (data: typeof form) =>
      (await api.put(`/tenant/companies/${company!.id}`, data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      toast.success("Societe mise a jour");
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.detail || "Erreur lors de la mise a jour"),
  });

  if (isLoading) {
    return <div className="bg-white border rounded-lg p-6 animate-pulse h-96" />;
  }

  if (!company) {
    return (
      <div className="bg-white border rounded-lg p-6 text-gray-500">
        Aucune societe trouvee.
      </div>
    );
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    updateCompany.mutate(form);
  };

  const handleChange = (name: string, value: string) => {
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Informations generales</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Raison sociale" name="name" value={form.name} onChange={handleChange} placeholder="Ma societe SARL" />
          <FormField label="Forme juridique" name="legal_form" value={form.legal_form} onChange={handleChange} placeholder="SARL, SA, SAS..." />
          <FormField label="Ville" name="city" value={form.city} onChange={handleChange} placeholder="Casablanca" />
          <FormField label="Adresse" name="address" value={form.address} onChange={handleChange} placeholder="123 Bd Mohammed V" />
          <FormField label="Telephone" name="phone" value={form.phone} onChange={handleChange} placeholder="+212 5XX XX XX XX" />
          <FormField label="Email" name="email" value={form.email} onChange={handleChange} placeholder="contact@societe.ma" type="email" />
        </div>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Identifiants fiscaux</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="ICE" name="ice" value={form.ice} onChange={handleChange} placeholder="00xxxxxxxxxx00" />
          <FormField label="IF (Identifiant Fiscal)" name="if_number" value={form.if_number} onChange={handleChange} placeholder="XXXXXXXX" />
          <FormField label="RC (Registre de Commerce)" name="rc" value={form.rc} onChange={handleChange} placeholder="XXXXX" />
          <FormField label="Patente" name="patente" value={form.patente} onChange={handleChange} placeholder="XXXXXXXX" />
          <FormField label="CNSS Employeur" name="cnss_employer" value={form.cnss_employer} onChange={handleChange} placeholder="XXXXXXXX" />
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={updateCompany.isPending}>
          {updateCompany.isPending ? "Enregistrement..." : "Enregistrer"}
        </Button>
      </div>
    </form>
  );
}

function ProfileTab() {
  const queryClient = useQueryClient();
  const { data: user, isLoading } = useQuery<AppUser>({
    queryKey: ["current-user"],
    queryFn: async () => (await api.get("/auth/me")).data,
  });

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
  });

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
      });
    }
  }, [user]);

  const updateProfile = useMutation({
    mutationFn: async (data: typeof form) =>
      (await api.put("/auth/profile", data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["current-user"] });
      toast.success("Profil mis a jour");
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.detail || "Erreur lors de la mise a jour"),
  });

  if (isLoading) {
    return <div className="bg-white border rounded-lg p-6 animate-pulse h-64" />;
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        updateProfile.mutate(form);
      }}
      className="space-y-6"
    >
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Mon profil</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Prenom" name="first_name" value={form.first_name} onChange={(n, v) => setForm((prev) => ({ ...prev, [n]: v }))} />
          <FormField label="Nom" name="last_name" value={form.last_name} onChange={(n, v) => setForm((prev) => ({ ...prev, [n]: v }))} />
          <div className="md:col-span-2">
            <FormField label="Email" name="email" value={form.email} onChange={(n, v) => setForm((prev) => ({ ...prev, [n]: v }))} type="email" />
          </div>
        </div>
        {user && (
          <div className="mt-4 pt-4 border-t text-sm text-gray-500">
            Role :{" "}
            <span className="font-medium text-gray-700">
              {user.roles.join(", ") || "Collaborateur"}
            </span>
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={updateProfile.isPending}>
          {updateProfile.isPending ? "Enregistrement..." : "Enregistrer"}
        </Button>
      </div>
    </form>
  );
}

function SecurityTab() {
  const [form, setForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const changePassword = useMutation({
    mutationFn: async (data: {
      current_password: string;
      new_password: string;
    }) => await api.post("/auth/change-password", data),
    onSuccess: () => {
      toast.success("Mot de passe modifie");
      setForm({ current_password: "", new_password: "", confirm_password: "" });
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.detail || "Erreur lors du changement"),
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (form.new_password !== form.confirm_password) {
      toast.error("Les mots de passe ne correspondent pas");
      return;
    }
    if (form.new_password.length < 8) {
      toast.error("Le mot de passe doit contenir au moins 8 caracteres");
      return;
    }
    changePassword.mutate({
      current_password: form.current_password,
      new_password: form.new_password,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Changer le mot de passe</h2>
        <div className="max-w-md space-y-4">
          <FormField label="Mot de passe actuel" name="current_password" value={form.current_password} onChange={(n, v) => setForm((prev) => ({ ...prev, [n]: v }))} type="password" />
          <FormField label="Nouveau mot de passe" name="new_password" value={form.new_password} onChange={(n, v) => setForm((prev) => ({ ...prev, [n]: v }))} type="password" />
          <FormField label="Confirmer le nouveau mot de passe" name="confirm_password" value={form.confirm_password} onChange={(n, v) => setForm((prev) => ({ ...prev, [n]: v }))} type="password" />
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={changePassword.isPending}>
          {changePassword.isPending ? "Modification..." : "Modifier le mot de passe"}
        </Button>
      </div>
    </form>
  );
}

function AdministrationTab({
  canAssignElevatedRoles,
}: {
  canAssignElevatedRoles: boolean;
}) {
  const queryClient = useQueryClient();
  const { data: users, isLoading: usersLoading } = useQuery<AppUser[]>({
    queryKey: ["admin-users"],
    queryFn: async () => (await api.get("/auth/users")).data,
  });
  const { data: roles } = useQuery<Role[]>({
    queryKey: ["admin-roles"],
    queryFn: async () => (await api.get("/auth/roles")).data,
  });
  const { data: dossiers, isLoading: dossiersLoading } = useQuery<Dossier[]>({
    queryKey: ["dossiers"],
    queryFn: async () => (await api.get("/tenant/dossiers")).data,
  });
  const assignableRoles =
    roles?.filter(
      (role) =>
        canAssignElevatedRoles ||
        !["Administrateur", "Responsable"].includes(role.name),
    ) ?? [];

  const [userForm, setUserForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    role_name: "Collaborateur",
  });

  useEffect(() => {
    if (
      assignableRoles.length > 0 &&
      !assignableRoles.some((role) => role.name === userForm.role_name)
    ) {
      setUserForm((prev) => ({ ...prev, role_name: assignableRoles[0].name }));
    }
  }, [assignableRoles, userForm.role_name]);

  const createUser = useMutation({
    mutationFn: async () => (await api.post("/auth/users", userForm)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      toast.success("Utilisateur cree");
      setUserForm({
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        role_name: assignableRoles[0]?.name ?? "Collaborateur",
      });
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.detail || "Erreur lors de la creation"),
  });

  const deleteDossierMutation = useMutation({
    mutationFn: async (dossierId: string) =>
      await api.delete(`/tenant/dossiers/${dossierId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dossiers"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      toast.success("Dossier supprime");
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.detail || "Erreur lors de la suppression"),
  });

  function handleDeleteDossier(dossier: Dossier) {
    const confirmed = window.confirm(
      `Supprimer le dossier "${dossier.name}" ? Cette suppression est logique et le dossier disparaitra de la liste active.`
    );
    if (!confirmed) return;
    deleteDossierMutation.mutate(dossier.id);
  }

  return (
    <div className="space-y-6">
      <div className="bg-white border rounded-lg p-6">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h2 className="text-lg font-semibold">Gestion des utilisateurs</h2>
            <p className="text-sm text-gray-500 mt-1">
              Les roles systeme sont predefinis par tenant. Seuls les profils
              Administrateur et Responsable voient cet ecran.
            </p>
            {!canAssignElevatedRoles && (
              <p className="text-xs text-amber-700 mt-2">
                En tant que Responsable, tu peux creer des collaborateurs,
                mais pas d'autres responsables ni d'administrateurs.
              </p>
            )}
          </div>
          <Badge variant="default">
            <Settings2 className="w-3 h-3 mr-1" />
            Admin tenant
          </Badge>
        </div>

        <form
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 items-end mb-6"
          onSubmit={(e) => {
            e.preventDefault();
            createUser.mutate();
          }}
        >
          <FormField label="Prenom" name="first_name" value={userForm.first_name} onChange={(n, v) => setUserForm((prev) => ({ ...prev, [n]: v }))} />
          <FormField label="Nom" name="last_name" value={userForm.last_name} onChange={(n, v) => setUserForm((prev) => ({ ...prev, [n]: v }))} />
          <FormField label="Email" name="email" value={userForm.email} onChange={(n, v) => setUserForm((prev) => ({ ...prev, [n]: v }))} type="email" />
          <FormField label="Mot de passe" name="password" value={userForm.password} onChange={(n, v) => setUserForm((prev) => ({ ...prev, [n]: v }))} type="password" />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <select
              value={userForm.role_name}
              onChange={(e) =>
                setUserForm((prev) => ({ ...prev, role_name: e.target.value }))
              }
              className="w-full h-10 border rounded-md px-2 text-sm"
            >
              {assignableRoles.map((role) => (
                <option key={role.id} value={role.name}>
                  {role.name}
                </option>
              ))}
            </select>
          </div>
          <div className="md:col-span-2 xl:col-span-5 flex justify-end">
            <Button type="submit" disabled={createUser.isPending}>
              {createUser.isPending ? "Creation..." : "Creer l'utilisateur"}
            </Button>
          </div>
        </form>

        {usersLoading ? (
          <div className="h-40 animate-pulse rounded bg-gray-100" />
        ) : !users || users.length === 0 ? (
          <div className="rounded-lg border border-dashed p-6 text-sm text-gray-500">
            Aucun utilisateur.
          </div>
        ) : (
          <div className="overflow-x-auto border rounded-lg">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b">
                  <th className="text-left px-4 py-3 font-medium text-gray-700">
                    Utilisateur
                  </th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">
                    Email
                  </th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">
                    Roles
                  </th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">
                    Statut
                  </th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b last:border-0">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-400" />
                        {user.first_name} {user.last_name}
                      </div>
                    </td>
                    <td className="px-4 py-3">{user.email}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2 flex-wrap">
                        {user.roles.map((role) => (
                          <Badge key={role} variant="default">
                            {role}
                          </Badge>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={user.is_active ? "success" : "default"}>
                        {user.is_active ? "Actif" : "Inactif"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-2">Suppression de dossier</h2>
        <p className="text-sm text-gray-500 mb-4">
          La suppression est logique: le dossier passe en statut supprime et
          disparait de la liste active.
        </p>

        {dossiersLoading ? (
          <div className="h-32 animate-pulse rounded bg-gray-100" />
        ) : !dossiers || dossiers.length === 0 ? (
          <div className="rounded-lg border border-dashed p-6 text-sm text-gray-500">
            Aucun dossier actif.
          </div>
        ) : (
          <div className="space-y-3">
            {dossiers.map((dossier) => (
              <div
                key={dossier.id}
                className="flex items-center justify-between gap-4 rounded-lg border p-4"
              >
                <div>
                  <p className="font-medium">{dossier.name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Statut: {dossier.status}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDeleteDossier(dossier)}
                  disabled={deleteDossierMutation.isPending}
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Supprimer
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
