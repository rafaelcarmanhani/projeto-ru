// Componentes visuais pequenos e reutilizáveis.
// Se quiser algo mais completo depois, dá para trocar por shadcn/ui sem mudar as páginas.

import type { ButtonHTMLAttributes, ReactNode, SelectHTMLAttributes, InputHTMLAttributes } from "react";

export function PageHeader({ titulo, descricao, acoes }: { titulo: string; descricao?: string; acoes?: ReactNode }) {
  return (
    <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{titulo}</h1>
        {descricao && <p className="mt-1 text-sm text-slate-500">{descricao}</p>}
      </div>
      {acoes && <div className="flex gap-2">{acoes}</div>}
    </header>
  );
}

export function Card({ titulo, children, className = "" }: { titulo?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
      {titulo && <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">{titulo}</h2>}
      {children}
    </section>
  );
}

type Variante = "primario" | "secundario" | "perigo";
const estilos: Record<Variante, string> = {
  primario: "bg-blue-700 text-white hover:bg-blue-800 disabled:bg-blue-300",
  secundario: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 disabled:text-slate-400",
  perigo: "bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300",
};

export function Button({ variante = "primario", className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variante?: Variante }) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed ${estilos[variante]} ${className}`}
      {...props}
    />
  );
}

const campoBase = "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20";

export function Campo({ rotulo, children }: { rotulo: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-600">{rotulo}</span>
      {children}
    </label>
  );
}

export const Input = (p: InputHTMLAttributes<HTMLInputElement>) => <input {...p} className={`${campoBase} ${p.className ?? ""}`} />;
export const Select = (p: SelectHTMLAttributes<HTMLSelectElement>) => <select {...p} className={`${campoBase} ${p.className ?? ""}`} />;

export function Aviso({ tipo = "info", children }: { tipo?: "info" | "erro" | "sucesso"; children: ReactNode }) {
  const cor = { info: "bg-blue-50 text-blue-800 border-blue-200", erro: "bg-red-50 text-red-800 border-red-200", sucesso: "bg-emerald-50 text-emerald-800 border-emerald-200" }[tipo];
  return <div className={`rounded-lg border px-4 py-3 text-sm ${cor}`}>{children}</div>;
}

export function Kpi({ rotulo, valor, detalhe }: { rotulo: string; valor: ReactNode; detalhe?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{rotulo}</p>
      <p className="mt-2 text-3xl font-semibold tabular-nums text-slate-900">{valor}</p>
      {detalhe && <p className="mt-1 text-xs text-slate-500">{detalhe}</p>}
    </div>
  );
}
