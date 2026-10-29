# Manual — Emenda 3: verificação tardia (14–31 out. 2026)

O que vais fazer: executar, por esta ordem, os instrumentos da Emenda 3 ao TDW6C. São quatro desvios registados feitos agora (D13, D11, D10, D14) e a verificação humana do Corpus B que substitui o D7. A bancada (`bancada.py`) mostra-te cada item e guarda cada decisão. O `relatorio.py` transforma tudo nos números do artigo.

**Prazo duro:** submissão até **31 out.** (waiver de APC). A execução fecha a **29 out.**, que é a data escrita na emenda. O que não estiver feito nessa data é relatado como não feito.

---

## Mapa da pasta `level3_extraction/verificacao_2026-10/`

| Ficheiro | Para quê |
|---|---|
| `MANUAL.md` | este manual |
| `lexico_camada_A.json` | léxico da camada A; deposita-o junto com a emenda |
| `AMENDMENT_FILED.txt` | interlock: crias na etapa 0; sem ele nada sorteia |
| `emenda/` | cópia **exata** do ficheiro que depositares no OSF |
| `dados/` | resumos do OpenAlex (já lá estão), export do Rayyan (etapa 0), exports do D14 (etapa 8) |
| `build_tasks.py` | sorteia e gera `tarefas/` (corre uma vez, depois do depósito) |
| `bancada.py` | a interface, em http://127.0.0.1:8765 |
| `tarefas/` | o que a bancada mostra; `tarefas/_ref/` tem as referências ocultas — **não abras** |
| `respostas/*.jsonl` | as tuas decisões; só se acrescenta, nunca edites à mão |
| `relatorio.py` | gera `RESULTADOS.md` + `resultados.json` |
| `d14_yield.py` | rendimento por string (etapa 8) |

Só precisas de `python3`, sem pacotes. Corre tudo a partir de `~/LocalResearch/Screening/level3_extraction`.

---

## Calendário

| Dia | Etapa | Horas (tuas) |
|---|---|---|
| Qua 14 – Qui 15 | **0** · rever, depositar e gerar tarefas | 1–1,5 |
| Qui 15 – Sex 16 | **2** · D13 exclusões; **3** · D11 reteste | 2–3 + 3–4 |
| Sáb 17 – Dom 18 | **4** · D7·A ausências | 3–5 |
| Seg 19 | **5** · D7·B 80 células | 5–6 |
| Ter 20 – Qui 22 | **6** · D10 auditoria Level-A | 10–13 |
| Sex 23 – Seg 26 | **7** · D7·C mapa de refinação | 8–13 |
| uma noite com b-on | **8** · D14 | 1–2 |
| Ter 27 – Qua 28 | **9** · relatório e atualização do artigo | 6–8 |
| Qui 29 | Mário revê; depósito dos registos no OSF | — |
| Sex 30 | **10** · submissão (31 fica de folga) | 1–2 |

Total: cerca de 40–55 h. A ordem não é estética: é a da emenda (§7). O D13 e o D11 vêm primeiro porque podem mudar quem está no Corpus A ou B. Não a trocas sem registar porquê.

---

## Etapa 0 · Rever, depositar e gerar as tarefas (hoje–amanhã)

**0.1 Rever a emenda** (`OSF_Amendment_TDW6C_A3_late-validation_2026-10-14.docx`). Confirma em especial:
- §1: a frase "not prospective with respect to the review's results". É verdade e é o que te protege; não a suavizes.
- §3.1: a escalada torna-se **vinculativa** com um único falso negativo na amostra aleatória do D13. Se não aceitas re-rastrear os 326 nesse caso (≈ 11 h), muda isto **antes** de depositar, nunca depois.
- §3.2: a escalada do reteste com mais de um flip no mesmo campo implica re-decidir até 67 decisões (≈ 6 h). Mesmo raciocínio.
- §4.2: n = 80 células. Podes baixar para 60 antes do depósito; depois, não.
- §4.3: os 13 relatórios da Tabela A1 são os do mapa do artigo.

