import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router";
import { useAuth } from "../auth/AuthContext";
import { SUPABASE_DEMO } from "../lib/supabase";
import { Aviso, Button, Campo, Input, Select } from "../components/ui";
import type { Papel } from "../types";

export default function Login() {
  const { perfil, entrar, recuperarSenha } = useAuth();
  const navegar = useNavigate();
  const destino = (useLocation().state as { de?: string } | null)?.de ?? "/";

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [papelDemo, setPapelDemo] = useState<Papel>("administrador");
  const [erro, setErro] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (perfil) return <Navigate to={destino} replace />;

  async function aoEnviar(e: FormEvent) {
    e.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      await entrar(email, senha, papelDemo);
      navegar(destino, { replace: true });
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Falha no login.");
    } finally {
      setEnviando(false);
    }
  }

  async function aoRecuperar() {
    if (!email) return setErro("Digite seu e-mail para recuperar a senha.");
    try {
      await recuperarSenha(email);
      setInfo("Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha.");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Falha ao enviar o e-mail.");
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-slate-50 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-700">RU · USP São Carlos</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">Apoio à decisão</h1>
          <p className="mt-1 text-sm text-slate-500">Entre com sua conta para continuar</p>
        </div>

        <form onSubmit={aoEnviar} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          {SUPABASE_DEMO && <Aviso>Modo demonstração: qualquer e-mail e senha funcionam.</Aviso>}
          {erro && <Aviso tipo="erro">{erro}</Aviso>}
          {info && <Aviso tipo="sucesso">{info}</Aviso>}

          <Campo rotulo="E-mail">
            <Input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </Campo>
          <Campo rotulo="Senha">
            <Input type="password" required={!SUPABASE_DEMO} autoComplete="current-password" value={senha} onChange={(e) => setSenha(e.target.value)} />
          </Campo>

          {SUPABASE_DEMO && (
            <Campo rotulo="Entrar como (só no modo demonstração)">
              <Select value={papelDemo} onChange={(e) => setPapelDemo(e.target.value as Papel)}>
                <option value="administrador">Administrador</option>
                <option value="usuario">Usuário</option>
              </Select>
            </Campo>
          )}

          <Button type="submit" disabled={enviando} className="w-full">
            {enviando ? "Entrando…" : "Entrar"}
          </Button>
          {!SUPABASE_DEMO && (
            <button type="button" onClick={aoRecuperar} className="block w-full text-center text-xs text-blue-700 hover:underline">
              Esqueci minha senha
            </button>
          )}
        </form>
      </div>
    </div>
  );
}
