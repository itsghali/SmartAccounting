"use client";

import { LogOut, User } from "lucide-react";
import { useCurrentUser, useLogout } from "@/hooks/use-auth";
import { DossierSwitcher } from "./dossier-switcher";
import { Button } from "./ui/button";

export function Header() {
  const { data: user } = useCurrentUser();
  const logout = useLogout();

  return (
    <header className="h-14 border-b bg-white flex items-center justify-between px-6">
      <DossierSwitcher />
      <div className="flex items-center gap-4">
        {user && (
          <span className="text-sm text-gray-600">
            {user.first_name} {user.last_name}
          </span>
        )}
        <Button variant="ghost" size="icon" onClick={logout}>
          <LogOut className="w-4 h-4" />
        </Button>
      </div>
    </header>
  );
}
