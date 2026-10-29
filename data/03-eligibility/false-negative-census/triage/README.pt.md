# Triagem do censo de falsos negativos — C-2.3 §3-Step-4

177 candidatos: **125 Tier-hit-A** (leitura completa, ~10-12 min) e **52 Tier-hit-B**
(skim de 2 min). São papers que **os dois modelos classificaram `level_3b=false`** e que
um detector sinalizou. A tua função é esvaziar a lista: cada candidato sai com um
veredicto e uma justificação. Nada é descartado sem decisão.

A união ainda **não** inclui o detector (c) — quando essa passagem fechar, entram
candidatos novos. Não esperes por ela: estes 177 têm de ser triados de qualquer forma,
e depois tratas só do delta.

## A pergunta

Uma só, do §5.3: **este paper aplica, valida ou demonstra empiricamente alguma coisa
num setor de produção contínua da lista registada?**

Refinação · petroquímica (química orgânica, polímeros, olefinas) · cimento, cal,
clínquer · pasta e papel · aço e outros metais primários em produção contínua · química
contínua (ácido sulfúrico, amoníaco, metanol, fertilizantes, cloro-álcalis) · gases
industriais (separação de ar, hidrogénio, azoto) · vidro (fusão contínua, float).

A pertença decide-se **só pelo modo de produção**: fluxo contínuo, 24/7, não-discreto,
não-batch. Fora: manufatura discreta, química batch, serviços, edifícios, agricultura,
mineração salvo processamento contínuo.

**«Pode ser aplicado a» não é aplicação.** Uma menção de fundo, uma lista de setores
energo-intensivos na introdução, ou uma citação de outro estudo não são aplicação —
é exactamente por isso que a maioria destes 177 vai sair como `not_fn`.

Setor contínuo mas **fora** da lista: `--sector continuous-unlisted`, e a justificação
nomeia o setor. Não é Corpus B, mas fica registado como caso exploratório.

## Fluxo

```bash
python3 verdict.py --next B          # próximo skim; --next A para leitura completa
cat contexts/rayyan-XXXXXXXXX.md     # excertos já extraídos, com página
```

Os excertos em `contexts/` mostram-te **onde** cada termo aparece, com a página. Para
um Tier-B isso costuma bastar: se o termo só aparece numa lista de setores da
introdução, decides sem abrir o PDF. Se o excerto for ambíguo, abre o paper.

```bash
# a exclusão está correta — o sinal era ruído
python3 verdict.py rayyan-XXXXXXXXX not_fn "«steel» só na lista de setores energo-intensivos da introdução; o caso é uma fábrica de componentes"

# é um falso negativo — o paper é Corpus B e foi perdido
python3 verdict.py rayyan-XXXXXXXXX confirmed_fn --sector cement/lime/clinker \
    --page 4 --quote "the plant operates two rotary kilns" \
    "aplicação medida numa cimenteira, com dados de consumo por linha"

# Tier-B com dúvida — não decidas, promove
python3 verdict.py rayyan-XXXXXXXXX --promote "o caso pode ser uma refinaria, o excerto não chega"
```

A citação de um `confirmed_fn` é verificada contra o texto Stage-0 do próprio paper
antes de gravar. Se não bater, nada é escrito — corriges a página ou a transcrição.

`python3 progress.py` dá o estado e diz-te o que cada resultado dispara.

## O que os resultados obrigam a fazer (§6a, já registado)

Qualquer FN confirmado obriga a expandir o lexicon com o vocabulário de setor desse
paper, re-correr o detector (b) e triar os candidatos novos. **A regra de fecho é zero
candidatos novos numa passagem completa** — não é «acabei a lista». Três ou mais FN
confirmados obrigam a discutir com o orientador um re-screen sectorial do corpus antes
de travar o roster.

## Ordem da fila

Ordenada por especificidade do sinal, decrescente: termos inequívocos (`refinery`,
`clinker`, `blast furnace`, `ammonia`, `paper mill`…) pesam mais que os ambíguos
(`steel`, `cement`, `petroleum`, que aparecem em qualquer introdução), e uma flag de
modelo (⚑) soma. Se parares a meio, paraste no sítio menos mau.

`FILA_A.md` e `FILA_B.md` são as listas legíveis; `QUEUE_A.json` / `QUEUE_B.json` o que
as ferramentas leem.

## O que isto não é

Não é adjudicação de pertença ao Corpus B por parte de nenhum modelo. Os detectores
produzem **sinal**; o veredicto é teu, e é o único que conta.
