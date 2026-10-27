import { Route, Routes } from "react-router";
import { RequireAuth } from "./auth/RequireAuth";
import { Layout } from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Previsao from "./pages/Previsao";
import GerarCardapio from "./pages/GerarCardapio";
import BaseDados from "./pages/BaseDados";
import Modelo from "./pages/Modelo";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RequireAuth><Layout /></RequireAuth>}>
        <Route index element={<Dashboard />} />
        <Route path="previsao" element={<Previsao />} />
        <Route path="cardapio" element={<RequireAuth papel="administrador"><GerarCardapio /></RequireAuth>} />
        <Route path="base" element={<RequireAuth papel="administrador"><BaseDados /></RequireAuth>} />
        <Route path="modelo" element={<RequireAuth papel="administrador"><Modelo /></RequireAuth>} />
        <Route path="*" element={<p className="text-slate-500">Página não encontrada.</p>} />
      </Route>
    </Routes>
  );
}
