import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router";
import { useAuth } from "./AuthContext";
import type { Papel } from "../types";

/** Protege uma rota: exige login e, opcionalmente, um papel específico. */
export function RequireAuth({ children, papel }: { children: ReactNode; papel?: Papel }) {
  const { perfil, carregando } = useAuth();
  const local = useLocation();

  if (carregando) {
    return <div className="grid h-screen place-items-center text-slate-500">Carregando…</div>;
  }
  if (!perfil) {
    return <Navigate to="/login" replace state={{ de: local.pathname }} />;
  }
  if (papel && perfil.papel !== papel) {
    return (
      <div className="p-8">
        <h1 className="text-lg font-semibold">Acesso restrito</h1>
        <p className="mt-1 text-slate-600">Esta página é exclusiva para administradores.</p>
      </div>
    );
  }
  return <>{children}</>;
}
