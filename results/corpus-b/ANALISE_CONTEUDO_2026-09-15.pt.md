# Stage C — o que os 41 registos dizem, e o que já dá para escrever
Data: 2026-09-15 · Base: 41 registos validados (0 problemas), 49 applications, 144 modelos,
146 ocorrências de mecanismo, 92 adaptações, 30 dossiers com 642 citações ancoradas.

> **Nível de evidência de tudo o que segue.** Isto é a leitura do extractor, com todas as
> citações ancoradas à página, e nada mais. Não é V1 (verificação humana de cada ocorrência)
> nem V2/V3. Os números servem para decidir onde ler, e para escrever o capítulo depois de
> lidos — não para ir directos para uma tabela de resultados.

---

## 1. Os cinco achados que o corpus dá, e que aguentam escrita

### 1.1 A literatura reporta sintomas, não causas
O eixo `mechanism_cause` está praticamente vazio: **92 de 146 ocorrências (63%) são
`not stated`** e outras 19 são `other` — 76% sem causa física registável. As causas que a tese
antecipava não aparecem: **fouling = 1, desactivação de catalisador = 0, degradação de
equipamento = 1.**

Isto é mais forte do que o R4 registado ("os mecanismos não são os que a tese previu"): os
papers descrevem o que corre mal **ao modelo** e quase nunca dizem o que no processo o causou.
É simultaneamente um achado sobre a literatura e um achado sobre o instrumento — um dos dois
eixos registados devolve quase nada, e isso tem de ser declarado.

### 1.2 O `claim_status` muda a composição do resultado — é a espinha metodológica
**41 de 146 ocorrências (28%) são `general`**: afirmações de manual, não resultados do estudo.
Praticamente o mesmo que o piloto mediu (27% em 30). Mas o que interessa não é a percentagem,
é que **a ordem dos efeitos muda consoante se conta tudo ou só o que é demonstrado**:

| efeito no modelo | papers (todas as ocorrências) | papers (excluindo `general`) |
|---|---|---|
| indicator not meaningful as defined | 16 | 12 |
| non-stationarity of the relationship | 15 | 12 |
| **statistical misspecification** | **13** | **8** |
| **observability gap — quantity not measured** | **12** | **12** |
| data quality — missing/erroneous/discontinuous | 11 | 10 |
| cross-site comparability | 11 | 10 |
| baseline drift or expiry | 7 | 4 |
| multi-product allocation | 6 | 3 |

`statistical misspecification` cai 13→8 e `baseline drift` 7→4: são queixas que a literatura
**repete**. `observability gap` fica 12→12: nunca é afirmação de manual, é sempre coisa que
alguém encontrou no caso. Contar todas as ocorrências mede o que a literatura repete, não o que
demonstra. É este o defeito que o campo tem e que o campo justifica.

### 1.3 A previsão registada sobre efeitos está errada — em duas direcções
O R4 esperava que "observabilidade, alocação e baseline drift dominassem". Não dominam:
lideram `indicator not meaningful as defined` (22 ocorrências), `statistical misspecification`
(20) e `non-stationarity` (18); alocação tem 8 e baseline drift 8. Tem de ser reportado como
contradição da expectativa registada, não silenciado.

### 1.4 Os papers propõem muito, e quase nada ancorado à norma
**37 de 41 papers propõem pelo menos uma adaptação** (92 no total; só 4 não propõem nada).
O **R7 registado — "dois terços não propõem nada" — está invertido.** Duas leituras possíveis, e
ambas têm de ir para o texto: ou a expectativa estava errada, ou o instrumento é generoso no que
conta como adaptação — **30 das 92 (33%) são `other`**, o que é sinal de taxonomia curta.

Já o R6 ("normativamente desancoradas") aguenta-se bem: `absent` 51, `implicit` 32,
**`ISO 50001/50006 explicit` apenas 9 — 10%**.

O R8 ("raramente ligadas ao mecanismo que tratam") está mal formulado: **46 ligam, 46 não.**
Metade não é "raramente". A frase tem de mudar.

### 1.5 Reprodutibilidade: as equações vêm, o resto não
Sobre 41 papers: equações `yes` 24, coeficientes `yes` 12, dados disponíveis `yes` 4,
**código disponível `yes` 0** (40 `not reported`, 1 `partial`). Zero partilha de código num
corpus de 41 papers de modelação energética é um número que se escreve sozinho.

---

## 2. O que sustenta os resultados de instrumento (R10–R13)

| campo | leitura |
|---|---|
| **C7 envelope de validade** (144 modelos) | `not stated` 110 (76%), qualitativo 16, **bounds numéricos 18 (12,5%)** |
| **C6 re-estimação** | `fixed, not mentioned` 93 (65%), `not stated` 18, event-triggered 19, rolling 6, periódico 4, online 4 |
| **C8 out-of-sample** | `reported` 13 (9%), `not reported` 67, `not applicable` 64 · design: `none` 37, held-out 18, só residuais in-sample 7 |
| **C5 origem do dado** (169 entradas) | `not reported` 55, calculado de dados de processo 48, contador dedicado 23, contador de sítio 17, factura 7, simulação 12, tag de historiador 7 |
| **C5 correspondência de fronteira** | `not reported` 77, **`exact` apenas 50 (30%)**, alocado por regra 21, alocado por estimativa 14, mismatch reconhecido 7 |

O R10 — "a quantidade de energia frequentemente **não** é medida na fronteira estudada" — é o
que tem mais peso por unidade de evidência e é o que se lê contra o caso de Sines. A
correspondência exacta é minoria.

---

## 3. Composição do corpus, e o que isso faz à SQ4

Sectores (49 applications): cimento 11, aço e metais 10, petroquímica 7, múltiplos 6,
**refinação 5**, pasta e papel 3, vidro 3, química contínua 2, gases industriais 1, fora dos
registados 1.

`refinery_or_petrochemical_case`: **14 applications com aplicação empírica** (7 refinação +
7 petroquímica), 3 nomeadas sem aplicação, 32 não.

Confirma o que a matriz já dizia: a maioria da evidência de mecanismo está fora da refinação.
Qualquer número tirado dos 11 do núcleo é um número sobre refinação, não sobre a literatura.

---

## 4. Já dá para escrever?

**Dá, e mais do que parece — mas não a parte que ainda não foi verificada.**

**Escrevível agora, sem mais verificação nenhuma:**
- Todo o capítulo de método: protocolo, fluxo PRISMA-ScR, a emenda e os seus três desvios, o
  instrumento e os defeitos encontrados e fechados, o desenho da triagem, e o quadro de níveis
  de verificação. É a parte que a maioria das teses faz mal e esta tem material a sério.
- **Layer A (SQ1, R16–R18)**: não é re-extraída, assenta no instrumento Tier-3 já registado.
  Nada no Stage C muda o que o capítulo pode dizer sobre SQ1.
- A caracterização descritiva do corpus (§3 acima) — **mas só depois de decidires o R0**: hoje
  esses campos não alimentam resultado registado nenhum, e sem R0 é um resultado não registado.

**Escrevível depois de leitura dirigida (não das 1 364 células):**
R1, R5, R6, R8 e R14 são existenciais a V1. São as de melhor rácio evidência/esforço, e o R5 é
a espinha do capítulo.

**Não escrevível como registado:** R2, R3, R7, R12, R13 e parte do R10 são denominadores sobre
os 42 e exigem V3, que a cobertura executada não tem. Reportáveis a V2 sobre as secções lidas,
declarado.

**Bloqueado:** R15 / SQ4 até ao blind-first nos 11.
