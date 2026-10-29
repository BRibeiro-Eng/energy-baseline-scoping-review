# Corpus A — bibliometria, mapeamento de evidência e PRISMA

O script `run_analysis.py` gera uma galeria HTML, um atlas PDF, figuras individuais
em PNG/PDF/SVG e tabelas CSV. O notebook `corpus_a.ipynb` executa o mesmo script,
mostra a cobertura dos dados e permite consultar figuras e tabelas. Não é necessário
acesso à rede para reproduzir a execução a partir da cache entregue.

## Executar

```bash
cd /Users/bernardoribeiro/LocalResearch/Screening/level3_extraction/bibliometrics
.venv/bin/python run_analysis.py
```

A saída principal fica em `results/union_inclusiva/`. Abrir `index.html` para navegar;
`figures/atlas.pdf` contém todas as figuras e `figures/` contém os ficheiros individuais.

Para executar exclusivamente sobre a lista de A registada:

```bash
.venv/bin/python run_analysis.py --population a
```

Essa saída fica em `results/corpus_a_registado/`. A opção `--output CAMINHO` permite
escolher outra pasta. `--enrich` consulta apenas metadados ainda não existentes na cache;
as respostas existentes não são substituídas. As consultas usam DOI exato, conservam
o fornecedor e a data e isolam discrepâncias de título para revisão.

Noutro ambiente, criar uma virtualenv e instalar `requirements.txt`. As versões
efetivamente utilizadas ficam em `package_versions.json` em cada saída.

## Inconsistência de pertença descoberta na implementação

O documento de fecho declara A=331 e B=42, mas os identificadores não formam conjuntos
aninhados. `corpus_profile.rosters()` produz:

| Conjunto | Publicações |
|---|---:|
| A registado | 331 |
| B registado | 42 |
| A ∩ B | 40 |
| A \ B | 291 |
| B \ A | 2 |
| A ∪ B | 333 |

Os registos `rayyan-472535628` e `rayyan-472535750` têm simultaneamente
`methodological_eligibility=false` e `level_3b=true` nos formulários de origem.
A lista de B fechada em 12/09/2026 também os contém.

A vista principal é, por isso, **A∪B exploratório (333)**: inclui todos os 42
registos de B, uma única vez, sem modificar as decisões de elegibilidade. A outra
vista mantém os 331 de A e contém 40 registos de B. Isto não é uma alteração do
protocolo nem uma adjudicação: é uma análise de sensibilidade enquanto se resolve
a inconsistência. A correção definitiva dos números necessita dessa decisão.

## Estado dos valores de conteúdo

Não existe neste ponto uma tabela Level A integralmente adjudicada. A implementação
mantém cada célula das duas superfícies de extração e usa na vista principal apenas
valores concordantes, marcados como provisórios. Divergências, extrações de uma
única superfície e células ausentes permanecem por resolver. A concordância entre
IA **não constitui validação humana nem estimativa de fiabilidade**.

`tables/model_surface_sensitivity.csv` conserva as distribuições separadas das duas
superfícies. Não se preenchem lacunas escolhendo automaticamente um modelo.
`config/verified_level_a.csv` permite introduzir valores verificados por um revisor:

```csv
paper_id,field,value_json,verified,reviewer,evidence
```

`value_json` deve conter um valor JSON válido. Só linhas `verified=true`, com revisor
e evidência, substituem a célula provisória. Os campos aceites estão em `biblio/data.py`.
Os ficheiros de extração originais são exclusivamente lidos e nunca alterados.

## Análises implementadas

- Produção anual/acumulada, composição temporal por tipo de estudo, fontes,
  concentração, zonas descritivas de Bradford e distribuição de produtividade dos autores.
- Tipos de documento/estudo, estudos multi-site, países dos casos, setores,
  organizações, modelos, normas, protocolos M&V e drivers regulamentares.
- Cruzamentos, comparação de grupos disjuntos B/restante conjunto, interseções
  UpSet, coocorrência de modelos/normas e diagrama aluvial fracionado.
- Redes de coautoria, países e instituições; colaboração internacional e
  educação–empresa; fontes de financiamento e acesso aberto.
- Palavras-chave normalizadas, rede de coocorrência, clusters exploratórios,
  evolução temporal, temas × conteúdo, termos dos títulos e resumos, tópicos NMF.
- Citações OpenAlex, Crossref e contagens históricas do export mantidas separadas;
  distribuição, citações por idade, FWCI fornecido pelo OpenAlex, citações locais,
  autocitações locais identificáveis, rede direta, acoplamento bibliográfico,
  cocitação de referências/autores/fontes, referências mais citadas e idade das referências.