**0.2 Export do Rayyan com resumos — antes do `build_tasks`.** Hoje 126 dos 326 excluídos não têm resumo (o OpenAlex deu 200). O censo do léxico do D13 corre sobre título + resumo, por isso os resumos têm de entrar **antes** do sorteio.
- No Rayyan: abre a revisão → *Export* → CSV, com *abstracts* incluídos.
- Grava como `verificacao_2026-10/dados/rayyan_export.csv`.
- O script aceita colunas `key` + `abstract`; se faltar a `key`, liga pelo título.
- Se o Rayyan não der os resumos, segue sem eles. O D13 regista a fonte de cada resumo e conta à parte os que não o têm.

**0.3 PDF da emenda.** No Word: *Ficheiro → Guardar como → PDF*. Deposita o PDF, como fizeste com a C-2.3.

**0.4 Depósito no OSF.** Projeto **wh62r** → *Files* → *OSF Storage* → *Upload*:
- o PDF da emenda;
- `lexico_camada_A.json`.

Abre o PDF no OSF e copia o **GUID** do URL (`osf.io/xxxxx`, cinco caracteres).

**0.5 Cópia local e interlock.**
```bash
cd ~/LocalResearch/Screening/level3_extraction
mkdir -p verificacao_2026-10/emenda
cp ~/Downloads/OSF_Amendment_TDW6C_A3_late-validation_2026-10-14.pdf verificacao_2026-10/emenda/
shasum -a 256 verificacao_2026-10/emenda/*.pdf
cat verificacao_2026-10/AMENDMENT_FILED.txt.template   # copia, preenche e grava sem o .template
```
Os campos são `deposited:` (AAAA-MM-DD), `osf_file:` (GUID) e `sha256:` (o hash acima). O `build_tasks` recusa correr se o hash não bater com um ficheiro em `emenda/`.

**0.6 Gerar as tarefas e congelar o sorteio.**
```bash
python3 verificacao_2026-10/build_tasks.py
git add verificacao_2026-10 && git commit -m "Emenda 3: depositada (OSF <GUID>), tarefas sorteadas seed 44"
```
O commit data o sorteio antes de veres qualquer item. **Não** voltes a correr com `--force` sem escrever no log porquê.

O que deves ver, aproximadamente:

| Módulo | Tarefas |
|---|---|
| d13 | 13 + 50 (muda com os resumos do Rayyan) |
| d11 | 30 |
| d7a | ≈ 65 |
| d7b | 80 |
| d7c | 13 |
| d10 | 40 |

---

## Etapa 1 · Usar a bancada

```bash
python3 verificacao_2026-10/bancada.py
```
Abre-se o browser em http://127.0.0.1:8765. Para parar: Ctrl+C. Para retomar, corre outra vez: o estado vem dos ficheiros.

- **Topo:** um separador por módulo, com progresso e tempo gasto (o tempo por item é medido automaticamente e entra no relatório).
- **Esquerda:** a lista de itens. ○ por fazer · ● laranja = decisão cega confirmada, falta revelar/concluir · ● roxo = feito. "Só pendentes" filtra a lista.
- **PDF ↗** abre o PDF numa aba nova, já na página certa quando há página.
- **Cmd+Enter** carrega no botão principal do rodapé.
- **Rascunhos:** o que escreves num item fica guardado no browser até gravares. Mesmo assim, não deixes itens a meio.
- **Módulos cegos (D11, D10, D7·C):** primeiro decides, depois **confirmas (irreversível)**, depois revelas a referência, depois concluis. A bancada não deixa revelar sem confirmar, nem reescrever uma decisão confirmada. Cada revelação fica registada com hora.
- **Fim do dia:** `git add verificacao_2026-10/respostas && git commit -m "respostas <dia>"`.

**Regras que não partes:**
1. Não abres `tarefas/_ref/`, os formulários, os dossiers, a tese nem o artigo enquanto fazes um item cego. A bancada não te consegue impedir; és tu que garantes.
2. Não editas `respostas/*.jsonl`. Se te enganaste num módulo não cego, volta ao item e grava outra vez: fica a última, com o histórico. Num módulo cego, o erro fica e explicas na nota da conclusão.
3. No D10 segues a **ordem da lista**, que é a ordem do sorteio. Só assim um corte a 30 continua a ser uma amostra aleatória.
4. Relatas tudo, incluindo o que corre mal.

---

