# Dúvidas e contradições encontradas no edital

Registro das ambiguidades e incompatibilidades matemáticas encontradas no
Edital de Pregão Eletrônico nº 10/2021-PUSP-SC (Anexo I — Memorial Descritivo)
durante a implementação do modelo de otimização.

Cada item traz: o que o edital diz, por que gera problema, o que foi decidido
provisoriamente e **o que precisa ser confirmado com o orientador / a nutricionista**.

Referência de cálculo: maio/2026 — 26 almoços, 21 jantas, 5 sábados (só almoço),
que é o mês de 26 dias úteis assumido pelas tabelas do edital.

---

## 1. Tabela 06 × alternância branca/vermelha (5.23.15) — CONTRADIÇÃO GRAVE

**O que o edital diz**

- Tabela 06 (5.23.19) fixa a frequência mensal de cada corte de carne.
  Agregando por tipo: almoço 7 brancas / 19 vermelhas; jantar 6 brancas /
  16 vermelhas.
- Item 5.23.15: "Quando utilizar carne branca no almoço, deve ser utilizada
  carne vermelha no jantar. Quando utilizar carne vermelha no almoço, deve
  utilizar carne branca no jantar."

**Por que é impossível cumprir os dois**

Duas demonstrações independentes, ambas confirmadas pelo IIS do Gurobi:

- **(a) Pelo lado das brancas.** A alternância obriga 1 carne branca por dia
  em cada um dos 21 dias que têm almoço e jantar → mínimo de 21 brancas no
  mês. A Tabela 06 teta as brancas em **13** (merluza 2, coxa/sobrecoxa 4,
  frango industrializado 3, peito 4). Faltam 8.

- **(b) Pelo lado das vermelhas.** Das 19 vermelhas exigidas no almoço, no
  máximo 5 cabem nos sábados (que não têm jantar). As outras 14 exigiriam 14
  brancas no jantar, mas a tabela só concede 6.

Não é erro de modelagem: as duas exigências do edital são mutuamente
inconsistentes para qualquer mês de 26 dias úteis.

**Decisão provisória (do grupo)**

Preservar os **tetos** da Tabela 06 (estourar cota é violação inequívoca) e
**afrouxar a alternância** do 5.23.15, substituindo-a por uma alternância mais
fraca porém bem definida: o **tipo** de carne (bovina, suína, frango, peixe,
embutidos) não se repete entre almoço e jantar do mesmo dia — restrição
`PP2T` no código. As restrições originais `PP2`/`PP3` foram removidas.

Complementarmente, um **piso de 1 aparição mensal por corte** (`T06min`)
garante que nenhum corte saia 0x no mês. Esse era o problema que motivou toda
a investigação: sem a Tabela 06, peixe, lagarto e bisteca simplesmente nunca
apareciam, porque o objetivo só premia itens de score alto.

**A CONFIRMAR COM O ORIENTADOR**

- [ ] Ceder na Tabela 06 ou no 5.23.15? A escolha atual foi ceder no 5.23.15.
- [ ] A alternância por tipo de carne é aceitável como substituta?
- [ ] "Embutidos" deve contar como tipo próprio (decisão atual, seguindo a
      própria Tabela 06) ou ser tratado como carne vermelha?
- [ ] As quantidades exatas da Tabela 06 deixam de ser atingidas (ex.: um
      corte pode sair menos vezes que a cota). Isso é aceitável, ou a cota
      deve ser piso obrigatório mesmo custando outras regras?

---

## 2. Tabelas 06, 07 e 08: as cotas de jantar não cabem no mês

**O que o edital diz**

As três tabelas dão cotas mensais por (almoço, jantar) para "26 dias úteis".

**O problema**

Um mês de 26 dias úteis tem 26 almoços mas apenas **21 jantas** — os sábados
têm almoço e não têm jantar (Tabela 02). Somando as cotas de jantar:

