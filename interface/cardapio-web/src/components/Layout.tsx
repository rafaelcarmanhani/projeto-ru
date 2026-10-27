import { NavLink, Outlet } from "react-router";
import { useAuth } from "../auth/AuthContext";
import { SUPABASE_DEMO } from "../lib/supabase";
import { API_DEMO } from "../lib/api";
import type { Papel } from "../types";

const itens: { para: string; rotulo: string; papel?: Papel }[] = [
  { para: "/", rotulo: "Início" },
  { para: "/previsao", rotulo: "Previsão de demanda" },
  { para: "/cardapio", rotulo: "Gerar cardápio", papel: "administrador" },
  { para: "/base", rotulo: "Base de dados", papel: "administrador" },
  { para: "/modelo", rotulo: "Modelo e retreino", papel: "administrador" },
];

export function Layout() {
  const { perfil, sair } = useAuth();
  const visiveis = itens.filter((i) => !i.papel || i.papel === perfil?.papel);

  return (
    <div className="min-h-screen bg-slate-50 md:flex">
      <aside className="border-b border-slate-200 bg-white md:sticky md:top-0 md:h-screen md:w-64 md:shrink-0 md:border-r md:border-b-0">
        <div className="px-5 py-4 md:py-6">
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-700">RU · USP São Carlos</p>
          <p className="text-sm text-slate-500">Apoio à decisão</p>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-col md:pb-0">
          {visiveis.map((i) => (
            <NavLink
              key={i.para}
              to={i.para}
              end={i.para === "/"}
              className={({ isActive }) =>
                `whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? "bg-blue-50 text-blue-800" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              {i.rotulo}
            </NavLink>
          ))}
        </nav>
        <div className="hidden border-t border-slate-200 px-5 py-4 md:absolute md:bottom-0 md:block md:w-64">
          <p className="truncate text-sm font-medium text-slate-800">{perfil?.nome}</p>
          <p className="text-xs capitalize text-slate-500">{perfil?.papel}</p>
          <button onClick={sair} className="mt-2 text-xs font-medium text-blue-700 hover:underline">Sair</button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 px-4 py-6 md:px-10 md:py-8">
        {(SUPABASE_DEMO || API_DEMO) && (
          <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-xs text-amber-800">
            Modo demonstração ({[SUPABASE_DEMO && "sem Supabase", API_DEMO && "sem API"].filter(Boolean).join(", ")}):
            os dados são fictícios. Preencha o arquivo <code>.env.local</code> para conectar.
          </div>
        )}
        <div className="mb-4 flex items-center justify-end md:hidden">
          <button onClick={sair} className="text-xs font-medium text-blue-700">Sair ({perfil?.nome})</button>
        </div>
        <Outlet />
      </main>
    </div>
  );
}