## Etapa 2 · D13 — exclusões no rastreio (2–3 h)

**O que é:** 13 registos excluídos que o léxico de processo contínuo apanhou (censo) mais 50 sorteados entre os restantes. Para cada um, decides se a exclusão se mantém.

**Como decidir.** Usa o critério de rastreio registado: o registo **podia** apresentar, propor, avaliar ou criticar um modelo EnPI/EnB? Na dúvida, passava ao texto integral. Não é a pergunta de elegibilidade; é "devia ter ido ver o PDF?".
- Sem resumo: abre o DOI. Se mesmo assim não houver resumo, decide pelo título e escreve-o no motivo ("só título").
- Os *chips* preenchem motivos frequentes; edita se não servirem.

**Se marcares "devia ter seguido":**
- procura o PDF e decide a elegibilidade (Corpus A? Corpus B?);
- regista em `verificacao_2026-10/dados/d13_seguimento.md` a chave, a decisão, a página e a citação;
- é relatado pelo nome como inclusão tardia, **não** entra nas contagens.

**Escalada (vinculativa):** se **algum** dos 50 da amostra aleatória for "devia ter seguido", re-rastreias os títulos e resumos dos restantes excluídos antes da submissão. Avisa-me e gero o módulo extra.

## Etapa 3 · D11 — teste–reteste (3–4 h)

**O que é:** 30 das tuas 90 decisões de setembro (67 de elegibilidade, 23 de pertença ao Corpus B), sorteadas. Decides de novo, só a partir do PDF.

**Como:**
1. Lê a pergunta e o critério (o botão "Critérios" abre o prompt da fase 1).
2. Abre o PDF e decide Sim ou Não. Regista a página e a citação, ou "não reportado após leitura integral" com a fundamentação.
3. Confirma. Depois revela a decisão original.
4. Se houver **FLIP**, re-adjudicas: valor final, evidência e porque divergiram. Esse valor final é o que conta para o corpus.

**Escalada:** mais de um flip **no mesmo campo** obriga a re-decidir todas as outras decisões desse campo entre as 90 (até 67 ou até 23). Avisa-me e gero o módulo. Cada flip re-adjudicado que mude a pertença ao Corpus A ou B muda as contagens do artigo.

## Etapa 4 · D7·A — censo de ausências por léxico (3–5 h)

**O que é:** cada unidade é um relatório × uma família de termos. Só aparecem as unidades com ocorrências; as outras ficam registadas como "sem ocorrência" automaticamente. Começa pelo núcleo T, F, K, C, Q; R e V só no fim, se houver tempo.

**Ecrã:** à esquerda, o que a extração codificou nesse campo; à direita, cada ocorrência com contexto e link para a página.

**Decisão:**
- **(a) nenhuma ocorrência relevante:** o termo aparece, mas não no sentido da família. Exemplo: "regeneration" em queimadores regenerativos, para K.
- **(b) relevante e já codificada:** a extração já tem isto.
- **(c) relevante e NÃO codificada:** omissão. Página, citação, campo afetado e valor corrigido são obrigatórios.

**O que conta como relevante, por família:**

| Família | Conta se… |
|---|---|
| **T** | o modelo é avaliado em dados que não usou no ajuste. Anota **sempre** se esses dados são de um período **posterior** ao do ajuste (teste em bloco temporal), porque é isso que o artigo afirma que nunca acontece. Uma partição aleatória 80/20 é fora da amostra mas **não** é bloco temporal. |
| **F** | fouling, depósitos ou degradação são apontados como causa de mudança na relação energética ou de erro/limitação do modelo. Uma limpeza de equipamento descrita como medida de poupança não conta, a não ser que o texto a ligue ao modelo. |
| **K** | atividade, desativação, regeneração ou ciclo do catalisador apontados como essa causa. |
| **C** | código ou dados do modelo disponíveis (repositório, suplementar, a pedido). |
| **Q** | qualidade ou composição da carga ou do produto usada ou discutida como variável explicativa ou de normalização. |
| **R** | uma regra ou prática para re-estimar ou atualizar o modelo ou a baseline. |
| **V** | um domínio de validade para usar o modelo. |

## Etapa 5 · D7·B — 80 células (5–6 h)