| Tabela | Soma jantar | Jantas disponíveis | Excesso |
|---|---|---|---|
| 06 (cortes de carne) | 22 | 21 | +1 |
| 07 (opção do prato principal) | 22 | 21 | +1 |
| 08 (guarnições) | 22 | 21 | +1 |

As três tabelas pedem exatamente 1 aparição a mais do que o mês comporta.
A regularidade sugere que o edital contou 26 jantas junto com os 26 almoços,
desconsiderando que sábado não tem jantar.

**Decisão provisória**

Usar `<=` (teto) no jantar em vez de `==`. O jantar fica sujeito a não
estourar a cota, mas não se garante bater o piso em toda categoria.

**A CONFIRMAR COM O ORIENTADOR**

- [ ] Qual linha de cada tabela deve ceder a aparição excedente no jantar?
- [ ] Ou as cotas de jantar devem ser reescaladas por 21/22?

---

## 3. Meses que não têm 26 dias úteis

**O problema**

Todas as tabelas de frequência assumem "26 dias úteis ao mês", mas os meses
reais variam. Janeiro/2026 tem 27 dias úteis: com `==` no almoço o modelo fica
**infactível** (testado), porque as cotas somam exatamente 26 e sobra 1 slot
sem cota que preencher.

**A CONFIRMAR COM O ORIENTADOR**

- [ ] Aceitar violação do edital nesses meses?
- [ ] Aumentar a cota do item mais frequente proporcionalmente?
- [ ] Escalar todas as cotas por `dias_uteis_reais / 26`? (parece o mais
      defensável, mas muda números contratados)

---

## 4. Repetição do mesmo prato no mesmo dia da semana

**O problema**

O edital proíbe repetir o prato principal "durante a semana" (5.23.6), o que
está implementado como janela móvel de 7 dias (`PP1`). Mas nada impede que o
mesmo prato caia toda sexta-feira do mês.

Isso acontecia de forma extrema antes da Tabela 06: cada dia da semana tinha
literalmente **um único prato** repetido em todas as suas ocorrências (ex.:
lasanha bolonhesa nas 5 sextas). Depois da Tabela 06 melhorou bastante — a
maioria dos dias passou a ter 4-5 pratos distintos — mas a sexta-feira ainda
concentra (lasanha bolonhesa 5x, estrogonofe de frango 4x).

**Causa técnica**

A função objetivo é `S[i,r,d] = P[i] × F[r][dia_da_semana]`. Ela não depende
de qual semana do mês é, então o valor de escolher um prato numa sexta é
idêntico em todas as sextas. Nada no modelo penaliza repetir entre semanas.

**A CONFIRMAR COM O ORIENTADOR / GRUPO**

- [ ] O edital não proíbe isso explicitamente. É aceitável na prática, ou o RU
      considera indesejável?
- [ ] Se for indesejável, qual abordagem: (a) ampliar a janela do `PP1` para
      mais de 7 dias, (b) limite de aparições mensais por item, ou (c) termo
      de diversidade na função objetivo?

---

## 5. Itens do edital ainda não implementados

Levantados na auditoria (ver BLOCO 4b em `src/otimizacao.py`), sem impedimento
conhecido — falta só decidir prioridade e, em alguns casos, cadastrar dados.

| Item | O que falta | Bloqueio |
|---|---|---|
| Tabela 09 (sobremesas, 5.26.2) | cota mensal por tipo de doce | precisa coluna `tipo_doce` |
| Tabela 10 (frutas, 5.26.14) | cota mensal por fruta | nenhum — itens já existem |
| 5.20.3 | fruta do desjejum não repete na semana | nenhum |
| 5.24.7 | se salada é feijão soja, nada com soja na refeição | acopla salada a pp2 |
| 5.24.8 | mesmo grão na salada e no pp2 do mesmo dia | acopla salada a pp2 |

---

## 6. Ressalvas sobre o score P (não é dúvida do edital)

O score de popularidade vem de um Double Machine Learning sobre a demanda
histórica, e tem limitações que valem menção no relatório:

