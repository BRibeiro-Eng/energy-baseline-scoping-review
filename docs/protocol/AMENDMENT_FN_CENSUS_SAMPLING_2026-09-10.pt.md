---
data: 2026-09-10
tipo: emenda-protocolo
estado: POR SUBMETER (OSF) — requer data de submissão antes da produção do relatório
afecta: VALIDATION_PROTOCOL_C.md §3-Step-4, §6a; PROTOCOL.md §12.5
---

# Emenda — censo de falsos negativos passa a triagem por amostragem

## O que estava registado

O C-2.3 §3-Step-4 especifica um **censo**: a união dos candidatos produzidos pelos
detectores (a) flags de modelo, (b) léxico determinístico e (c) passagem de recall é
**esvaziada** pelo revisor — cada candidato recebe um veredicto com justificação, e a
regra de fecho é uma passagem completa sem candidatos novos. A ordem de corte
pré-registada (C-2 §6) exclui explicitamente os censos de qualquer redução.

## O que aconteceu

A união em 2026-09-10 tinha 177 candidatos (125 Tier-hit-A, 52 Tier-hit-B), com o
detector (c) ainda em execução. Foram registados 177 veredictos, todos `not_fn`.

A auditoria dos ficheiros mostra que **171 desses veredictos foram emitidos sem
leitura**:

- mediana de 2 segundos entre decisões consecutivas, incluindo em Tier-hit-A, cuja
  carga registada é de 10-12 minutos de leitura completa por paper;
- 166 das 176 transições abaixo de 10 segundos;
- 169 justificações idênticas (`"nao aplicável"`), mais duas variantes vazias
  equivalentes.

Os 171 foram anulados para `verdicts/_voided_20260910T1530/` (preservados, fora de
qualquer cálculo). Seis veredictos com justificação substantiva foram mantidos.

Registo directo desta constatação: o resultado que o instrumento produzia
— «censo completo, zero falsos negativos confirmados» — seria uma afirmação empírica
falsa no relatório, na tese e no depósito OSF. Não é uma limitação por declarar; é um
facto que não ocorreu. Daí esta emenda, e não uma nota de rodapé.

## O que se altera

O censo exaustivo é substituído por **triagem por amostragem aleatória simples** sobre
o mesmo frame de candidatos:

| parâmetro | valor |
|---|---|
| frame | 177 candidatos (união dos detectores a+b; (c) por integrar) |
| n | 40 |
| método | `random.Random(45).sample(sorted(frame), 40)` |
| seed | **45** (nova; 42 form pilot, 43 validação, 44 SRS audit já em uso) |
| composição sorteada | 33 Tier-hit-A · 7 Tier-hit-B |
| cobertura | 22,6 % do frame |
| registo | `output/fn_census/triage/SAMPLE.json` |

Estimativa de esforço: ~6,2 h, contra as ~35 h do censo com os candidatos projectados
do detector (c).

## Como se reporta

A palavra «censo» **não** pode aparecer associada a este resultado. A formulação é:

> Triagem por amostragem aleatória simples do frame de candidatos a falso negativo
> (n = 40, seed 45, 22,6 % de um frame de 177), com taxa de falsos negativos observada
> de e/n e intervalo de confiança exacto de Clopper-Pearson a 95 %.

O denominador é o da amostra, nunca o do frame. Se a amostra der zero falsos negativos,
o limite superior de Clopper-Pearson a 95 % para n=40 é 8,8 % — é isso que se pode
afirmar, e não «não há falsos negativos».

## O que isto custa, dito explicitamente

A regra de fecho do §3-Step-4 (zero candidatos novos numa passagem completa) **deixa de
poder ser satisfeita**. O roster do Corpus B passa a ser travado sobre uma estimativa
da taxa de falsos negativos em vez de sobre a sua exclusão. Os 137 candidatos fora da
amostra ficam por examinar e essa é a limitação central a declarar nas SQ2-4: qualquer
paper de processo contínuo que lhes pertença permanece por identificar.

## O que continua obrigatório

O §6a mantém-se sem alteração. Qualquer falso negativo confirmado na amostra dispara a
expansão do léxico com o vocabulário de sector desse paper e a re-execução do detector
(b); três ou mais obrigam a discussão com o orientador sobre re-screen sectorial antes
de travar o roster. Com amostragem, um FN na amostra implica além disso uma taxa
extrapolável ao frame, o que torna a re-execução mais urgente e não menos.

## Instrumentação acrescentada

`serve_triage.py` passa a registar `dwell_seconds` por veredicto — o intervalo entre o
paper ser servido e a decisão ser gravada — e `progress.py` reporta a mediana e o número
de decisões abaixo de 30 segundos. O campo destina-se ao relatório: é a evidência
verificável de que a triagem foi executada, e substitui a confiança na afirmação de que
foi.

## Frame incompleto: o segundo estrato

