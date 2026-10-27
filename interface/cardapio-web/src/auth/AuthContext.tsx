import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { supabase } from "../lib/supabase";
import type { Papel, Perfil } from "../types";

interface AuthValor {
  perfil: Perfil | null;
  carregando: boolean;
  entrar(email: string, senha: string, papelDemo?: Papel): Promise<void>;
  sair(): Promise<void>;
  recuperarSenha(email: string): Promise<void>;
}

const AuthContext = createContext<AuthValor | null>(null);
const CHAVE_DEMO = "ru-demo-perfil";

/** Busca nome e papel na tabela `perfil` (ligada a auth.users). */
async function carregarPerfil(userId: string, email: string): Promise<Perfil> {
  const { data, error } = await supabase!.from("perfil").select("nome, papel").eq("id", userId).single();
  if (error) throw new Error("Não foi possível carregar seu perfil: " + error.message);
  return { id: userId, email, nome: data.nome, papel: data.papel };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (!supabase) {
      try {
        const salvo = sessionStorage.getItem(CHAVE_DEMO);
        if (salvo) setPerfil(JSON.parse(salvo));
      } catch { /* sessionStorage indisponível: segue sem sessão */ }
      setCarregando(false);
      return;
    }

    supabase.auth.getSession().then(async ({ data }) => {
      const u = data.session?.user;
      if (u) setPerfil(await carregarPerfil(u.id, u.email ?? "").catch(() => null));
      setCarregando(false);
    });

    const { data: sub } = supabase.auth.onAuthStateChange((_evento, sessao) => {
      const u = sessao?.user;
      if (!u) setPerfil(null);
      else carregarPerfil(u.id, u.email ?? "").then(setPerfil).catch(() => setPerfil(null));
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  async function entrar(email: string, senha: string, papelDemo: Papel = "administrador") {
    if (!supabase) {
      const p: Perfil = { id: "demo", email, nome: email.split("@")[0] || "Demo", papel: papelDemo };
      try { sessionStorage.setItem(CHAVE_DEMO, JSON.stringify(p)); } catch { /* ignora */ }
      setPerfil(p);
      return;
    }
    const { data, error } = await supabase.auth.signInWithPassword({ email, password: senha });
    if (error) throw new Error(traduzirErro(error.message));
    setPerfil(await carregarPerfil(data.user.id, data.user.email ?? email));
  }

  async function sair() {
    if (!supabase) {
      try { sessionStorage.removeItem(CHAVE_DEMO); } catch { /* ignora */ }
      setPerfil(null);
      return;
    }
    await supabase.auth.signOut();
  }

  async function recuperarSenha(email: string) {
    if (!supabase) return;
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: window.location.origin + "/login",
    });
    if (error) throw new Error(error.message);
  }

  return (
    <AuthContext.Provider value={{ perfil, carregando, entrar, sair, recuperarSenha }}>
      {children}
    </AuthContext.Provider>
  );
}

function traduzirErro(msg: string) {
  if (msg.includes("Invalid login credentials")) return "E-mail ou senha incorretos.";
  if (msg.includes("Email not confirmed")) return "Confirme seu e-mail antes de entrar.";
  return msg;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth precisa estar dentro de <AuthProvider>");
  return ctx;
}
