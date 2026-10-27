// Acesso direto às tabelas do Supabase (CRUD da base).
// As regras de quem pode escrever ficam no próprio Supabase (RLS), ver supabase/schema.sql.
// Sem Supabase configurado, lê e grava nos dados em memória de mock.ts.

import { supabase } from "./supabase";
import * as mock from "./mock";
import { listarDias } from "./datas";
import type { Area, Cardapio, DiaCalendario, Horario, Prato } from "../types";

function checar<T>(r: { data: T | null; error: { message: string } | null }): T {
  if (r.error) throw new Error(r.error.message);
  return r.data as T;
}

const chaveCardapio = (c: Pick<Cardapio, "data" | "horario" | "area">) => `${c.data}|${c.horario}|${c.area}`;

export const db = {
  // ---------- Pratos ----------
  async listarPratos(): Promise<Prato[]> {
    if (!supabase) return [...mock.pratos];
    return checar(await supabase.from("pratos").select("*").order("nome"));
  },

  async salvarPrato(p: Omit<Prato, "id"> & { id?: number }): Promise<void> {
    if (!supabase) {
      if (p.id) Object.assign(mock.pratos.find((x) => x.id === p.id)!, p);
      else mock.pratos.push({ ...p, id: Math.max(0, ...mock.pratos.map((x) => x.id)) + 1 });
      return;
    }
    checar(await supabase.from("pratos").upsert(p));
  },

  async removerPrato(id: number): Promise<void> {
    if (!supabase) {
      mock.pratos.splice(mock.pratos.findIndex((x) => x.id === id), 1);
      return;
    }
    checar(await supabase.from("pratos").delete().eq("id", id));
  },

  // ---------- Áreas ----------
  async listarAreas(): Promise<Area[]> {
    if (!supabase) return [...mock.areas];
    return checar(await supabase.from("areas").select("*").order("area"));
  },

  async salvarArea(a: Area): Promise<void> {
    if (!supabase) {
      const existente = mock.areas.find((x) => x.area === a.area);
      if (existente) existente.numero_usuarios = a.numero_usuarios;
      else mock.areas.push(a);
      return;
    }
    checar(await supabase.from("areas").upsert(a));
  },

  // ---------- Calendário (entidade DATA) ----------
  async listarCalendario(inicio: string, fim: string): Promise<DiaCalendario[]> {
    if (!supabase) {
      return listarDias(inicio, fim).map((data) => {
        const dia = new Date(data + "T12:00:00").getDay();
        return mock.calendario.get(data) ?? { data, letivo: dia !== 0 && dia !== 6, feriado: false, ferias: false };
      });
    }
    return checar(await supabase.from("calendario").select("*").gte("data", inicio).lte("data", fim).order("data"));
  },

  async salvarDias(dias: DiaCalendario[]): Promise<void> {
    if (!supabase) {
      dias.forEach((d) => mock.calendario.set(d.data, d));
      return;
    }
    checar(await supabase.from("calendario").upsert(dias));
  },

  // ---------- Cardápios ----------
  async listarCardapios(inicio: string, fim: string, area: string, horario?: Horario): Promise<Cardapio[]> {
    if (!supabase) {
      return [...mock.cardapiosSalvos.values()].filter(
        (c) => c.data >= inicio && c.data <= fim && c.area === area && (!horario || c.horario === horario),
      );
    }
    let q = supabase.from("cardapios").select("*").gte("data", inicio).lte("data", fim).eq("area", area);
    if (horario) q = q.eq("horario", horario);
    return checar(await q.order("data"));
  },

  async salvarCardapios(lista: Cardapio[]): Promise<void> {
    if (!supabase) {
      lista.forEach((c) => mock.cardapiosSalvos.set(chaveCardapio(c), c));
      return;
    }
    checar(await supabase.from("cardapios").upsert(lista, { onConflict: "data,horario,area" }));
  },
};
