import { useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../lib/api";
import { db } from "../lib/db";
import { formatarCurto, hoje, somarDias } from "../lib/datas";
import { useCarregar } from "../lib/useCarregar";
import { Aviso, Button, Campo, Card, Input, PageHeader, Select } from "../components/ui";
import type { Previsao as TPrevisao } from "../types";

export default function Previsao() {
  const [filtro, setFiltro] = useState({ data_inicio: hoje(), data_fim: somarDias(hoje(), 13), area: "Área 1" });
  const [consulta, setConsulta] = useState(filtro);

  const areas = useCarregar(() => db.listarAreas());
  const previsao = useCarregar(() => api.previsao(consulta), [consulta]);

  const linhas = agruparPorDia(previsao.dados ?? []);

  return (
    <>
      <PageHeader
        titulo="Previsão de demanda"
        descricao="Número estimado de refeições por dia e horário."
        acoes={<Button variante="secundario" onClick={() => exportarCsv(previsao.dados ?? [])} disabled={!previsao.dados?.length}>Exportar CSV</Button>}
      />

      <Card className="mb-6">
        <form
          className="grid gap-4 sm:grid-cols-4 sm:items-end"
          onSubmit={(e) => { e.preventDefault(); setConsulta({ ...filtro }); }}
        >
          <Campo rotulo="Área">
            <Select value={filtro.area} onChange={(e) => setFiltro({ ...filtro, area: e.target.value })}>
              {(areas.dados ?? []).map((a) => <option key={a.area}>{a.area}</option>)}
            </Select>
          </Campo>
          <Campo rotulo="De">
            <Input type="date" value={filtro.data_inicio} onChange={(e) => setFiltro({ ...filtro, data_inicio: e.target.value })} />
          </Campo>
          <Campo rotulo="Até">
            <Input type="date" min={filtro.data_inicio} value={filtro.data_fim} onChange={(e) => setFiltro({ ...filtro, data_fim: e.target.value })} />
          </Campo>
          <Button type="submit" disabled={previsao.carregando}>{previsao.carregando ? "Calculando…" : "Atualizar"}</Button>
        </form>
      </Card>

      {previsao.erro && <div className="mb-6"><Aviso tipo="erro">{previsao.erro}</Aviso></div>}

      <Card titulo={`${consulta.area} · ${formatarCurto(consulta.data_inicio)} a ${formatarCurto(consulta.data_fim)}`} className="mb-6">
        <div className="h-80">
          <ResponsiveContainer>
            <LineChart data={linhas}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="rotulo" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} width={48} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="almoco" name="Almoço" stroke="#1d4ed8" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="jantar" name="Jantar" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card titulo="Tabela">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr><th className="py-2">Dia</th><th className="py-2 text-right">Almoço</th><th className="py-2 text-right">Jantar</th><th className="py-2 text-right">Total</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100 tabular-nums">
              {linhas.map((l) => (
                <tr key={l.data}>
                  <td className="py-2">{l.rotulo}</td>
                  <td className="py-2 text-right">{l.almoco.toLocaleString("pt-BR")}</td>
                  <td className="py-2 text-right">{l.jantar.toLocaleString("pt-BR")}</td>
                  <td className="py-2 text-right font-medium">{(l.almoco + l.jantar).toLocaleString("pt-BR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </>
  );
}

function agruparPorDia(lista: TPrevisao[]) {
  const mapa = new Map<string, { data: string; rotulo: string; almoco: number; jantar: number }>();
  for (const p of lista) {
    const linha = mapa.get(p.data) ?? { data: p.data, rotulo: formatarCurto(p.data), almoco: 0, jantar: 0 };
    linha[p.horario] = p.demanda_prevista;
    mapa.set(p.data, linha);
  }
  return [...mapa.values()].sort((a, b) => a.data.localeCompare(b.data));
}

function exportarCsv(lista: TPrevisao[]) {
  const csv = ["data,area,horario,demanda_prevista", ...lista.map((p) => `${p.data},${p.area},${p.horario},${p.demanda_prevista}`)].join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: "previsao_demanda.csv" });
  a.click();
  URL.revokeObjectURL(url);
}
