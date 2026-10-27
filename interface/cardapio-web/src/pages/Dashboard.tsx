import { useState } from "react";
import { Link } from "react-router";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { db } from "../lib/db";
import { formatarCurto, formatarLongo, hoje, somarDias } from "../lib/datas";
import { useCarregar } from "../lib/useCarregar";
import { Aviso, Card, Kpi, PageHeader, Select } from "../components/ui";
import { HORARIOS, TIPOS_PRATO, type Prato } from "../types";

export default function Dashboard() {
  const { perfil } = useAuth();
  const [area, setArea] = useState("Área 1");
  const dataHoje = hoje();
  const fimSemana = somarDias(dataHoje, 6);

  const areas = useCarregar(() => db.listarAreas());
  const previsao = useCarregar(() => api.previsao({ data_inicio: dataHoje, data_fim: fimSemana, area }), [area]);
  const pratos = useCarregar(() => db.listarPratos());
  const cardapiosHoje = useCarregar(() => db.listarCardapios(dataHoje, dataHoje, area), [area]);

  const nomePrato = (id: number | null) => pratos.dados?.find((p: Prato) => p.id === id)?.nome ?? "—";
  const deHoje = previsao.dados?.filter((p) => p.data === dataHoje) ?? [];
  const almocoHoje = deHoje.find((p) => p.horario === "almoco")?.demanda_prevista;
  const jantarHoje = deHoje.find((p) => p.horario === "jantar")?.demanda_prevista;
  const totalSemana = previsao.dados?.reduce((s, p) => s + p.demanda_prevista, 0);

  // Agrupa por dia para o gráfico (almoço e jantar lado a lado)
  const grafico = Object.values(
    (previsao.dados ?? []).reduce<Record<string, { dia: string; almoco: number; jantar: number }>>((acc, p) => {
      acc[p.data] ??= { dia: formatarCurto(p.data), almoco: 0, jantar: 0 };
      acc[p.data][p.horario] = p.demanda_prevista;
      return acc;
    }, {}),
  );

  return (
    <>
      <PageHeader
        titulo={`Olá, ${perfil?.nome}`}
        descricao={`Hoje é ${formatarLongo(dataHoje)}`}
        acoes={
          <Select value={area} onChange={(e) => setArea(e.target.value)} className="w-40">
            {(areas.dados ?? [{ area: "Área 1" }]).map((a) => <option key={a.area}>{a.area}</option>)}
          </Select>
        }
      />

      {previsao.erro && <div className="mb-4"><Aviso tipo="erro">{previsao.erro}</Aviso></div>}

      <div className="grid gap-4 sm:grid-cols-3">
        <Kpi rotulo="Almoço hoje (previsto)" valor={almocoHoje?.toLocaleString("pt-BR") ?? "…"} detalhe="refeições" />
        <Kpi rotulo="Jantar hoje (previsto)" valor={jantarHoje?.toLocaleString("pt-BR") ?? "…"} detalhe="refeições" />
        <Kpi rotulo="Próximos 7 dias" valor={totalSemana?.toLocaleString("pt-BR") ?? "…"} detalhe="refeições no total" />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-5">
        <Card titulo="Demanda prevista · próximos 7 dias" className="lg:col-span-3">
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={grafico}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="dia" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} width={48} />
                <Tooltip />
                <Bar dataKey="almoco" name="Almoço" fill="#1d4ed8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="jantar" name="Jantar" fill="#93c5fd" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <Link to="/previsao" className="mt-2 inline-block text-sm font-medium text-blue-700 hover:underline">Ver previsão detalhada →</Link>
        </Card>

        <Card titulo="Cardápio de hoje" className="lg:col-span-2">
          {HORARIOS.map((h) => {
            const c = cardapiosHoje.dados?.find((x) => x.horario === h.valor);
            return (
              <div key={h.valor} className="mb-4 last:mb-0">
                <p className="mb-1 text-sm font-semibold text-slate-800">{h.rotulo}</p>
                {c ? (
                  <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
                    {TIPOS_PRATO.map((t) => (
                      <div key={t.valor} className="contents">
                        <dt className="text-slate-500">{t.rotulo}</dt>
                        <dd className="text-slate-800">{nomePrato(c[t.valor])}</dd>
                      </div>
                    ))}
                  </dl>
                ) : (
                  <p className="text-sm text-slate-400">
                    Ainda não definido.{" "}
                    {perfil?.papel === "administrador" && <Link to="/cardapio" className="text-blue-700 hover:underline">Gerar agora</Link>}
                  </p>
                )}
              </div>
            );
          })}
        </Card>
      </div>
    </>
  );
}
