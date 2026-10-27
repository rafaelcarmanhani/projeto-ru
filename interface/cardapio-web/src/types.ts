// Tipos espelhando o MER do projeto.

export type Papel = "administrador" | "usuario";

export interface Perfil {
  id: string; // = auth.users.id no Supabase
  nome: string;
  email: string;
  papel: Papel;
}

export type TipoPrato =
  | "prato_principal_1"
  | "prato_principal_2"
  | "guarnicao"
  | "sobremesa_1";

export const TIPOS_PRATO: { valor: TipoPrato; rotulo: string }[] = [
  { valor: "prato_principal_1", rotulo: "Prato principal" },
  { valor: "prato_principal_2", rotulo: "Opção vegetariana" },
  { valor: "guarnicao", rotulo: "Guarnição" },
  { valor: "sobremesa_1", rotulo: "Sobremesa" },
];

export interface Prato {
  id: number;
  nome: string;
  classe: string; // ex.: "frango", "carne vermelha", "massa"
  tipo: TipoPrato;
  descricao: string;
}

export type Horario = "almoco" | "jantar";

export const HORARIOS: { valor: Horario; rotulo: string }[] = [
  { valor: "almoco", rotulo: "Almoço" },
  { valor: "jantar", rotulo: "Jantar" },
];

export interface Area {
  area: string; // ex.: "Área 1"
  numero_usuarios: number;
}

/** Entidade DATA do MER. Os campos derivados (véspera, dias até feriado…)
 *  são calculados no backend a partir de letivo/feriado/ferias. */
export interface DiaCalendario {
  data: string; // YYYY-MM-DD
  letivo: boolean;
  feriado: boolean;
  ferias: boolean;
}

/** Um cardápio = uma data + horário + área, com um prato por "slot".
 *  Cada slot guarda o id do prato (FK para pratos). */
export interface Cardapio {
  data: string;
  horario: Horario;
  area: string;
  prato_principal_1: number | null;
  prato_principal_2: number | null;
  guarnicao: number | null;
  sobremesa_1: number | null;
}

export interface Previsao {
  data: string;
  area: string;
  horario: Horario;
  demanda_prevista: number;
}

export interface StatusModelo {
  ultimo_treino: string | null; // ISO
  metricas: { mae?: number; mape?: number; [k: string]: number | undefined };
}

export type EstadoJob = "na_fila" | "em_andamento" | "concluido" | "erro";

export interface JobRetreino {
  job_id: string;
  status: EstadoJob;
  progresso?: number; // 0–100
  mensagem?: string;
}
