# Verificação de citações do Stage C — instruções e codebook

Estás a verificar valores codificados por outro modelo a partir de artigos científicos (revisão de âmbito sobre modelos de desempenho energético, EnPI/EnB, em indústrias de processo contínuo). Para cada item tens: o valor registado (`orig`), a citação (`quote`) e a página física (`page`). Em `pages[key]` tens o texto extraído dessa página e das adjacentes.

Para cada item decide, lendo a citação no seu parágrafo:
1. A citação está na página indicada (ou numa adjacente)? O texto extraído pode ter hifenização, colunas intercaladas e ligaduras (ﬁ, ﬂ); isso não é falha.
2. A citação, lida no contexto do parágrafo, sustenta o valor registado?
3. Se não sustenta, qual seria o valor certo, escolhido SÓ entre os valores permitidos abaixo?

Sê rigoroso e conservador. Não inventes. Não infiras causas que o artigo não nomeia. Na dúvida, marca dúvida — é para isso que existe: o revisor humano só vai ler os itens em que marcas dúvida, por isso uma confirmação tua que esteja errada passa sem revisão. Confirma com confiança alta só quando a frase, lida no seu parágrafo, justifica claramente o valor.

## Definições (do protocolo de extração)

**Mecanismo vs. limitação do estudo vs. barreira.** Mecanismo = limitação DO MODELO de desempenho energético: condiciona se o modelo pode ser construído ou confiado. Limitação do estudo = um estudo maior/diferente resolveria sem mudar o modelo (amostra, acesso a dados, âmbito). Barreira = pessoas, dinheiro, organização, manutenção. Propor trabalho futuro não é limitação. Data quality e data length só são mecanismo se o artigo declarar a consequência para construir/usar o modelo.

**claim_status** (mecanismos):
- `general` — propriedade de métodos em princípio: definição, afirmação sobre regressão em geral, cautela tirada da literatura. Uma definição de heteroscedasticidade é general mesmo num artigo de caso.
- `applied to the case` — afirmado sobre o modelo DESTE estudo (sem ser mostrado com os dados).
- `empirically demonstrated` — mostrado com os dados DESTE estudo (resultado, figura, teste, valor).

**mechanism_cause** — só a causa física/operacional que o artigo NOMEIA; `not stated` é a resposta normal. Valores: fouling; catalyst deactivation; feedstock quality or composition change; product mix or grade change; equipment degradation or ageing; operating mode or campaign change; ambient conditions; plant or process modification; concurrent improvement programme; other; not stated.

**mechanism_effect_on_model** — o que faz ao modelo. Valores: non-stationarity of the relationship (a relação do PROCESSO muda); baseline drift or expiry (o MODELO/baseline caduca e tem de ser refeito); validity envelope exceeded; statistical misspecification; observability gap — quantity not measured; data quality — missing, erroneous or discontinuous data; insufficient data length for the model; multi-product allocation; baseload or non-productive energy; cross-site comparability; indicator not meaningful as defined; other; not stated.

**adaptation** — rolling window; segmented baseline; change-point; additional normalisation variable; hybrid physical-statistical; online re-estimation; outlier exclusion; weighted estimation; normalisation to a reference product; improved metering; other.
**status** — proposed (futuro, recomendação, conclusões "poderia/deveria"); implemented (feito no estudo); evaluated (comparado com uma alternativa no estudo).
**normative_framing** — ISO 50001/50006 explicit (a adaptação é justificada citando a norma); implicit (vocabulário da norma — EnPI, EnB, variáveis relevantes — sem a citar para esta adaptação); absent.
**addresses_mechanism** — K-id do mecanismo que o artigo liga EXPLICITAMENTE a esta adaptação; vazio se não liga. Nunca inferir a ligação.

**C5 data_origin** — dedicated meter; site meter; invoice or utility bill; process historian tag; calculated from process data; laboratory assay; simulation; not reported.
**C5 boundary** — exact; allocated by rule; allocated by estimate; mismatch acknowledged; not reported. Origem e fronteira são independentes.
**C6 regime** — not stated; explicitly none in period; fixed, not mentioned; periodic, interval stated; event-triggered, trigger stated; rolling window; online or adaptive. Regime declarado só se o artigo diz quando/como a baseline é refeita.
**C7 statement** — stated with numeric bounds (dá limites numéricos de validade do modelo); stated qualitatively; not stated.
**C8 OOS status** — reported (erro em dados NÃO usados no ajuste: hold-out, validação cruzada, período de teste); not reported; not applicable. R² de treino não é validação fora da amostra.
**C13** (data_available / code_available) — yes; partial (algumas instâncias); no; not reported; not applicable. Dados tabelados no próprio artigo contam como dados disponíveis só se forem os dados usados no modelo.

## Output

Escreve um ficheiro JSON (lista) com um objeto por item, TODOS os itens do lote:
{"id": "MEC-001", "citacao_na_pagina": true|false, "veredicto": "confirma" | "corrige" | "nao_sustenta" | "retirar",
 "correcoes": {"campo": "novo valor"},   // só se veredicto = corrige; campos: effect, cause, claim, adaptation, status, framing, addresses, value
 "retirar_motivo": "...",                 // só se retirar (não é limitação do modelo / duplicado / outro)
 "confianca": "alta" | "media" | "baixa",
 "duvida": true|false,                    // true se confianca != alta OU veredicto != confirma
 "razao": "≤ 2 frases em português europeu, concretas",
 "evidencia": "≤ 25 palavras do texto da página que decidem a questão"}