- Rodado apenas na Área 1; assume-se que as preferências da Área 2 são iguais.
- Mede efeito sobre **demanda total**, que é proxy de popularidade — um prato
  pode ter coeficiente alto por ter sido servido em dias de movimento maior.
  O DML controla covariáveis (clima, calendário, dia da semana), o que mitiga
  mas não elimina.
- 15 itens sem histórico receberam P = 5.5 (ponto médio neutro).
- Saladas são neutras por decisão (`CATEGORIAS_SEM_SCORE`), não por falta de
  dado.

---

## 7. O modelo não tem restrição nutricional

O edital exige "alimentação balanceada" (1.1) e a Tabela 04 define porções,
mas o modelo não conhece caloria, proteína, sódio nem custo. Um cardápio pode
ser ótimo para o objetivo e desequilibrado nutricionalmente.

**A CONFIRMAR** — [ ] entra no escopo do projeto ou fica fora?

---

## 8. Pratos de mesmo preparo aparecendo colados (PEN1) — NÃO É REGRA DO EDITAL

**O problema observado**

Pratos com o mesmo **modo de preparo** mas ingrediente diferente apareciam
muito próximos: "estrogonofe de carne" no almoço e "estrogonofe de frango"
no jantar do mesmo dia; "lasanha bolonhesa" (pp1) e "lasanha de pvt" (pp2)
na **mesma refeição**; o mesmo com as iscas de carne.

Medido no cardápio de maio/2026 **antes** da correção:

| Tipo de colisão | Ocorrências |
|---|---|
| Mesmo preparo no mesmo dia | 10 |
| Mesmo preparo em refeições consecutivas | 12 |
| Mesmo preparo na **mesma refeição** (pp1 + pp2) | 2 (estrogonofe, lasanha) |

**Por que acontecia**

Duas causas somadas:

1. **A planilha não modelava preparo.** As colunas eram `especificacao`
   (tipo de carne) e `produto` (corte/ingrediente). Para o modelo,
   "estrogonofe de carne" e "estrogonofe de frango" são *maximamente*
   diferentes — espécies e cortes distintos — e passam por `PP2T` e `PP6`
   sem nenhum conflito.

2. **O objetivo empurrava para isso.** Preparos populares têm P alto em
   várias categorias ao mesmo tempo: se estrogonofe é popular, o de carne,
   o de frango e o de pvt herdam P alto. O solver escolhia o melhor de cada
   categoria e eles convergiam para a mesma família.

**Solução implementada (decisão do grupo)**

Coluna nova `preparo` na planilha + **penalização de proximidade no
objetivo** (`PEN1` em `src/otimizacao.py`), e não restrição rígida.