**O que é:** 80 das 350 células em que assentam os resultados do Corpus B, sorteadas. Cada uma mostra o valor atual (já com as decisões de setembro), a citação e a página.

**Decisão:**
- **Correto**;
- **Incorreto**, com o valor certo;
- **Não determinável**, com a razão (é excluído do denominador e relatado à parte).

As definições dos valores estão em `stage_c/PROMPT_EXTRACTION.md` e `stage_c/verification_v1/verificacao_modelo/CODEBOOK_verificador.md`. Julga o valor, não a citação: se o valor está certo mas a citação é fraca, é "correto" com nota.

## Etapa 6 · D10 — auditoria Level-A (10–13 h, o bloco mais pesado)

**O que é:** 40 relatórios do Corpus A, sorteados como no `audit_sampler.py`. Para cada um extrais **às cegas** os campos Level-A em que os dois modelos concordaram. Os outros campos aparecem listados como "fora da auditoria", porque células divergentes ou de uma só superfície não entram no n_v. Não pedir esses campos não muda a métrica.

**Como:**
1. Abre o PDF; as definições estão nos botões *Definições (stage2)* e *Tipo de artigo (stage1)*.
2. Preenche cada campo:
   - enum: "(sem valor no texto)" se o artigo não diz;
   - multi: marca `none` se nenhum se aplica;
   - texto: vazio = sem valor.

   Página e citação são opcionais, mas ajudam quando revelares.
3. Confirma e revela. Para cada célula, classifica a diferença:
   - **igual**;
   - **erro da extração**;
   - **erro meu (extração certa)**: voltaste ao PDF e a extração tinha razão;
   - **equivalente após normalização**: o mesmo conteúdo escrito de outra forma.

   No texto livre (país, setor), "igual" significa sem diferença substantiva; se não for, justifica.
4. **Métrica registada = diferença bruta** (o que confirmaste às cegas vs o valor concordante). A tua classificação aparece ao lado, como "adjudicada".

**Escalada:** e_v ≥ 3 num campo obriga a recheck desse campo no corpus todo. Se não couber até 29 out., o campo é relatado com a marca de ter atingido o limiar.

**Corte permitido:** se o tempo não der, paras aos **30** (sempre um prefixo da lista).

## Etapa 7 · D7·C — mapa de refinação/petroquímica (8–13 h)

**O que é:** os 13 relatórios do mapa do artigo, lidos de ponta a ponta, com os valores codificados escondidos até confirmares.

**Atenção à honestidade:** **não é blind-first**. Já viste estes valores (mapa, Tabela A4, dossiers). O texto diz "valores ocultados durante a leitura, após exposição prévia". Mesmo assim, lê o PDF como se não soubesses.

**Os cinco campos** (o nível mais forte entre os modelos do relatório):

| Campo | Opções |
|---|---|
| C5 · fronteira | exata / alocada (por regra ou estimativa) / desajuste reconhecido / não reportada |
| C6 · re-estimação | declarada e executada / declarada, não executada / fixa ou não declarada |
| C7 · domínio de validade | limites numéricos / qualitativo / não declarado |
| C8 · fora da amostra | reportado / não reportado / não aplicável |
| Bloco temporal | teste em observações posteriores ao ajuste: sim / não / não aplicável |

Cada campo leva evidência (página + citação, ou "não reportado após leitura integral"). Depois da revelação escolhes o valor final; se for diferente do teu ou do codificado, a razão é obrigatória.

## Etapa 8 · D14 — rendimento por string (1–2 h)

Precisas do acesso b-on (VPN ou rede NOVA). As strings estão no protocolo, §4.1:

**String A (Scopus):**
```
TITLE-ABS-KEY("ISO 50001" OR "ISO 50006") AND PUBYEAR > 1995 AND DOCTYPE(ar OR cp OR re)
```

**String B (Scopus):**
```
TITLE-ABS-KEY( ("energy performance indicator*" OR "EnPI" OR "energy baseline*" OR "EnB" OR "energy performance measurement" OR "energy performance monitoring") AND ("industrial" OR "industry" OR "manufacturing" OR "facility" OR "organization" OR "management system" OR "energy management" OR "ISO 50001" OR "continuous process" OR "refin*") ) AND PUBYEAR > 1995 AND DOCTYPE(ar OR cp OR re)
```

