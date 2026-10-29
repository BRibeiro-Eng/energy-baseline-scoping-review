# Detector (c) — estado das surfaces, 2026-09-10

**Surface de record: Claude.** Lançada 2026-09-10 ~12:35 com
`work/detector_claude/run.py --workers 2`, fila completa de 394, escreve em
`responses_claude/`.

## Tentativa ChatGPT/Codex — parada por quota, estatuto por decidir

`responses_chatgpt/` tem **30 respostas válidas de 394** (5 de 2026-09-09 + 25 de
2026-09-10). As duas corridas pararam com `You've hit your usage limit` da conta
ChatGPT Plus: a de 09-09 aos 5 papers com 3 workers, a de 09-10 aos ~25 com 1 worker,
com reset anunciado para as 16:51.

Medido: **a conta rende ~25-30 papers por janela de ~5 h** neste perfil de chamada
(texto Stage-0 completo por paper, `gpt-6-astra`, reasoning `xhigh`). 394 papers
exigiriam ~14 janelas — cerca de três dias de execução vigiada. Por isso a surface
foi trocada, não por preferência metodológica.

**Estas 30 respostas não estão na união e não entram nela sem uma decisão explícita
do reviewer.** `collect.py` corre por diretório: nada aqui é agregado por acidente.

Duas saídas possíveis, ambas defensáveis, à escolha do reviewer:

1. **Descartar** — a união fica com uma só passagem de máquina, que é o que o
   §3-Step-4 especifica. As 30 ficam como registo de tentativa. Simples de declarar.
2. **Unir** — `collect.py --responses responses_chatgpt --out recall_flags.json` além
   do Claude. Estritamente mais recall, mas cobertura assimétrica (30/394 num lado,
   394/394 no outro), o que tem de ser dito assim no relatório: não é uma segunda
   passagem, é uma passagem parcial de 7,6 % do frame. Cada disparo extra é uma
   leitura completa a somar à fila de triagem.

Recomendação registada nesta nota: opção 1, por causa da assimetria e do custo de
triagem. A decisão é do reviewer.

## Nota de provenance

O runner do lado Claude regista `models_returned` por chamada. As primeiras respostas
trazem `["claude-haiku-4-5-20251001", "claude-opus-4-8[1m]"]` — o CLI usa haiku em
tarefas auxiliares além do modelo pinado. O campo fica registado por resposta; o
relatório do censo deve dizê-lo em vez de declarar um modelo único.

O lado Codex correu `gpt-6-astra` / reasoning `xhigh` / codex-cli 0.153.4 — modelo
distinto do twin de extração (`gpt-5.6-sol`), o que é aceitável num detector
independente mas tem de constar se a opção 2 for escolhida.

## Alteração ao verificador de citações do runner — 2026-09-10 12:30

**Autorizada pelo reviewer nesta data.** O run bloqueou às 11:51 com 69 respostas
válidas, em `rayyan-472535487`, com quatro erros `quote is not verbatim`.

Diagnóstico: as quatro citações são reais e estão na página indicada. O paper é um
manuscrito em formato de submissão, com numeração de linhas impressa que o extractor
apanhou intercalada no texto corrido — a p.38 lê-se `most large steelmakers in china
1490 have deployed similar information technologies (…) over the 1491 past decade`.
O modelo transcreveu a frase sem os números de linha. Não houve fabricação: o defeito
estava no verificador.

O runner usava uma verificação própria (`norm()` + substring exacta) em vez do
`grounding.py`, que é o verificador registado no protocolo (§6.3, 8 regras v2.2.1,
alinhamento difuso com threshold por comprimento). O canónico valida as quatro
citações com scores 92,7 · 96,3 · 93,2 e `page_unverified: false`.

**Alteração aplicada:** `work/detector_claude/run.py` passa a validar com
`ground_quote()`. Backup do original em `run.py.bak_20260910T1230`.

- Falha (e recusa a resposta) quando `grounded` é falso.
- Quando a citação está fundamentada mas a página não se confirma, regista o aviso em
  `_grounding_warnings` na própria resposta e **não** bloqueia — bloquear por número de
  página quando a citação é real reintroduz o defeito que isto corrige.
- A verificação de página inexistente no bundle mantém-se como erro.

**Isto não relaxa o critério:** substitui um verificador ad-hoc pelo verificador mais
exigente e já registado do pipeline. As 69 respostas anteriores passaram pelo teste
estrito e continuam válidas — o canónico é estritamente mais permissivo, nada do que
passou deixa de passar. Não há necessidade de reprocessar o que já está feito.

**Alcance do problema:** 18 dos 459 papers do corpus têm numeração de linhas no texto
extraído. Sem esta correção o run bloquearia uma vez por cada um que aparecesse na fila.

Run relançado às 12:32; `rayyan-472535487` validado (3 sinais de setor listado, 1 outro,
1 aviso de página registado).
