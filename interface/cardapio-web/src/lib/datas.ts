// Utilitários de datas no formato YYYY-MM-DD (sem fuso, para evitar surpresas).

export function hoje(): string {
  return paraISO(new Date());
}

export function paraISO(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const dia = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${dia}`;
}

export function somarDias(iso: string, n: number): string {
  const d = new Date(iso + "T12:00:00");
  d.setDate(d.getDate() + n);
  return paraISO(d);
}

export function listarDias(inicio: string, fim: string): string[] {
  const dias: string[] = [];
  for (let d = inicio; d <= fim && dias.length < 366; d = somarDias(d, 1)) dias.push(d);
  return dias;
}

const fmtCurto = new Intl.DateTimeFormat("pt-BR", { weekday: "short", day: "2-digit", month: "2-digit" });
const fmtLongo = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "numeric", month: "long" });

export const formatarCurto = (iso: string) => fmtCurto.format(new Date(iso + "T12:00:00"));
export const formatarLongo = (iso: string) => fmtLongo.format(new Date(iso + "T12:00:00"));
