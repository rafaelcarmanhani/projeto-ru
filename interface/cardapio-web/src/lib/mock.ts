// Dados falsos para o modo demonstração. Pode apagar quando o backend estiver pronto.

import type {
  Area, Cardapio, DiaCalendario, Horario, JobRetreino, Prato, Previsao, StatusModelo,
} from "../types";
import { listarDias } from "./datas";

const espera = (ms = 400) => new Promise((r) => setTimeout(r, ms));

export const pratos: Prato[] = [
  { id: 1, nome: "Frango grelhado", classe: "frango", tipo: "prato_principal_1", descricao: "" },
  { id: 2, nome: "Carne de panela", classe: "carne vermelha", tipo: "prato_principal_1", descricao: "" },
  { id: 3, nome: "Strogonoff de frango", classe: "frango", tipo: "prato_principal_1", descricao: "" },
  { id: 4, nome: "Peixe empanado", classe: "peixe", tipo: "prato_principal_1", descricao: "" },
  { id: 5, nome: "Feijoada", classe: "suíno", tipo: "prato_principal_1", descricao: "" },
  { id: 6, nome: "Almôndegas ao sugo", classe: "carne vermelha", tipo: "prato_principal_1", descricao: "" },
  { id: 7, nome: "Omelete de legumes", classe: "ovo", tipo: "prato_principal_2", descricao: "" },
  { id: 8, nome: "Hambúrguer de grão-de-bico", classe: "leguminosa", tipo: "prato_principal_2", descricao: "" },
  { id: 9, nome: "Lasanha de berinjela", classe: "massa", tipo: "prato_principal_2", descricao: "" },
  { id: 10, nome: "Quibe de abóbora", classe: "legume", tipo: "prato_principal_2", descricao: "" },
  { id: 11, nome: "Farofa", classe: "farinha", tipo: "guarnicao", descricao: "" },
  { id: 12, nome: "Purê de batata", classe: "tubérculo", tipo: "guarnicao", descricao: "" },
  { id: 13, nome: "Legumes refogados", classe: "legume", tipo: "guarnicao", descricao: "" },
  { id: 14, nome: "Polenta", classe: "milho", tipo: "guarnicao", descricao: "" },
  { id: 15, nome: "Fruta da época", classe: "fruta", tipo: "sobremesa_1", descricao: "" },
  { id: 16, nome: "Gelatina", classe: "doce", tipo: "sobremesa_1", descricao: "" },
  { id: 17, nome: "Doce de leite", classe: "doce", tipo: "sobremesa_1", descricao: "" },
  { id: 18, nome: "Pudim", classe: "doce", tipo: "sobremesa_1", descricao: "" },
];

export const areas: Area[] = [
  { area: "Área 1", numero_usuarios: 14000 },
  { area: "Área 2", numero_usuarios: 5000 },
];

export const calendario = new Map<string, DiaCalendario>();
export const cardapiosSalvos = new Map<string, Cardapio>();

/** Número pseudoaleatório estável a partir de um texto (mesma data → mesmo valor). */
function ruido(semente: string): number {
  let h = 2166136261;
  for (const c of semente) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return ((h >>> 0) % 1000) / 1000;
}

export async function previsao(p: { data_inicio: string; data_fim: string; area: string }): Promise<Previsao[]> {
  await espera();
  const base = p.area === "Área 2" ? 900 : 1900;
  const resultado: Previsao[] = [];
  for (const data of listarDias(p.data_inicio, p.data_fim)) {
    const dia = new Date(data + "T12:00:00").getDay(); // 0 = domingo
    const fatorDia = dia === 0 ? 0.25 : dia === 6 ? 0.35 : dia === 5 ? 0.8 : 1;
    const cal = calendario.get(data);
    const fatorCal = cal?.feriado ? 0.2 : cal?.ferias ? 0.4 : 1;
    for (const horario of ["almoco", "jantar"] as Horario[]) {
      const fatorHorario = horario === "almoco" ? 1 : 0.45;
      const variacao = 0.9 + ruido(data + horario + p.area) * 0.2;
      resultado.push({
        data, area: p.area, horario,
        demanda_prevista: Math.round(base * fatorDia * fatorCal * fatorHorario * variacao),
      });
    }
  }
  return resultado;
}

export async function gerarCardapio(p: { data_inicio: string; data_fim: string; area: string; horario: Horario }): Promise<Cardapio[]> {
  await espera(700);
  const doTipo = (t: Prato["tipo"]) => pratos.filter((x) => x.tipo === t);
  const escolher = (lista: Prato[], semente: string) => lista[Math.floor(ruido(semente) * lista.length)].id;
  return listarDias(p.data_inicio, p.data_fim).map((data) => ({
    data, horario: p.horario, area: p.area,
    prato_principal_1: escolher(doTipo("prato_principal_1"), data + "p1" + p.horario),
    prato_principal_2: escolher(doTipo("prato_principal_2"), data + "p2" + p.horario),
    guarnicao: escolher(doTipo("guarnicao"), data + "g" + p.horario),
    sobremesa_1: escolher(doTipo("sobremesa_1"), data + "s" + p.horario),
  }));
}

let ultimoTreino = new Date(Date.now() - 12 * 86400000).toISOString();
const jobs = new Map<string, number>(); // job_id → instante de início

export async function statusModelo(): Promise<StatusModelo> {
  await espera(200);
  return { ultimo_treino: ultimoTreino, metricas: { mae: 87.4, mape: 6.2 } };
}

export async function iniciarRetreino(): Promise<JobRetreino> {
  await espera(200);
  const job_id = "demo-" + Date.now();
  jobs.set(job_id, Date.now());
  return { job_id, status: "na_fila", progresso: 0 };
}

export async function statusRetreino(jobId: string): Promise<JobRetreino> {
  await espera(150);
  const inicio = jobs.get(jobId) ?? Date.now();
  const progresso = Math.min(100, Math.round(((Date.now() - inicio) / 8000) * 100));
  if (progresso >= 100) {
    ultimoTreino = new Date().toISOString();
    return { job_id: jobId, status: "concluido", progresso: 100, mensagem: "Modelo atualizado." };
  }
  return { job_id: jobId, status: "em_andamento", progresso };
}