A amostra acima foi sorteada com o detector (c) ainda a correr (96/394 em
2026-09-10 15:30). Quando fechar, acrescenta candidatos ao frame — a projecção sobre
os primeiros 96 é de ~66 novos, para um frame final de ~243.

A amostra **não** é re-sorteada. O desenho passa a ter dois estratos com pesos
conhecidos:

| estrato | frame | n | como |
|---|--:|--:|---|
| I — candidatos anteriores ao detector (c) | 177 | 40 | já sorteado, seed 45 |
| II — candidatos acrescentados pelo detector (c) | a determinar | ⌈0,226 × N_II⌉ | seed 46, sorteio após o fecho de (c) |

A fracção de amostragem é a mesma nos dois estratos (22,6 %), portanto a taxa global
é a média ponderada pelos tamanhos dos estratos e o intervalo combina-se pelos métodos
usuais de amostragem estratificada. Reporta-se a taxa por estrato **e** a global; nunca
só a global, porque o estrato II é o que o léxico não tinha apanhado e a sua taxa de FN
é, à partida, a mais alta dos dois.

Consequência prática: a triagem do estrato I pode começar imediatamente e não é
invalidada pelo que o detector (c) trouxer.

## Estado

Emenda **não submetida**. A data de submissão tem de ser preenchida e o depósito feito
antes de qualquer relatório que use estes números.

---

# Revisão do desenho — estratificação por risco (2026-09-10, 16h)

A amostragem aleatória simples descrita acima (n=40, seed 45) **é substituída** antes de
qualquer execução, por um desenho que cobre melhor o mesmo esforço humano. O sorteio
seed 45 fica registado em `SAMPLE_superseded_seed45.json`; nenhum paper foi triado sob ele.

## Quarto detector (classificação automática do frame)

Aos três detectores registados junta-se uma **passagem de classificação sobre a totalidade
dos 177 candidatos**, executada por seis agentes Claude Opus em 2026-09-10, cada um com
acesso aos excertos de léxico e ao texto Stage-0 integral. Papel: detector, nunca
adjudicador — a saída é uma recomendação ordenada, e nenhuma entra num ficheiro de
veredicto sem decisão humana.

Saída (`CLASSIFIER.json`), por categoria:

| categoria | n | significado |
|---|--:|---|
| `A_aplica` | 5 | evidência de aplicação num sector da lista fechada — candidato forte a FN |
| `B_contexto` | 43 | indústria de processo contínuo sem aplicação clara, ou sector contínuo não-listado |
| `C_mencao` | 55 | menção, contexto, revisão de literatura ou lista de sectores |
| `D_homonimo` | 74 | homonímia (`refining` de parâmetros, `steel` como material, `ammonia` como refrigerante) ou bibliografia |

**Verificação:** das 48 classificações que citam evidência, as 48 citações foram
verificadas contra o texto Stage-0 do próprio paper com `grounding.py` — **zero falhas**.
O classificador não fabricou evidência em nenhum caso.

## Desenho de revisão humana

| estrato | frame | revistos | critério |
|---|--:|--:|---|
| alto risco (`A` + `B`) | 48 | **48** | integral, sem amostragem |
| baixo risco (`C` + `D`) | 129 | **25** | aleatória, seed 46, 19,4 % |
| **total** | **177** | **73** | |

Vantagem face à ASR: o estrato onde os falsos negativos plausivelmente estão é coberto
**na totalidade** em vez de a 22,6 %, pelo mesmo esforço humano (~73 papers). A amostra de
controlo do estrato de baixo risco existe para o que a ASR daria de graça e este desenho
não dá — uma estimativa da taxa de falsos negativos **que o classificador deixou passar**.

## Como se reporta

> Triagem do frame de candidatos a falso negativo (n = 177) assistida por classificação
> automática com evidência verificada contra o texto-fonte. O estrato de alto risco
> (n = 48) foi revisto integralmente pelo revisor; o estrato de baixo risco (n = 129) foi
> amostrado aleatoriamente (n = 25, seed 46, 19,4 %). Reporta-se a taxa de falsos negativos
> por estrato, com intervalo exacto de Clopper-Pearson no estrato amostrado.

Continua a **não** ser um censo, e a palavra não se usa. O que mudou face ao desenho
anterior é a eficiência da alocação, não a natureza da alegação.

**Regra de leitura do controlo:** qualquer falso negativo encontrado nos 25 de controlo é
uma falha do classificador e obriga a rever integralmente o estrato de baixo risco — a
alegação de cobertura dirigida deixa de se sustentar. Zero falsos negativos em 25 dá um
limite superior de Clopper-Pearson a 95 % de 13,7 % para esse estrato: é isso que se
escreve, não «o classificador não falhou».

## Instrumentação

O formulário mostra a recomendação do classificador ao lado dos excertos e do PDF, com a
citação e o estado de verificação. O `dwell_seconds` continua a ser registado por decisão:
o desenho pressupõe leitura, e a evidência de que houve leitura é esse campo.