- Cobertura, proveniência de células, filas de normalização e discrepâncias de identidade.
- PRISMA com contagens documentadas, equações verificadas e lacunas explícitas.
- Adaptadores para novos campos de conteúdo e métricas externas, que geram as
  análises automaticamente quando forem disponibilizados dados verificados.

O catálogo HTML e `tables/analyses_pending.csv` distinguem o que foi gerado do que
ainda depende de dados. O código não fabrica gráficos de métricas ausentes.

## Convenções de contagem e interpretação

1. A unidade primária é a **publicação**, não um estudo independente nem uma instalação.
2. Campos de resposta múltipla: cada publicação conta uma vez por categoria/célula;
   somas podem ultrapassar 100%. Nas comparações, os denominadores são os tamanhos
   dos grupos disjuntos; os dados em falta ficam explícitos.
3. O diagrama aluvial distribui peso total 1 por publicação entre todas as combinações.
   As larguras não são contagens integrais. UpSet mostra combinações exatas.
4. Os países de A7 são locais dos casos; os países OpenAlex são afiliações dos autores.
5. O agrupamento setorial por expressões regulares é exploratório e verificável em
   `normalization_sector_mapping.csv`; não altera A8 nem determina a pertença a B.
6. As redes usam limiares documentados nas legendas. Os GEXF permitem inspeção noutras
   ferramentas. Centralidade e clusters não demonstram qualidade ou causalidade.
7. Cocitação por autor/fonte está restrita às 80 referências de maior frequência
   cuja resolução de metadados foi tentada. A cobertura conseguida é indicada.
8. Ausência de metadados não é zero. Citações por idade não são normalização por campo;
   FWCI é uma medida externa que depende da definição e cobertura do fornecedor.
9. Os nomes do export não estão integralmente desambiguados. Não interpretar os rankings
   como avaliação de investigadores ou como a produção completa das instituições.
10. O idioma English é a classificação no export. Títulos traduzidos ou divergentes
    nos fornecedores são enviados para revisão, não usados para alterar a elegibilidade.

## Campos ainda necessários

- `source_strings.csv`: origem A/B/both e evidência do log de pesquisa. A12 está vazio;
  null não significa snowballing. Não confundir strings A/B com Corpus A/B.
- `extended_content.csv`: novos campos, extraídos comparavelmente e verificados:
  variáveis, escala, dados, duração, amostragem, validação, atualização, resíduos,
  incerteza, limites e reprodutibilidade. Campos do B não são generalizados ao A.
- `external_metrics.csv`: atenção em patentes/políticas ou outras métricas, sempre com
  fornecedor, data e fonte. Não se calcula um índice de carreira a partir deste corpus.
- `prisma_pending.json`: totais iniciais por base, duplicados anteriores à triagem e
  registos de snowballing. Null representa **por confirmar**, nunca zero.

## PRISMA e proveniência

O fluxo usa o export atual, os registos de não recuperação/exclusão e a nota de fecho.
O ficheiro histórico `Primeiro assisted screening/prisma_stats.txt` contém decisões
IA preliminares (667 excluídos) e **não substitui** as 326 exclusões do export atual.

Equações verificadas: 925=326+599; 599=3+596; 596=137+459;
459=11+448; 448=117+331. Assim, as exclusões a texto integral somam 128:
10 por idioma, 1 retratação, 117 por elegibilidade metodológica. Os motivos destas
117 necessitam de desagregação validada. A inconsistência dos dois registos B/A
é exibida no rascunho, sem corrigir silenciosamente os totais.

Referências metodológicas e fornecedores:

- [PRISMA 2020 — modelos do fluxograma, CC BY 4.0](https://www.prisma-statement.org/prisma-2020-flow-diagram)
- [VOSviewer — redes e técnicas](https://www.vosviewer.com/features)
- [Bibliometrix/Biblioshiny — famílias de análise](https://www.bibliometrix.org/biblioshiny/)
- [OpenAlex — API](https://help.openalex.org/api/)
- [Crossref — acesso à API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/)

`cache/input_snapshot.json` congela os registos utilizados e os hashes dos ficheiros
de origem. `run_manifest.json` regista hashes do código, configurações e metadados.
Alterar o corpus requer rever a incoerência, guardar a decisão e atualizar
explicitamente o snapshot; uma reexecução normal não altera a composição.

## Verificar

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Os testes verificam a conservação de registos no PRISMA, inclusão de B sem duplicações,
contagens por publicação, semântica de coocorrência, leitura de autores e ausência de
precedência automática para células divergentes. O notebook foi preparado para
executar de cima para baixo e conservar saídas compactas.
