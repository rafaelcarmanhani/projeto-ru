import { useState } from "react";
import { db } from "../lib/db";
import { formatarCurto, hoje, paraISO } from "../lib/datas";
import { useCarregar } from "../lib/useCarregar";
import { Aviso, Button, Campo, Card, Input, PageHeader, Select } from "../components/ui";
import { TIPOS_PRATO, type Area, type DiaCalendario, type Prato } from "../types";

type Aba = "pratos" | "areas" | "calendario";

export default function BaseDados() {
  const [aba, setAba] = useState<Aba>("pratos");
  const abas: { id: Aba; rotulo: string }[] = [
    { id: "pratos", rotulo: "Pratos" },
    { id: "areas", rotulo: "Áreas" },
    { id: "calendario", rotulo: "Calendário" },
  ];

  return (
    <>
      <PageHeader titulo="Base de dados" descricao="Dados usados pelo previsor e pelo gerador de cardápio." />
      <div className="mb-6 flex gap-1 border-b border-slate-200">
        {abas.map((a) => (
          <button
            key={a.id}
            onClick={() => setAba(a.id)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${aba === a.id ? "border-blue-700 text-blue-800" : "border-transparent text-slate-500 hover:text-slate-800"}`}
          >
            {a.rotulo}
          </button>
        ))}
      </div>
      {aba === "pratos" && <AbaPratos />}
      {aba === "areas" && <AbaAreas />}
      {aba === "calendario" && <AbaCalendario />}
    </>
  );
}

// ---------------------------------------------------------------- Pratos
const pratoVazio: Omit<Prato, "id"> & { id?: number } = { nome: "", classe: "", tipo: "prato_principal_1", descricao: "" };

function AbaPratos() {
  const pratos = useCarregar(() => db.listarPratos());
  const [form, setForm] = useState(pratoVazio);
  const [filtro, setFiltro] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  async function salvar() {
    setErro(null);
    try {
      await db.salvarPrato(form);
      setForm(pratoVazio);
      pratos.recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Falha ao salvar.");
    }
  }

  async function remover(p: Prato) {
    if (!confirm(`Remover "${p.nome}"?`)) return;
    try {
      await db.removerPrato(p.id);
      pratos.recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Falha ao remover.");
    }
  }

  const rotuloTipo = (t: string) => TIPOS_PRATO.find((x) => x.valor === t)?.rotulo ?? t;
  const visiveis = (pratos.dados ?? []).filter((p) => p.nome.toLowerCase().includes(filtro.toLowerCase()));

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card titulo={form.id ? "Editar prato" : "Novo prato"}>
        <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); salvar(); }}>
          {erro && <Aviso tipo="erro">{erro}</Aviso>}
          <Campo rotulo="Nome"><Input required value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} /></Campo>
          <Campo rotulo="Tipo">
            <Select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value as Prato["tipo"] })}>
              {TIPOS_PRATO.map((t) => <option key={t.valor} value={t.valor}>{t.rotulo}</option>)}
            </Select>
          </Campo>
          <Campo rotulo="Classe"><Input placeholder="ex.: frango, massa, fruta" value={form.classe} onChange={(e) => setForm({ ...form, classe: e.target.value })} /></Campo>
          <Campo rotulo="Descrição"><Input value={form.descricao} onChange={(e) => setForm({ ...form, descricao: e.target.value })} /></Campo>
          <div className="flex gap-2">
            <Button type="submit">{form.id ? "Salvar alterações" : "Adicionar"}</Button>
            {form.id && <Button type="button" variante="secundario" onClick={() => setForm(pratoVazio)}>Cancelar</Button>}
          </div>
        </form>
      </Card>

      <Card titulo={`Pratos cadastrados (${pratos.dados?.length ?? 0})`} className="lg:col-span-2">
        <Input placeholder="Buscar por nome…" value={filtro} onChange={(e) => setFiltro(e.target.value)} className="mb-3" />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr><th className="py-2">Nome</th><th className="py-2">Tipo</th><th className="py-2">Classe</th><th /></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {visiveis.map((p) => (
                <tr key={p.id}>
                  <td className="py-2">{p.nome}</td>
                  <td className="py-2 text-slate-600">{rotuloTipo(p.tipo)}</td>
                  <td className="py-2 text-slate-600">{p.classe}</td>
                  <td className="py-2 text-right whitespace-nowrap">
                    <button onClick={() => setForm(p)} className="mr-3 text-blue-700 hover:underline">Editar</button>
                    <button onClick={() => remover(p)} className="text-red-600 hover:underline">Remover</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------- Áreas
function AbaAreas() {
  const areas = useCarregar(() => db.listarAreas());
  const [nova, setNova] = useState<Area>({ area: "", numero_usuarios: 0 });
  const [msg, setMsg] = useState<string | null>(null);

  async function salvar(a: Area) {
    await db.salvarArea(a);
    setMsg(`"${a.area}" salva.`);
    areas.recarregar();
  }

  return (
    <Card titulo="Áreas do restaurante" className="max-w-2xl">
      {msg && <div className="mb-3"><Aviso tipo="sucesso">{msg}</Aviso></div>}
      <table className="w-full text-sm">
        <thead className="text-left text-xs uppercase text-slate-500">
          <tr><th className="py-2">Área</th><th className="py-2">Nº de usuários</th><th /></tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {(areas.dados ?? []).map((a) => <LinhaArea key={a.area} area={a} aoSalvar={salvar} />)}
          <tr>
            <td className="py-2 pr-3"><Input placeholder="Nova área" value={nova.area} onChange={(e) => setNova({ ...nova, area: e.target.value })} /></td>
            <td className="py-2 pr-3"><Input type="number" min={0} value={nova.numero_usuarios} onChange={(e) => setNova({ ...nova, numero_usuarios: Number(e.target.value) })} /></td>
            <td className="py-2 text-right"><Button disabled={!nova.area} onClick={() => { salvar(nova); setNova({ area: "", numero_usuarios: 0 }); }}>Adicionar</Button></td>
          </tr>
        </tbody>
      </table>
    </Card>
  );
}

function LinhaArea({ area, aoSalvar }: { area: Area; aoSalvar: (a: Area) => void }) {
  const [n, setN] = useState(area.numero_usuarios);
  return (
    <tr>
      <td className="py-2 pr-3 font-medium">{area.area}</td>
      <td className="py-2 pr-3"><Input type="number" min={0} value={n} onChange={(e) => setN(Number(e.target.value))} /></td>
      <td className="py-2 text-right">
        <Button variante="secundario" disabled={n === area.numero_usuarios} onClick={() => aoSalvar({ ...area, numero_usuarios: n })}>Salvar</Button>
      </td>
    </tr>
  );
}

// ---------------------------------------------------------------- Calendário
function AbaCalendario() {
  const [mes, setMes] = useState(hoje().slice(0, 7)); // YYYY-MM
  const [ano, m] = mes.split("-").map(Number);
  const inicio = `${mes}-01`;
  const fim = paraISO(new Date(ano, m, 0)); // último dia do mês

  const dias = useCarregar(() => db.listarCalendario(inicio, fim), [mes]);
  const [alterados, setAlterados] = useState<Record<string, DiaCalendario>>({});
  const [msg, setMsg] = useState<string | null>(null);

  const atual = (d: DiaCalendario) => alterados[d.data] ?? d;
  const alternar = (d: DiaCalendario, campo: "letivo" | "feriado" | "ferias") =>
    setAlterados({ ...alterados, [d.data]: { ...atual(d), [campo]: !atual(d)[campo] } });

  async function salvar() {
    await db.salvarDias(Object.values(alterados));
    setMsg(`${Object.keys(alterados).length} dia(s) atualizado(s).`);
    setAlterados({});
    dias.recarregar();
  }

  return (
    <Card>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <Campo rotulo="Mês"><Input type="month" value={mes} onChange={(e) => { setMes(e.target.value); setAlterados({}); setMsg(null); }} /></Campo>
        <Button onClick={salvar} disabled={!Object.keys(alterados).length}>Salvar alterações</Button>
      </div>
      {msg && <div className="mb-3"><Aviso tipo="sucesso">{msg}</Aviso></div>}
      <p className="mb-3 text-xs text-slate-500">
        Os campos derivados (véspera de feriado, dias até as férias etc.) são calculados pelo backend a partir destas marcações.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase text-slate-500">
            <tr><th className="py-2">Dia</th><th className="py-2 text-center">Letivo</th><th className="py-2 text-center">Feriado</th><th className="py-2 text-center">Férias</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {(dias.dados ?? []).map((d) => {
              const v = atual(d);
              return (
                <tr key={d.data} className={alterados[d.data] ? "bg-amber-50" : ""}>
                  <td className="py-1.5">{formatarCurto(d.data)}</td>
                  {(["letivo", "feriado", "ferias"] as const).map((campo) => (
                    <td key={campo} className="py-1.5 text-center">
                      <input type="checkbox" className="h-4 w-4 accent-blue-700" checked={v[campo]} onChange={() => alternar(d, campo)} />
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