Por que penalização e não restrição: uma proibição ("no máximo 1
estrogonofe por dia") é cega à distância — trataria igual um par colado no
mesmo dia e um par separado por duas semanas — e pode tornar o modelo
infactível junto com as cotas fixas da Tabela 07 (lasanha aparece em
"massa com queijo" E "massa com pts", ambas com cota mensal).

Formulação: trabalha em **slots** (a sequência cronológica de refeições
principais), não em dias — almoço → jantar do mesmo dia é distância 1.
O peso decai com a distância, `peso(k) = PESO_PEN_BASE / k`, e a distância
0 (mesma refeição) leva o dobro do peso da distância 1.

> **Atualizado pelo item 9:** o par pp1 + pp2 de mesmo preparo na mesma
> refeição deixou de ser penalizado e passou a receber bônus (`BON1`). A
> distância 0 continua penalizando os outros casos (ex.: pp2 e guarnição
> ambos "frito"). E, nas distâncias k ≥ 1, cada slot passou a contar a
> **presença** do preparo, não o número de itens — senão um slot com
> estrogonofe no pp1 e no pp2 colidiria com todos os vizinhos.

Parâmetros atuais: `ALCANCE_PEN = 4` slots, `PESO_PEN_BASE = 25.0`.

**Resultado (maio/2026)**

- Colisões dentro do alcance de 4 slots: **10 + 12 → 0**
- Intervalo mínimo entre pratos do mesmo preparo: **0 → 5 slots**
- Custo em popularidade: objetivo 2017,1 → 2001,6 (**−0,8%**)
- Todas as restrições do edital continuam satisfeitas (reverificado)
- Tempo de resolução: <1s → ~105s

**DECISÕES TOMADAS QUE PRECISAM DE VALIDAÇÃO**

- [ ] **A classificação de `preparo` é julgamento culinário**, não dado de
      fonte — mesma natureza da coluna `fritura`. Precisa de revisão da
      nutricionista. Está em `PREPARO`, em `data/atualizar_planilha.py`
      (64 itens classificados, 16 preparos com 2+ itens).
- [ ] **"ao molho" foi deliberadamente EXCLUÍDO** como preparo, por decisão
      do grupo: o molho é detalhe do prato e não caracteriza semelhança.
      Se fosse incluído, agruparia 7 itens de pp1 (lagarto, lombo, pernil,
      bisteca, peixe, filé de frango) e travaria o modelo sem necessidade.
- [ ] **30 itens ficaram sem preparo** e portanto nunca são penalizados:
      "pvt", "legumes", "farofa", "polenta", "cuscuz", "macarrão",
      "nhoque", "creme de milho", vegetais puros de guarnição e os pratos
      "ao molho". Conferir se algum deveria entrar.
- [ ] **"bife" agrupa bifes de carne e vegetarianos** (bife de pvt, de grão
      de bico, de lentilha, de feijão): o formato do prato é o mesmo, que é
      o que o comensal percebe. Confirmar se é a leitura desejada.
- [ ] **"assado" ficou só com "coxa de frango assada"**, o único item cujo
      nome declara o preparo. Vários outros provavelmente são assados na
      prática — vale classificá-los?
- [ ] **Calibração de `PESO_PEN_BASE = 25.0`**: escolhido porque o maior S
      possível é ~20 (P=10 × F=2.0), então uma colisão adjacente custa mais
      que o ganho máximo de trocar um prato dentro da categoria. Com 0
      colisões no resultado, o peso pode estar mais alto que o necessário —
      vale testar valores menores se o custo de tempo incomodar.
- [ ] **`ALCANCE_PEN = 4` slots** (~2 dias). Aumentar espalha mais, mas o
      número de termos cresce linearmente e o tempo de resolução sobe.

**CUSTO COMPUTACIONAL** — a penalização acrescenta 3600 variáveis
contínuas e subiu o tempo de resolução de menos de 1 segundo para ~105
segundos. Ainda aceitável para uso mensal, mas é o fator que mais pesa se
o alcance ou o número de preparos crescer.

## 9. pp2 mais atrativo que o pp1 (PEN2) e pp1/pp2 do mesmo preparo (BON1) — NÃO É REGRA DO EDITAL

**Pedido do grupo**

1. O prato principal 2 não deve ser mais atrativo que o prato principal 1.
   Não precisa valer sempre, mas nunca deveria sair, por exemplo, o melhor
   pp2 junto do pior pp1.
2. É desejável que pp1 e pp2 sejam do mesmo preparo na mesma refeição
   (estrogonofe de frango + estrogonofe de pvt, lasanha bolonhesa +
   lasanha de berinjela).

**Solução implementada** (ambas no objetivo, em `src/otimizacao.py`)

- **PEN2** — penalidade linear por refeição:
  `v >= P(pp2) − P(pp1) − FOLGA_PEN2`, `v >= 0`, custo `PESO_PEN2 · v`.
  Comparar P entre categorias faz sentido porque o P é reescalado para
  [1, 10] **dentro** de cada categoria: P_pp2 > P_pp1 significa "o pp2 está
  mais alto no ranking dele do que o pp1 no dele".
  Parâmetros: `FOLGA_PEN2 = 1.0` (inversões de até 1 ponto são de graça),
  `PESO_PEN2 = 1.0` por ponto (o pior caso, 10 contra 1, custa 8).
- **BON1** — bônus `PESO_BON1 = 5.0` por refeição em que pp1 e pp2 têm o
  mesmo `preparo`. Só vale para preparos presentes nas duas categorias
  (bife, cozido, estrogonofe, gratinado, hambúrguer, lasanha, quibe, xadrez,
  frito).

**Resultado (maio/2026, 47 refeições principais)**

| Métrica | Antes | Depois |
|---|---|---|
| Refeições com P(pp2) > P(pp1) | 7 | 2 |
| Refeições com P(pp2) > P(pp1) + 1 | 4 | 2 |
| Pior excesso | +4,31 (lombo 5,7 × lasanha de pvt 10,0) | +3,09 |
| pp1 e pp2 do mesmo preparo | 0 | 23 |
| Colisões PEN1 (1 a 4 slots) | 0 | 0 |
| Popularidade pura (Σ S·x) | 2001,6 | 1990,6 (−0,55%) |
| Tempo de resolução | ~158 s | ~134 s |

As 2 inversões que sobraram são com "peixe ao molho" (P = 1, o piso da
escala), que o `T06min` obriga a aparecer; qualquer pp2 com P > 2 inverte.

**DECISÕES TOMADAS QUE PRECISAM DE VALIDAÇÃO**

- [ ] **23 de 47 refeições casadas é muito?** O bônus pode estar alto. Se
      o grupo achar repetitivo, baixar `PESO_BON1` (ex.: 2–3) ou limitar
      quantas vezes por semana o casamento é premiado.
- [ ] **"Atrativo" = P do DML.** É popularidade relativa dentro da
      categoria, não percepção declarada.
- [ ] **Calibração de `FOLGA_PEN2` e `PESO_PEN2`**: escolhidos para ser uma
      penalização branda, como pedido. Para zerar as inversões seria preciso
      subir o peso bem acima de 1.


## 10. Mesmo prato na mesma refeição na semana seguinte (PEN3) — NÃO É REGRA DO EDITAL

Pedido do grupo, por variedade: evitar, por exemplo, lasanha no almoço de
uma terça e de novo no almoço da terça seguinte.

**Por que nenhuma regra anterior cobria:** `PP1`/`OP1` usam janela móvel de
7 dias, que proíbe o item duas vezes dentro da janela mas permite `d` e
`d + 7` (janelas diferentes). A `PEN1` age só até `ALCANCE_PEN = 4` slots, e
a mesma refeição da semana seguinte fica a ~11 slots.

**O que foi feito:** para cada item de pp1 ou pp2 (prato EXATO, não
preparo) e cada par (`d`, `r`), (`d + 7`, `r`) existente:
`z >= x[i,r,d] + x[i,r,d+7] − 1`, `z >= 0`, custo `PESO_PEN3 · z`, com
`PESO_PEN3 = 6.0` (~30% do maior S, ~1/4 de uma colisão adjacente da PEN1).
Só pp1 e pp2; guarnição e sobremesa ficaram de fora por terem poucos itens
e cotas próprias.

**Resultado (maio/2026, ótima nos dois casos):**

| | Sem PEN3 | Com PEN3 |
|---|---:|---:|
| Repetições semanais de pp1/pp2 | 23 | 0 |
| Objetivo | 2101,5 | 2100,0 |

**DECISÕES QUE PRECISAM DE VALIDAÇÃO**

- [ ] **Peso:** com 6 a PEN3 já zera as repetições a um custo de 1,5 ponto,
      ou seja, age como proibição na prática. Se o grupo aceitar alguma
      repetição quando o prato for muito popular, baixar para 2–3.
- [ ] **Prato exato × preparo:** hoje é o prato exato. Penalizar o preparo
      colidiria com o BON1 (pp1 e pp2 do mesmo preparo são desejados).
- [ ] **Só semana N × N+1.** N × N+2 não é penalizado.
