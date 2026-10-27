import { useCallback, useEffect, useState } from "react";

/** Executa uma função assíncrona e guarda dados, erro e estado de carregamento. */
export function useCarregar<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [dados, setDados] = useState<T | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const recarregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      setDados(await fn());
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregando(false);
    }
  }, deps);

  useEffect(() => { recarregar(); }, [recarregar]);

  return { dados, erro, carregando, recarregar, setDados };
}