**No WoS (Core Collection):** troca `TITLE-ABS-KEY` por `TS=`, `PUBYEAR > 1995` por `PY=(1996-2026)` e o `DOCTYPE` por `DT=(Article OR Proceedings Paper OR Review)`.

**Exports e ficheiros:**
- Scopus → *Export* → CSV, com pelo menos *Title*, *DOI* e *Year*.
- WoS → *Export* → *Tab delimited file*, *Full Record*. O limite é de 1000 por export; se passar, exporta em dois e junta.
- Grava em `verificacao_2026-10/dados/d14/` como `scopus_A.csv`, `scopus_B.csv`, `wos_A.txt` e `wos_B.txt`.
- Corre: `python3 verificacao_2026-10/d14_yield.py`.

Anota a data e a hora da pesquisa e as contagens que cada base mostrar: vão para o artigo e para a nota de execução.

## Etapa 9 · Relatório e artigo (27–28 out.)

```bash
python3 verificacao_2026-10/relatorio.py      # RESULTADOS.md + resultados.json
```
Manda-me o `RESULTADOS.md` (e o `D14_RESULTADOS.md`) e eu atualizo o artigo:
- **Tabela A2 (desvios):** a coluna passa a "Executed late (date); results in …" para D10, D11, D13 e D14. O D7 passa a ser descrito pelas camadas A–C. O D12 fica com a razão da §3.4.
- **Métodos, 3.4–3.5:** parágrafo de validação novo; a frase "absences not verified" sai ou muda conforme a camada A.
- **Resultados:** cada contagem que mude é substituída, e diz-se o que mudou.
- **Limitações:** "executados depois de os resultados serem conhecidos" e "não blind-first no Corpus B".
- **Conclusão:** a frase do D7 passa a passado ("was completed…") ou, se algo ficou por fazer, diz exatamente o quê.
- **Data availability:** aponta para o depósito do passo seguinte.

**Depósito dos registos no OSF (wh62r)**, antes da submissão:
- `tarefas/` incluindo `_ref/`;
- `respostas/`;
- `RESULTADOS.md` e `resultados.json`;
- `dados/d14/D14_RESULTADOS.md`;
- os scripts;
- o hash do commit git.

## Etapa 10 · Submissão (30 out.)

- [ ] PDF final compilado, revisto pelo Mário
- [ ] Carta de apresentação: convite do editor, waiver até 31/10, scoping review, nada submetido noutro lado
- [ ] Revisores sugeridos (a MDPI costuma pedir 3–5; sem conflitos de interesse, de países diferentes)
- [ ] Suplementos S1–S3 e checklist PRISMA-ScR (não publicada)
- [ ] CRediT confirmado com o Nuno e o Mário
- [ ] ORCID e afiliações iguais em todo o lado; email pessoal como correspondente
- [ ] Declaração de IA generativa atualizada (a bancada foi escrita com IA; nenhuma decisão foi tomada por IA)

---

## Se o tempo apertar — ordem de corte (já coberta pela emenda)

1. Famílias **R** e **V** do D7·A (2.ª prioridade): ficam por fazer e relatadas como tal.
2. **D14:** fica "não feito".
3. **D10** reduzido de 40 para **30** (prefixo da lista).
4. **D7·C** parcial: relatam-se os relatórios concluídos, pelo nome.

**Nunca se corta** D13, D11, o núcleo do D7·A nem o D7·B: são o que sustenta as afirmações do artigo. Qualquer outro corte, fora destes quatro, é um desvio novo e tem de ser declarado.

## Problemas comuns

| Sintoma | Causa / solução |
|---|---|
| `[interlock] …` | falta ou está errado o `AMENDMENT_FILED.txt`, ou o hash não bate com o ficheiro em `emenda/` |
| A bancada diz "sem tarefas geradas" | corre o `build_tasks.py` (etapa 0.6) |
| O PDF não abre | falta `data/pdfs/<key>.pdf` |
| Porta ocupada | `python3 verificacao_2026-10/bancada.py --port 8800` |
| Confirmaste uma decisão cega errada | não há volta; explica na nota da conclusão. É assim que deve ser. |
