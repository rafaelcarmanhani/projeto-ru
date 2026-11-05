# ------------------------ RELATÓRIO VISUAL DO CARDÁPIO ------------------------
#
# Gera uma página HTML autocontida (sem dependências, abre offline) com o
# cardápio otimizado em formato de calendário, para apresentar ao time. Salva
# também os mesmos dados em JSON, para quem quiser reaproveitar o resultado
# sem rodar o modelo de novo.
#
# O otimizacao.py monta o dicionário `resultado` com os itens escolhidos e
# chama gerar_relatorio(). As métricas (PEN1, PEN2, BON1) são recalculadas
# aqui a partir do cardápio final, e não lidas das variáveis do modelo: assim
# o relatório mostra o que de fato saiu, independente de folgas e pesos.

import json
import webbrowser
from datetime import datetime
from pathlib import Path

PP1 = "prato_principal_1"
PP2 = "prato_principal_2"


def _slots(resultado):
    """Refeições principais em ordem cronológica: [(dia, refeicao, itens)]."""
    return [
        (dia["dia"], ref["refeicao"], ref["itens"])
        for dia in resultado["dias"]
        for ref in dia["refeicoes"]
        if ref["refeicao"] != "Desjejum"
    ]


def _item_da_categoria(itens, categoria):
    for item in itens:
        if item["categoria"] == categoria:
            return item
    return None


def calcular_metricas(resultado):
    slots = _slots(resultado)
    preparos_pen = set(resultado["preparos_penalizados"])
    alcance = resultado["parametros"]["ALCANCE_PEN"]

    popularidade = sum(
        item["S"]
        for dia in resultado["dias"]
        for ref in dia["refeicoes"]
        for item in ref["itens"]
    )

    inversoes, casados = [], []
    presenca = []
    colisoes_mesma_refeicao = 0

    for dia, refeicao, itens in slots:
        pp1 = _item_da_categoria(itens, PP1)
        pp2 = _item_da_categoria(itens, PP2)

        casado = None
        if pp1 and pp2:
            diferenca = pp2["P"] - pp1["P"]
            if diferenca > 0:
                inversoes.append({
                    "dia": dia, "refeicao": refeicao,
                    "pp1": pp1["nome"], "P1": pp1["P"],
                    "pp2": pp2["nome"], "P2": pp2["P"],
                    "diferenca": round(diferenca, 2),
                })
            if pp1["preparo"] and pp1["preparo"] == pp2["preparo"]:
                casado = pp1["preparo"]
                casados.append({
                    "dia": dia, "refeicao": refeicao,
                    "pp1": pp1["nome"], "pp2": pp2["nome"],
                    "preparo": casado,
                })

        # Mesma refeição: o par pp1/pp2 casado é desejado (BON1); o que
        # passar dele é colisão, como no PEN1.
        contagem = {}
        for item in itens:
            if item["preparo"] in preparos_pen:
                contagem[item["preparo"]] = contagem.get(item["preparo"], 0) + 1
        for q, n in contagem.items():
            colisoes_mesma_refeicao += max(0, n - 1 - (1 if q == casado else 0))
        presenca.append(set(contagem))

    colisoes_proximas = sum(
        len(presenca[a] & presenca[b])
        for a in range(len(presenca))
        for b in range(a + 1, min(a + 1 + alcance, len(presenca)))
    )

    return {
        "popularidade": round(popularidade, 1),
        "refeicoes": len(slots),
        "desjejuns": sum(
            1 for dia in resultado["dias"]
            for ref in dia["refeicoes"] if ref["refeicao"] == "Desjejum"
        ),
        "inversoes": sorted(inversoes, key=lambda t: -t["diferenca"]),
        "casados": casados,
        "colisoes": colisoes_mesma_refeicao + colisoes_proximas,
    }


