import { useState } from "react";
import { api } from "../lib/api";
import { db } from "../lib/db";
import { formatarCurto, hoje, somarDias } from "../lib/datas";
import { useCarregar } from "../lib/useCarregar";
import { Aviso, Button, Campo, Card, Input, PageHeader, Select } from "../components/ui";
import { HORARIOS, TIPOS_PRATO, type Cardapio, type Horario, type TipoPrato } from "../types";

export default function GerarCardapio() {
  const [params, setParams] = useState({
    data_inicio: somarDias(hoje(), 1),
    data_fim: somarDias(hoje(), 5),
    area: "Área 1",
    horario: "almoco" as Horario,
  });
  const [cardapios, setCardapios] = useState<Cardapio[]>([]);
  const [gerando, setGerando] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [msg, setMsg] = useState<{ tipo: "erro" | "sucesso"; texto: string } | null>(null);

  const areas = useCarregar(() => db.listarAreas());
  const pratos = useCarregar(() => db.listarPratos());
  const porTipo = (t: TipoPrato) => (pratos.dados ?? []).filter((p) => p.tipo === t);

  async function gerar() {
    setMsg(null);
    setGerando(true);
    try {
      setCardapios(await api.gerarCardapio(params));
    } catch (e) {
      setMsg({ tipo: "erro", texto: e instanceof Error ? e.message : "Falha ao gerar." });
    } finally {
      setGerando(false);
    }
  }

  async function salvar() {
    setMsg(null);
    setSalvando(true);
    try {
      await db.salvarCardapios(cardapios);
      setMsg({ tipo: "sucesso", texto: `${cardapios.length} cardápio(s) salvo(s).` });
    } catch (e) {
      setMsg({ tipo: "erro", texto: e instanceof Error ? e.message : "Falha ao salvar." });
    } finally {
      setSalvando(false);
    }
  }

  function trocar(indice: number, tipo: TipoPrato, pratoId: number) {
    setCardapios((lista) => lista.map((c, i) => (i === indice ? { ...c, [tipo]: pratoId } : c)));
  }

  return (
    <>
      <PageHeader titulo="Gerar cardápio" descricao="O otimizador sugere os pratos; você pode ajustar antes de salvar." />

      <Card className="mb-6">
        <form className="grid gap-4 sm:grid-cols-5 sm:items-end" onSubmit={(e) => { e.preventDefault(); gerar(); }}>
          <Campo rotulo="Área">
            <Select value={params.area} onChange={(e) => setParams({ ...params, area: e.target.value })}>
              {(areas.dados ?? []).map((a) => <option key={a.area}>{a.area}</option>)}
            </Select>
          </Campo>
          <Campo rotulo="Horário">
            <Select value={params.horario} onChange={(e) => setParams({ ...params, horario: e.target.value as Horario })}>
              {HORARIOS.map((h) => <option key={h.valor} value={h.valor}>{h.rotulo}</option>)}
            </Select>
          </Campo>
          <Campo rotulo="De">
            <Input type="date" value={params.data_inicio} onChange={(e) => setParams({ ...params, data_inicio: e.target.value })} />
          </Campo>
          <Campo rotulo="Até">
            <Input type="date" min={params.data_inicio} value={params.data_fim} onChange={(e) => setParams({ ...params, data_fim: e.target.value })} />
          </Campo>
          <Button type="submit" disabled={gerando}>{gerando ? "Gerando…" : "Gerar sugestão"}</Button>
        </form>
      </Card>

      {msg && <div className="mb-6"><Aviso tipo={msg.tipo}>{msg.texto}</Aviso></div>}

      {cardapios.length > 0 && (
        <Card titulo="Sugestão">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="text-left text-xs uppercase text-slate-500">
                <tr>
                  <th className="py-2 pr-3">Dia</th>
                  {TIPOS_PRATO.map((t) => <th key={t.valor} className="py-2 pr-3">{t.rotulo}</th>)}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {cardapios.map((c, i) => (
                  <tr key={c.data}>
                    <td className="py-2 pr-3 font-medium whitespace-nowrap">{formatarCurto(c.data)}</td>
                    {TIPOS_PRATO.map((t) => (
                      <td key={t.valor} className="py-2 pr-3">
                        <Select value={c[t.valor] ?? ""} onChange={(e) => trocar(i, t.valor, Number(e.target.value))}>
                          {porTipo(t.valor).map((p) => <option key={p.id} value={p.id}>{p.nome}</option>)}
                        </Select>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <Button variante="secundario" onClick={gerar} disabled={gerando}>Gerar de novo</Button>
            <Button onClick={salvar} disabled={salvando}>{salvando ? "Salvando…" : "Salvar cardápios"}</Button>
          </div>
        </Card>
      )}
    </>
  );
}
