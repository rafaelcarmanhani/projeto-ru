import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useCarregar } from "../lib/useCarregar";
import { Aviso, Button, Card, Kpi, PageHeader } from "../components/ui";
import type { JobRetreino } from "../types";

const fmtDataHora = new Intl.DateTimeFormat("pt-BR", { dateStyle: "long", timeStyle: "short" });

export default function Modelo() {
  const status = useCarregar(() => api.statusModelo());
  const [job, setJob] = useState<JobRetreino | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const rodando = job?.status === "na_fila" || job?.status === "em_andamento";

  // Enquanto o retreino roda, consulta o status a cada 2 segundos.
  useEffect(() => {
    if (!job || !rodando) return;
    const t = setInterval(async () => {
      try {
        const novo = await api.statusRetreino(job.job_id);
        setJob(novo);
        if (novo.status === "concluido") status.recarregar();
      } catch (e) {
        setErro(e instanceof Error ? e.message : "Falha ao consultar o retreino.");
      }
    }, 2000);
    return () => clearInterval(t);
  }, [job?.job_id, rodando]); // eslint-disable-line react-hooks/exhaustive-deps

  async function iniciar() {
    if (!confirm("Refazer o treino do modelo com os dados atuais da base?")) return;
    setErro(null);
    try {
      setJob(await api.iniciarRetreino());
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Falha ao iniciar o retreino.");
    }
  }

  const s = status.dados;

  return (
    <>
      <PageHeader titulo="Modelo e retreino" descricao="Acompanhe o modelo de previsão e treine novamente quando a base mudar." />

      <div className="grid gap-4 sm:grid-cols-3">
        <Kpi rotulo="Último treino" valor={<span className="text-lg">{s?.ultimo_treino ? fmtDataHora.format(new Date(s.ultimo_treino)) : "—"}</span>} />
        <Kpi rotulo="MAE" valor={s?.metricas.mae?.toFixed(1) ?? "—"} detalhe="erro médio absoluto (refeições)" />
        <Kpi rotulo="MAPE" valor={s?.metricas.mape != null ? `${s.metricas.mape.toFixed(1)}%` : "—"} detalhe="erro percentual médio" />
      </div>

      <Card titulo="Refazer treino" className="mt-6 max-w-2xl">
        <p className="mb-4 text-sm text-slate-600">
          O retreino roda em segundo plano na API. Você pode sair desta página; o andamento continua no servidor.
        </p>
        {erro && <div className="mb-4"><Aviso tipo="erro">{erro}</Aviso></div>}
        {job && (
          <div className="mb-4">
            <div className="mb-1 flex justify-between text-xs text-slate-600">
              <span>{{ na_fila: "Na fila", em_andamento: "Treinando…", concluido: "Concluído", erro: "Erro" }[job.status]}</span>
              <span className="tabular-nums">{job.progresso ?? 0}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className={`h-full transition-all ${job.status === "erro" ? "bg-red-500" : job.status === "concluido" ? "bg-emerald-500" : "bg-blue-600"}`}
                style={{ width: `${job.progresso ?? 0}%` }}
              />
            </div>
            {job.mensagem && <p className="mt-2 text-xs text-slate-500">{job.mensagem}</p>}
          </div>
        )}
        <Button onClick={iniciar} disabled={rodando}>{rodando ? "Retreino em andamento…" : "Refazer treino"}</Button>
      </Card>
    </>
  );
}
