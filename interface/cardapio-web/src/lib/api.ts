// Cliente da API FastAPI (previsão de demanda, geração de cardápio, retreino).
// Sem VITE_API_URL, usa as funções de mock para a interface funcionar sozinha.

import { getAccessToken } from "./supabase";
import * as mock from "./mock";
import type { Cardapio, Horario, JobRetreino, Previsao, StatusModelo } from "../types";

const API_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "");
export const API_DEMO = !API_URL;

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await getAccessToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!res.ok) {
    const detalhe = await res.text().catch(() => "");
    throw new Error(`Erro ${res.status} em ${path}${detalhe ? `: ${detalhe}` : ""}`);
  }
  return res.json() as Promise<T>;
}

export interface ParamsPeriodo {
  data_inicio: string; // YYYY-MM-DD
  data_fim: string;
  area: string;
}

export const api = {
  /** POST /previsao → demanda prevista por dia e horário */
  previsao(p: ParamsPeriodo): Promise<Previsao[]> {
    if (API_DEMO) return mock.previsao(p);
    return request("/previsao", { method: "POST", body: JSON.stringify(p) });
  },

  /** POST /cardapio/gerar → sugestão de cardápios para o período */
  gerarCardapio(p: ParamsPeriodo & { horario: Horario }): Promise<Cardapio[]> {
    if (API_DEMO) return mock.gerarCardapio(p);
    return request("/cardapio/gerar", { method: "POST", body: JSON.stringify(p) });
  },

  /** GET /modelo/status → data do último treino e métricas */
  statusModelo(): Promise<StatusModelo> {
    if (API_DEMO) return mock.statusModelo();
    return request("/modelo/status");
  },

  /** POST /modelo/retreino → inicia o retreino em segundo plano */
  iniciarRetreino(): Promise<JobRetreino> {
    if (API_DEMO) return mock.iniciarRetreino();
    return request("/modelo/retreino", { method: "POST" });
  },

  /** GET /modelo/retreino/{job_id} → acompanha o progresso */
  statusRetreino(jobId: string): Promise<JobRetreino> {
    if (API_DEMO) return mock.statusRetreino(jobId);
    return request(`/modelo/retreino/${encodeURIComponent(jobId)}`);
  },
};
