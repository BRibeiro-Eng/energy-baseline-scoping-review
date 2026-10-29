# Fecho do censo Tier-1 — 2026-09-09

Decisão do reviewer (B. Ribeiro, 2026-09-09): **confirmar as decisões cegas como finais,
sem adoptar nenhum valor revelado**, e reverter as edições produzidas por uma sessão de IA.
Registo obrigatório: `production/` não é versionado em git, este ficheiro e
`revert_confirm_20260909T173542.json` são o único rasto.

## O que foi revertido

Entre as 17:52 e as 17:56 de 2026-09-09, uma sessão Codex/ChatGPT abriu cinco papers no
formulário e gravou neles. Quatro foram gravados sem alteração de valor. Um foi alterado:

| paper | campo | cego | alterado para | estado agora |
|---|---|---|---|---|
| `rayyan-472536742` | `eligibility.level_3b` | `false` | `true` | **revertido para `false`** |

A justificação escrita pela sessão de IA declarava-se «pendente de adjudicação humana» e
apoiava-se na citação da p.6 (testemunho da California Portland Cement Company). A decisão
cega do reviewer já tinha examinado e rejeitado essa mesma passagem, classificando-a como
testemunho de parceiro atribuído a comunicação pessoal (nota 13), sem variáveis, forma
funcional, dados ou resultado de cimento em lado nenhum, e identificando os dois setores
efectivamente demonstrados como montagem automóvel (discreto) e moagem húmida de milho
(contínuo não-listado) — o que dispara a cláusula CRITICAL do §5.3. A reversão restaura o
valor e a evidência a partir do snapshot cego imutável `rayyan-472536742.blind.json`.

O log `rayyan-472536742.reveal_changes.jsonl` foi anulado para
`rayyan-472536742.reveal_changes.jsonl.voided_20260909T173542` (conteúdo preservado, fora do
cálculo). Razão: a figura de exposição a anchoring do §3-Step-3 mede alterações do reviewer
humano após ver o twin. Três linhas escritas por uma sessão de IA não são observações desse
instrumento; contá-las sobrestimaria o anchoring do reviewer com um evento que não é dele.
O evento é reportado aqui, como incidente, não como dado.

## Estado final

82/82 papers, 90/90 células, todos `finalised` com o valor cego. Nenhuma célula adoptou o
valor do twin. Verificado programaticamente: zero divergências entre cada `{key}.json` e o
respectivo `{key}.blind.json`.

## Como isto tem de ser reportado (não usar o output do progress.py tal como sai)

`progress.py` imprime «0 reveal-changes over 82 revealed papers». O denominador está errado
para efeitos de relatório: conta `revealed + finalised`. A exposição real reparte-se assim:

| classe | n | o que se pode afirmar |
|---|--:|---|
| Finalizados sem qualquer exposição a output de modelo | 73 | decisão cega assumida como final; nunca houve reveal |
| Revelados a 2026-09-01, trabalhados pelo reviewer, finalizados hoje em bloco | 3 | `rayyan-472535377`, `-472535386`, `-472535481`; exposição real, adjudicação individual não concluída |
| Revelados por sessão de IA a 2026-09-09, finalizados no valor cego | 5 | `rayyan-472535511`, `-472535541`, `-472536054`, `-472536742`, `-472535739`; cegueira consumida sem adjudicação humana |
| Revelado e adjudicado integralmente pelo reviewer | 1 | `rayyan-472535360` (2026-09-01) |

**Formulação para o relatório e para a limitação declarada:** o reveal previsto no §3-Step-5
foi executado integralmente em 1 paper e parcialmente em 3; em 5 a exposição ao twin ocorreu
por uma sessão automatizada e não constitui adjudicação humana; nos restantes 73 o reveal não
foi executado e a decisão cega foi assumida como final por decisão do reviewer, tomada sob
constrangimento de calendário. A figura de anchoring-exposure do §3-Step-3 é, portanto,
**1/1 papers adjudicados com 0 alterações** — não 0/82. Qualquer número maior que 1 no
denominador sobrestima a quantidade de leitura independente que existiu.

O que isto **não** compromete: nenhuma decisão de pertença foi tomada com o twin à vista, e o
sentido do erro residual é conhecido — as decisões são as do reviewer, cegas, sem contaminação.
O que isto **custa**: perde-se a segunda leitura independente sobre 81 dos 82 papers, e com ela
a capacidade de estimar quanto é que essa segunda leitura teria mudado.