def gerar_relatorio(resultado, pasta_saida, abrir=True):
    """Salva <pasta>/cardapio_AAAA_MM.{json,html} e devolve o caminho do HTML."""
    resultado = dict(resultado)
    resultado["metricas"] = calcular_metricas(resultado)
    resultado["gerado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)
    base = pasta / f"cardapio_{resultado['ano']}_{resultado['mes']:02d}"

    dados = json.dumps(resultado, ensure_ascii=False, indent=1)
    base.with_suffix(".json").write_text(dados, encoding="utf-8")

    # "</" dentro do JSON fecharia a tag <script> antes da hora.
    html = MODELO_HTML.replace("/*__DADOS__*/", dados.replace("</", "<\\/"))
    caminho_html = base.with_suffix(".html")
    caminho_html.write_text(html, encoding="utf-8")

    if abrir:
        webbrowser.open(caminho_html.resolve().as_uri())

    return caminho_html


MODELO_HTML = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cardápio otimizado</title>
<style>
  :root {
    --bg: #f6f6f3;
    --surface: #ffffff;
    --surface-2: #fafaf8;
    --text: #1d1d1b;
    --muted: #6f6e69;
    --faint: #a3a29c;
    --border: #e7e6e1;
    --pp1: #b8532c;
    --pp2: #2f7c4e;
    --link: #2f5fd0;
    --link-soft: #ecf1fd;
    --warn: #a3650f;
    --warn-soft: #fcf2df;
    --ok: #2f7c4e;
    --shadow: 0 1px 2px rgba(20, 20, 18, .05);
    color-scheme: light;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #141413;
      --surface: #1d1d1b;
      --surface-2: #232321;
      --text: #ecebe6;
      --muted: #a09f99;
      --faint: #6d6c67;
      --border: #302f2c;
      --pp1: #e38a62;
      --pp2: #66c28c;
      --link: #86a9ff;
      --link-soft: #1f2a44;
      --warn: #e7b456;
      --warn-soft: #3a2e17;
      --ok: #66c28c;
      --shadow: none;
      color-scheme: dark;
    }
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .pagina { max-width: 1320px; margin: 0 auto; padding: 36px 28px 64px; }

  /* ---------- topo ---------- */
  .topo { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; margin-bottom: 28px; }
  .sobre { margin: 0 0 4px; color: var(--muted); font-size: 13px; letter-spacing: .02em; }
  h1 { margin: 0; font-size: 30px; font-weight: 650; letter-spacing: -.02em; }
  .meta { color: var(--muted); font-size: 13px; text-align: right; }
  .meta .status { display: inline-flex; align-items: center; gap: 6px; color: var(--text); font-weight: 550; }
  .meta .status::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--ok); }
  .meta .status.alerta::before { background: var(--warn); }

  /* ---------- indicadores ---------- */
  .kpis { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 28px; }
  .kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; box-shadow: var(--shadow); }
  .kpi .rotulo { color: var(--muted); font-size: 12.5px; }
  .kpi .valor { font-size: 26px; font-weight: 650; letter-spacing: -.02em; margin: 4px 0 2px; font-variant-numeric: tabular-nums; }
  .kpi .sub { color: var(--faint); font-size: 12px; }
  .kpi.azul .valor { color: var(--link); }
  .kpi.ambar .valor { color: var(--warn); }
  .kpi.verde .valor { color: var(--ok); }

  /* ---------- barra de controles ---------- */
  .barra { display: flex; justify-content: space-between; align-items: center; gap: 12px 20px; flex-wrap: wrap; margin-bottom: 14px; }
  .segmentado { display: inline-flex; background: var(--surface); border: 1px solid var(--border); border-radius: 9px; padding: 3px; }
  .segmentado button { border: 0; background: transparent; color: var(--muted); font: inherit; font-size: 13px; padding: 6px 14px; border-radius: 6px; cursor: pointer; }
  .segmentado button[aria-pressed="true"] { background: var(--text); color: var(--bg); }
  .legenda { display: flex; gap: 16px; flex-wrap: wrap; color: var(--muted); font-size: 12.5px; }
  .legenda span { display: inline-flex; align-items: center; gap: 6px; }
  .marca { width: 3px; height: 13px; border-radius: 2px; display: inline-block; }
  .marca.p1 { background: var(--pp1); }
  .marca.p2 { background: var(--pp2); }

  /* ---------- calendário ---------- */
  .calendario { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }
  .cab-semana { color: var(--muted); font-size: 12px; font-weight: 550; text-transform: uppercase; letter-spacing: .06em; padding: 0 4px 2px; }
  .vazio { min-height: 60px; }
  .dia {
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 12px 12px 10px; box-shadow: var(--shadow); cursor: pointer; text-align: left;
    transition: border-color .15s, transform .15s;
  }
  .dia:hover, .dia:focus-visible { border-color: var(--faint); outline: none; }
  .dia-topo { display: flex; align-items: baseline; gap: 6px; margin-bottom: 8px; }
  .dia-topo .num { font-size: 17px; font-weight: 650; font-variant-numeric: tabular-nums; }
  .dia-topo .sem { color: var(--faint); font-size: 12px; }
  .ref + .ref { margin-top: 10px; padding-top: 9px; border-top: 1px solid var(--border); }
  .ref-nome { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; font-weight: 550; }
  .prato { display: flex; align-items: baseline; gap: 8px; padding-left: 8px; border-left: 3px solid transparent; margin: 3px 0; }
  .prato.p1 { border-color: var(--pp1); font-weight: 560; }
  .prato.p2 { border-color: var(--pp2); }
  .prato .nome { flex: 1; min-width: 0; }
  .nota { color: var(--faint); font-size: 11.5px; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .extra { display: none; }
  .completo .extra { display: block; }
  .extra-linha { display: flex; gap: 6px; font-size: 12.5px; color: var(--muted); margin: 2px 0 0 11px; }
  .extra-linha .cat { color: var(--faint); flex: 0 0 62px; }
  .desjejum { font-size: 12.5px; color: var(--muted); margin-bottom: 8px; }
  .chips { display: flex; gap: 4px; flex-wrap: wrap; margin: 5px 0 0 11px; }
  .chip { font-size: 11px; border-radius: 999px; padding: 1px 8px; font-weight: 550; white-space: nowrap; }
  .chip.grupo { background: var(--link-soft); color: var(--link); }
  .chip.inv { background: var(--warn-soft); color: var(--warn); }

  /* ---------- destaques ---------- */
  .destaques { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 32px; }
  .painel { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; box-shadow: var(--shadow); }
  .painel h2 { font-size: 15px; margin: 0 0 2px; font-weight: 620; }
  .painel .explica { color: var(--muted); font-size: 12.5px; margin: 0 0 12px; }
  .lista { list-style: none; margin: 0; padding: 0; max-height: 360px; overflow-y: auto; }
  .lista li { display: grid; grid-template-columns: 104px 1fr auto; gap: 10px; align-items: baseline; padding: 7px 4px; border-top: 1px solid var(--border); cursor: pointer; border-radius: 6px; }
  .lista li:first-child { border-top: 0; }
  .lista li:hover { background: var(--surface-2); }
  .lista .quando { color: var(--muted); font-size: 12.5px; font-variant-numeric: tabular-nums; }
  .lista .vazia { color: var(--faint); cursor: default; display: block; }

  /* ---------- parâmetros ---------- */
  details.params { margin-top: 20px; color: var(--muted); font-size: 12.5px; }
  details.params summary { cursor: pointer; }
  details.params dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 16px; margin: 12px 0 0; }
  details.params dt { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--text); }
  details.params dd { margin: 0; }

  /* ---------- detalhe do dia ---------- */
  dialog { border: 1px solid var(--border); border-radius: 16px; padding: 0; width: min(560px, calc(100vw - 32px)); background: var(--surface); color: var(--text); box-shadow: 0 20px 50px rgba(0,0,0,.18); }
  dialog::backdrop { background: rgba(20, 20, 18, .35); }
  .dlg-topo { display: flex; justify-content: space-between; align-items: center; padding: 18px 22px 12px; border-bottom: 1px solid var(--border); }
  .dlg-topo h3 { margin: 0; font-size: 18px; font-weight: 640; }
  .fechar { border: 0; background: transparent; color: var(--muted); font-size: 22px; line-height: 1; cursor: pointer; padding: 4px 8px; border-radius: 6px; }
  .fechar:hover { background: var(--surface-2); color: var(--text); }
  .dlg-corpo { padding: 8px 22px 20px; max-height: 70vh; overflow-y: auto; }
  .dlg-ref { margin-top: 14px; }
  .dlg-ref-topo { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
  .dlg-ref-topo h4 { margin: 0; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); font-weight: 600; }
  .dlg-ref-topo .f { color: var(--faint); font-size: 12px; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 6px 0; border-top: 1px solid var(--border); vertical-align: baseline; }
  td.cat { color: var(--muted); font-size: 12.5px; width: 104px; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; color: var(--muted); font-size: 12.5px; width: 52px; }
  tr.p1 td.item { font-weight: 580; box-shadow: inset 3px 0 var(--pp1); padding-left: 10px; }
  tr.p2 td.item { box-shadow: inset 3px 0 var(--pp2); padding-left: 10px; }
  th { font-size: 11px; color: var(--faint); font-weight: 500; text-align: right; padding-bottom: 4px; }

  @media (max-width: 1100px) {
    .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  }
  @media (max-width: 760px) {
    .pagina { padding: 24px 16px 48px; }
    h1 { font-size: 24px; }
    .meta { text-align: left; }
    .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .calendario { grid-template-columns: 1fr; }
    .cab-semana, .vazio { display: none; }
    .destaques { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<main class="pagina">
  <header class="topo">
    <div>
      <p class="sobre">Otimização do cardápio · RU USP São Carlos</p>
      <h1 id="titulo"></h1>
    </div>
    <div class="meta" id="meta"></div>
  </header>

  <section class="kpis" id="kpis"></section>

  <div class="barra">
    <div class="segmentado" role="group" aria-label="Visualização">
      <button type="button" data-modo="resumo" aria-pressed="true">Pratos principais</button>
      <button type="button" data-modo="completo" aria-pressed="false">Cardápio completo</button>
    </div>
    <div class="legenda">
      <span><i class="marca p1"></i>Prato 1</span>
      <span><i class="marca p2"></i>Prato 2</span>
      <span><span class="chip grupo">mesmo grupo</span></span>
      <span><span class="chip inv">▲ prato 2 acima</span></span>
      <span>números = score P (1 a 10)</span>
    </div>
  </div>

  <section class="calendario" id="calendario"></section>

  <section class="destaques">
    <div class="painel">
      <h2 id="t-casados"></h2>
      <p class="explica">Refeições em que o prato 1 e o prato 2 são do mesmo preparo (bônus BON1).</p>
      <ul class="lista" id="l-casados"></ul>
    </div>
    <div class="painel">
      <h2 id="t-inv"></h2>
      <p class="explica">Refeições em que o prato 2 tem score maior que o prato 1 (penalização PEN2).</p>
      <ul class="lista" id="l-inv"></ul>
    </div>
  </section>

  <details class="params">
    <summary>Parâmetros desta rodada</summary>
    <dl id="params"></dl>
  </details>
</main>

<dialog id="detalhe" aria-labelledby="dlg-titulo">
  <div class="dlg-topo">
    <h3 id="dlg-titulo"></h3>
    <button class="fechar" type="button" aria-label="Fechar">×</button>
  </div>
  <div class="dlg-corpo" id="dlg-corpo"></div>
</dialog>

<script id="dados" type="application/json">/*__DADOS__*/</script>
<script>
(function () {
  var dados = JSON.parse(document.getElementById("dados").textContent);
  var met = dados.metricas;

  var MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
               "agosto", "setembro", "outubro", "novembro", "dezembro"];
  var SEM_CURTO = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"];
  var SEM_LONGO = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"];
  var REFEICAO = { Desjejum: "Desjejum", Almoco: "Almoço", Janta: "Jantar" };
  var CATEGORIA = {
    prato_principal_1: "Prato 1", prato_principal_2: "Prato 2", "guarnição": "Guarnição",
    salada_1: "Salada 1", salada_2: "Salada 2", salada_3: "Salada 3",
    sobremesa_1: "Sobremesa", sobremesa_2: "Fruta"
  };
  var ORDEM = ["prato_principal_1", "prato_principal_2", "guarnição", "salada_1",
               "salada_2", "salada_3", "sobremesa_1", "sobremesa_2"];
  var EXTRAS = ORDEM.slice(2);

  function num(v, casas) {
    return v.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
  }
  function esc(t) {
    return String(t).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function cap(t) { return t.charAt(0).toUpperCase() + t.slice(1); }

  var porDia = {};
  dados.dias.forEach(function (d) { porDia[d.dia] = d; });

  var chave = function (dia, ref) { return dia + "|" + ref; };
  var casados = {}, inversoes = {};
  met.casados.forEach(function (c) { casados[chave(c.dia, c.refeicao)] = c; });
  met.inversoes.forEach(function (c) { inversoes[chave(c.dia, c.refeicao)] = c; });

  function doCat(itens, cat) {
    for (var i = 0; i < itens.length; i++) if (itens[i].categoria === cat) return itens[i];
    return null;
  }

  // ---------- cabeçalho ----------
  document.getElementById("titulo").textContent = cap(MESES[dados.mes - 1]) + " de " + dados.ano;
  var ok = dados.solver.status === "ótima";
  document.getElementById("meta").innerHTML =
    '<div class="status' + (ok ? "" : " alerta") + '">Solução ' + esc(dados.solver.status) + "</div>" +
    "<div>" + num(dados.solver.tempo_s, 0) + " s de resolução · gerado em " + esc(dados.gerado_em) + "</div>";

  // ---------- indicadores ----------
  var pctCasados = met.refeicoes ? Math.round(100 * met.casados.length / met.refeicoes) : 0;
  var maiorInv = met.inversoes.length ? "maior diferença +" + num(met.inversoes[0].diferenca, 1) : "nenhuma refeição";
  var kpis = [
    ["", "Popularidade total", num(met.popularidade, 1), "soma dos scores P × F"],
    ["", "Refeições planejadas", met.refeicoes, "almoços e jantares · + " + met.desjejuns + " desjejuns"],
    ["azul", "Pratos do mesmo grupo", met.casados.length, pctCasados + "% das refeições"],
    [met.inversoes.length ? "ambar" : "verde", "Prato 2 acima do prato 1", met.inversoes.length, maiorInv],
    [met.colisoes ? "ambar" : "verde", "Preparos repetidos perto", met.colisoes,
     "até " + dados.parametros.ALCANCE_PEN + " refeições de distância"]
  ];
  document.getElementById("kpis").innerHTML = kpis.map(function (k) {
    return '<div class="kpi ' + k[0] + '"><div class="rotulo">' + k[1] + '</div><div class="valor">' +
      k[2] + '</div><div class="sub">' + k[3] + "</div></div>";
  }).join("");

  // ---------- calendário ----------
  function chips(dia, ref) {
    var h = "";
    var c = casados[chave(dia, ref)];
    var v = inversoes[chave(dia, ref)];
    if (c) h += '<span class="chip grupo" title="Mesmo preparo: ' + esc(c.preparo) + '">' + esc(c.preparo) + "</span>";
    if (v) h += '<span class="chip inv" title="Prato 2 com score maior que o prato 1">▲ +' + num(v.diferenca, 1) + "</span>";
    return h ? '<div class="chips">' + h + "</div>" : "";
  }

  function cartao(d) {
    var h = '<div class="dia" tabindex="0" role="button" data-dia="' + d.dia + '" aria-label="Ver detalhes do dia ' + d.dia + '">';
    h += '<div class="dia-topo"><span class="num">' + d.dia + '</span><span class="sem">' + SEM_CURTO[d.dia_semana] + "</span></div>";
    d.refeicoes.forEach(function (r) {
      if (r.refeicao === "Desjejum") {
        var fruta = r.itens[0];
        if (fruta) h += '<div class="desjejum extra">Desjejum · ' + esc(fruta.nome) + "</div>";
        return;
      }
      var p1 = doCat(r.itens, "prato_principal_1");
      var p2 = doCat(r.itens, "prato_principal_2");
      h += '<div class="ref"><div class="ref-nome">' + REFEICAO[r.refeicao] + "</div>";
      if (p1) h += '<div class="prato p1"><span class="nome">' + esc(p1.nome) + '</span><span class="nota">' + num(p1.P, 1) + "</span></div>";
      if (p2) h += '<div class="prato p2"><span class="nome">' + esc(p2.nome) + '</span><span class="nota">' + num(p2.P, 1) + "</span></div>";
      h += '<div class="extra">';
      EXTRAS.forEach(function (cat) {
        var it = doCat(r.itens, cat);
        if (it) h += '<div class="extra-linha"><span class="cat">' + CATEGORIA[cat] + "</span><span>" + esc(it.nome) + "</span></div>";
      });
      h += "</div>" + chips(d.dia, r.refeicao) + "</div>";
    });
    return h + "</div>";
  }

  var cal = "";
  for (var c = 0; c < 6; c++) cal += '<div class="cab-semana">' + SEM_CURTO[c] + "</div>";
  // Grade de 6 colunas (seg a sáb). Como o domingo é pulado, basta
  // preencher o início da primeira semana; o resto quebra sozinho.
  var inicio = dados.primeiro_dia_semana === 6 ? 0 : dados.primeiro_dia_semana;
  for (var c0 = 0; c0 < inicio; c0++) cal += '<div class="vazio"></div>';
  for (var dia = 1; dia <= dados.dias_no_mes; dia++) {
    var ds = (dados.primeiro_dia_semana + dia - 1) % 7;
    if (ds === 6) continue;               // domingo: sem refeições
    var d = porDia[dia];
    cal += d ? cartao(d) : '<div class="vazio"></div>';
  }
  var calEl = document.getElementById("calendario");
  calEl.innerHTML = cal;

  // ---------- destaques ----------
  function quando(dia, ref) { return "Dia " + dia + " · " + REFEICAO[ref].toLowerCase(); }
  document.getElementById("t-casados").textContent = "Pratos do mesmo grupo (" + met.casados.length + ")";
  document.getElementById("l-casados").innerHTML = met.casados.length ? met.casados.map(function (c) {
    return '<li data-dia="' + c.dia + '"><span class="quando">' + quando(c.dia, c.refeicao) + "</span><span>" +
      esc(c.pp1) + " + " + esc(c.pp2) + '</span><span class="chip grupo">' + esc(c.preparo) + "</span></li>";
  }).join("") : '<li class="vazia">Nenhuma refeição.</li>';

  document.getElementById("t-inv").textContent = "Prato 2 acima do prato 1 (" + met.inversoes.length + ")";
  document.getElementById("l-inv").innerHTML = met.inversoes.length ? met.inversoes.map(function (c) {
    return '<li data-dia="' + c.dia + '"><span class="quando">' + quando(c.dia, c.refeicao) + "</span><span>" +
      esc(c.pp1) + " (" + num(c.P1, 1) + ") · " + esc(c.pp2) + " (" + num(c.P2, 1) + ')</span><span class="chip inv">▲ +' +
      num(c.diferenca, 1) + "</span></li>";
  }).join("") : '<li class="vazia">Nenhuma refeição. O prato 1 é sempre o mais bem avaliado.</li>';

  // ---------- parâmetros ----------
  var DESC = {
    PESO_PEN_BASE: "custo de repetir um preparo na refeição seguinte (PEN1)",
    ALCANCE_PEN: "distância máxima, em refeições, em que o PEN1 age",
    PESO_BON1: "bônus quando prato 1 e prato 2 são do mesmo preparo",
    FOLGA_PEN2: "diferença de score tolerada sem custo (PEN2)",
    PESO_PEN2: "custo por ponto de score em que o prato 2 passa o prato 1"
  };
  document.getElementById("params").innerHTML = Object.keys(dados.parametros).map(function (k) {
    return "<dt>" + k + " = " + dados.parametros[k] + "</dt><dd>" + (DESC[k] || "") + "</dd>";
  }).join("");

  // ---------- modo de visualização ----------
  var botoes = document.querySelectorAll(".segmentado button");
  function aplicarModo(modo) {
    calEl.classList.toggle("completo", modo === "completo");
    botoes.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.modo === modo)); });
    try { localStorage.setItem("cardapio-modo", modo); } catch (e) {}
  }
  botoes.forEach(function (b) { b.addEventListener("click", function () { aplicarModo(b.dataset.modo); }); });
  try { aplicarModo(localStorage.getItem("cardapio-modo") || "resumo"); } catch (e) { aplicarModo("resumo"); }

  // ---------- detalhe do dia ----------
  var dlg = document.getElementById("detalhe");
  function abrirDia(numDia) {
    var d = porDia[numDia];
    if (!d) return;
    document.getElementById("dlg-titulo").textContent =
      SEM_LONGO[d.dia_semana] + ", " + d.dia + " de " + MESES[dados.mes - 1];
    var h = "";
    d.refeicoes.forEach(function (r) {
      var itens = r.itens.slice().sort(function (a, b) {
        return ORDEM.indexOf(a.categoria) - ORDEM.indexOf(b.categoria);
      });
      h += '<div class="dlg-ref"><div class="dlg-ref-topo"><h4>' + REFEICAO[r.refeicao] + "</h4>" +
        (r.refeicao !== "Desjejum" ? '<span class="f" title="Peso da refeição no objetivo, vindo da demanda estimada pelo DML">movimento F = ' + num(r.F, 2) + "</span>" : "") +
        "</div><table><tr><th></th><th></th><th>P</th><th>P × F</th></tr>";
      itens.forEach(function (it) {
        var cls = it.categoria === "prato_principal_1" ? "p1" : it.categoria === "prato_principal_2" ? "p2" : "";
        var semScore = it.S === 0;
        h += '<tr class="' + cls + '"><td class="cat">' + (CATEGORIA[it.categoria] || it.categoria) + '</td><td class="item">' +
          esc(it.nome) + '</td><td class="num">' + (semScore ? "—" : num(it.P, 1)) + '</td><td class="num">' +
          (semScore ? "—" : num(it.S, 1)) + "</td></tr>";
      });
      h += "</table>" + (r.refeicao !== "Desjejum" ? chips(d.dia, r.refeicao).replace('class="chips"', 'class="chips" style="margin-left:0"') : "") + "</div>";
    });
    document.getElementById("dlg-corpo").innerHTML = h;
    dlg.showModal();
  }
  document.addEventListener("click", function (e) {
    var alvo = e.target.closest("[data-dia]");
    if (alvo) abrirDia(Number(alvo.dataset.dia));
  });
  document.addEventListener("keydown", function (e) {
    if ((e.key === "Enter" || e.key === " ") && e.target.matches(".dia")) {
      e.preventDefault();
      abrirDia(Number(e.target.dataset.dia));
    }
  });
  dlg.querySelector(".fechar").addEventListener("click", function () { dlg.close(); });
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
})();
</script>
</body>
</html>
"""
  