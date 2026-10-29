# Estrato II — amostra verificada

O Estrato II são os 122 papers elegíveis, fora do Corpus B, com sinal mas com
`application_strength` em {{mentioned_only, none}}. O §5.3 exclui-os pela sua própria
redacção — *"the paper must apply, validate, or empirically demonstrate"* — pelo que o
filtro não é uma conveniência, é o critério registado. A amostra serve para **limitar o
erro do filtro**, não para decidir pertenças.

Sub-estratificado por risco: IIa tem sinal de sector da lista §5.3 (mais arriscado), IIb não.

| Sub-estrato | N | n | seed | limite sup. 95% se 0/n |
|---|---|---|---|---|
| IIa — sector §5.3 | 81 | 25 | 46 | 11.3% |
| IIb — outro sinal | 41 | 8 | 47 | 31.2% |

Para cada paper da amostra: o sinal é a aplicação do próprio paper, ou uma citação /
menção? Se for aplicação própria num sector §5.3, é um falso negativo do filtro e
dispara o §6a (expansão de léxico + nova passagem do detector (b)).

---

## Amostra IIa

### rayyan-472535361 — `mentioned_only`
- sectores sinalizados: cogeneration / thermal power generation, continuous chemical production, petrochemicals (organic chemistry)
- A8: 'government buildings' · A9: 'buildings'
- The paper is a case study of implementing an ISO 50001 energy management system in the government office buildings of the Saudi Standards, Metrology and Quality Organization (SASO); continuous-industry sectors appear only as passing literature mentions and bibliographic references.
- p.2: `Industrial firms were the earliest adopters, primarily energy-intensive
sectors such as automotive, chemicals, and technology`
- p.4: `industries characterized by high energy consumption, such as manufacturing, chemical
processing, and utilities`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535362 — `mentioned_only`
- sectores sinalizados: cement, lime, clinker
- A8: 'higher education institutions' · A9: 'buildings'
- A systematic literature review of energy management systems (EnMS) applied to higher education institutions' buildings (classrooms, offices, laboratories, campuses) in relation to ISO 50001 — a buildings/education context, not continuous-flow industrial production.
- p.30: `Gonzalez, A.J.; Castrillon, R.; Quispe, E.C. Energy Efficiency Improvement in the Cement Industry Through Energy Management.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535373 — `mentioned_only`
- sectores sinalizados: cement, lime, clinker, flour milling, glass (continuous melting, float lines), pulp & paper
- A8: None · A9: 'not specified'
- The paper empirically demonstrates ISO 50001 energy-management implementation (transformer/SCADA power-quality audits, energy KPIs, CO2 footprint) at an unspecified generic industrial facility; the only ties to continuous-flow sectors (cement, glass, pulp & paper, flour milling) appear solely as bibliographic references, not as the study's application context.
- p.5: `Review of measures for energy efficiency and sustainability in the cement industry worldwide.`
- p.5: `Carbon footprint estimation in glass production in Cuba.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535377 — `mentioned_only`
- sectores sinalizados: pulp & paper
- A8: None · A9: 'buildings'
- The paper applies an ISO 50001/50002-based energy management and photovoltaic optimization methodology to a tertiary office building in Meknes, Morocco; the only continuous-industry reference (pulp & paper) is a citation, not an application.
- p.6: `Energy conservation potential of an energy audit within the pulp and paper industry in Morocco`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535404 — `mentioned_only`
- sectores sinalizados: continuous processes (unspecified), natural gas sweetening / gas processing, petrochemicals
- A8: 'tire industry' · A9: 'discrete manufacturing'
- The paper develops and evaluates machine-learning models to predict steam consumption in a tire manufacturing factory (discrete curing/press operations); petrochemical, gas-sweetening, ethylene and "continuous processes" appear only as cited prior work, not as the application context.
- p.2: `While numerous researchers have paid attention to the 
application of ML for energy efficiency analysis in various 
industries, especially petrochemicals, there still is not an 
ad`
- p.5: `S. Gong, C. Shao, and L. Zhu, “Energy efficiency evaluation in 
ethylene production process with respect to operation classification,”`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535416 — `mentioned_only`
- sectores sinalizados: cement, lime, clinker
- A8: 'higher education buildings' · A9: 'buildings'
- The paper applies an ISO 50001 energy-review methodology to a university campus (higher education buildings) in Cali, Colombia; the only cement reference is a bibliographic citation, not an application context.
- p.14: `Improvement in the Cement Industry through Energy Management. 
In: 2012 IEEE-IAS/PCA 54th Cement Industry Technical Conference.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535481 — `mentioned_only`
- sectores sinalizados: cement, lime, clinker, ceramics, cogeneration, plastics processing / converting, pulp & paper, steel and other primary-metals continuous production
- A8: None · A9: 'mixed'
- Empirical statistical analysis of Italian energy-audit and energy-management-system data across four sectors (plastics product manufacturing, ceramics, retail, banks) to assess the impact of monitoring/ISO 50001 on energy performance improvement actions; registered continuous-flow sectors (steel, paper, cement) appear only as dataset descriptors or citations.
- p.2: `with particular importance to the plastic (8%), iron and steel
(9%), food (6%), textile (3%), and paper (2%) industries.`
- p.2: `with particular importance to the plastic (8%), iron and steel
(9%), food (6%), textile (3%), and paper (2%) industries.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535487 — `mentioned_only`
- sectores sinalizados: aluminium (fabrication/extrusion, not primary smelting), continuous chemical production (fertilizers), pulp & paper, steel and other primary-metals continuous production
- A8: None · A9: 'mixed'
- The paper proposes and validates an ISO 50001-based energy management maturity model for Chinese industrial enterprises, empirically tested on three discrete-manufacturing case firms (aluminium-section and bathroom-accessory building-materials makers and a semiconductor component maker), with continuous-flow sectors like steel, fertilizer and pulp & paper only mentioned in passing or references.
- p.38: `Most large steelmakers in China have deployed similar information technologies and achieved Automatic Meter Reading over the past decade.`
- p.46: `Discussion on the establishment and operation effect of energy management system in chemical fertilizer enterprises.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535542 — `mentioned_only`
- sectores sinalizados: cement, glass / pulp & paper / cement, petroleum refining / continuous chemical production (ammonia), pulp & paper, sugar processing
- A8: 'manufacturing' · A9: 'mixed'
- A systematic literature review of energy-efficiency assessment methods and tools for manufacturing systems; it catalogues reviewed studies (some in cement, pulp & paper, refining) but does not itself apply, validate, or demonstrate anything in a specific continuous-flow production context.
- p.3: `They are used to analyse only speciﬁc
industrial processes (e.g. industrial ammonia synthesis, petroleum
reﬁning)`
- p.5: `the manufacture of other non-metallic
mineral products, such as cement (4)`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535584 — `mentioned_only`
- sectores sinalizados: steel and other primary-metals continuous production (lead melting), steel and other primary-metals continuous production (lead refining), steel and other primary-metals continuous production (lead refining/smelting)
- A8: 'lead-acid battery (LAB) manufacturing' · A9: 'discrete manufacturing'
- The paper applies an ISO 50001-based energy management methodology to reduce electricity consumption in a lead-acid battery manufacturing (discrete assembly) plant in Colombia; in-plant lead refining/melting is mentioned as an upstream metals-processing step but is not the study's focus.
- p.9: `Battery manufacturing starts with refining scrap lead and lead ores (coming from LAB recycling facilities and lead mines), to produce pure lead and lead alloys. The refined lead is`
- p.15: `The remaining 31% of the energy originates from the natural gas used to generate heat e.g. the refining of the lead scrap.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535663 — `mentioned_only`
- sectores sinalizados: steel / petrochemicals
- A8: 'mine' · A9: 'continuous process'
- A practitioner case study of implementing and integrating an ISO 50001 energy management system at New Gold's New Afton underground gold mine (ore milling/mining), which is out of scope; the only Corpus-B sector terms (steel, petrochemical) appear solely in the author's biographical note.
- p.12: `He began his career as an
engineer in South African gold mines and later in the steel and pet-
rochemical industries.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535691 — `mentioned_only`
- sectores sinalizados: petroleum refining / petrochemicals / steel, pulp & paper, steel / cement / pulp & paper / petroleum refining / petrochemicals
- A8: None · A9: 'mixed'
- The paper compares three national government programs (mandatory in Japan, tax-incentive in Sweden, market-based certification in the US) for accelerating industrial uptake of ISO 50001 energy management systems; continuous-flow sectors like steel, cement, paper, and refining appear only as illustrative regulated/energy-intensive industries, not as an application context.
- p.9: `Currently set business lines: Iron and steel, electric power, 
cement, paper manufacturing, petroleum refining and chemical.`
- p.17: `Companies that are not participating in the PFE include a large number 
of small and medium enterprises (SME), refineries, and some chemical 
and steel companies (which already hav`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535734 — `mentioned_only`
- sectores sinalizados: petroleum refining, petroleum refining / petrochemicals
- A8: 'oil and gas industry' · A9: 'continuous process'
- The paper describes ADCO's implementation and ISO 50001 accreditation of an energy management system across its upstream onshore oil and gas production operations (extraction, gas/water injection, pumping, compression); refineries/petrochemical plants are only referenced generically as industry activities and as downstream recipients of ADCO's crude.
- p.2: `Refining/petrochemical plants
Seismic
Process plants`
- p.3: `Some of the oil and gas used directly by the industry is
transformed into electricity and heat, especially in the case of refineries and other large facilities.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535855 — `mentioned_only`
- sectores sinalizados: cement / glass, cement, lime, clinker, non-ferrous primary metals, non-ferrous primary metals (copper), petrochemicals / continuous chemical production, petroleum refining, pulp & paper, steel / cement / petrochemicals, steel and other primary-metals continuous production, thermal power plants / power generation
- A8: 'manufacturing' · A9: 'mixed'
- An econometric (PSM-DID) study of how ISO 50001 energy management certification affects energy intensity across Chinese manufacturing firms broadly (2007–2016 tax survey data); continuous-flow sectors appear only as pooled sample industries or cited case studies, not as the paper's specific application context.
- p.3: `Pelser et al. (2018) examined ISOEnMS’s impact on the energy performance of a cement manufacturing firm in South Africa.`
- p.3: `their study focused exclusively on large steel enterprises. Specifically, they examined data from 54 large steel firms obtained from the China Iron and Steel Industry Association.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536035 — `mentioned_only`
- sectores sinalizados: cement, lime, clinker, glass (continuous melting, float lines), pulp & paper; steel and other primary-metals continuous production, steel and other primary-metals continuous production
- A8: 'biscuit manufacturing' · A9: 'discrete manufacturing'
- The paper proposes exergy-based energy management guidelines (ISO 50001 format) and applies them via a case study of a biscuit manufacturing facility (discrete/food manufacturing), with Corpus B sectors like paper mill, steel, cement and glass appearing only as cited prior-work examples.
- p.3: `For examples, see Wall [21] (a paper mill and a steel plant), Atmaca and Yumrutas [22] (a cement plant)`
- p.3: `Atmaca and Yumruta¸s [22] (a cement plant)`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536345 — `mentioned_only`
- sectores sinalizados: cogeneration, ethanol distillation, pulp & paper, sugar milling / food processing
- A8: 'sugar industry' · A9: 'continuous process'
- The paper applies energy analysis and pinch/heat-integration methods (Aspen Energy Analyzer) to a real sugar cane mill to identify energy and water savings and design a heat exchanger network; sugar milling is not a listed Corpus B sector, and the only listed-sector mention (pulp & paper) is a stray phrase.
- p.2: `Energy management in the paper manufacturing process is based on the Cuban standard ISO 50001: 2019 and a methodology 
for energy use [9].`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536400 — `mentioned_only`
- sectores sinalizados: cement, lime, clinker, chemical production, foundries / primary metals, glass (continuous melting, float lines)
- A8: 'pharmaceutical industry' · A9: 'discrete manufacturing'
- Empirical study of 84 Italian pharmaceutical-manufacturing (NACE 21.20, drug formulation/mixing/filling/finishing — batch, not continuous) energy audits to derive energy performance indicators and energy-saving actions; continuous-flow sectors (cement, glass, foundries, chemicals) appear only as methodological or comparison references.
- p.29: `A methodology to characterize productive sectors. the italian cement industry case study. Energies`
- p.18: `has already been used for other branches of Italian productive sectors,
namely glass [36] and foundries [37].`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536439 — `mentioned_only`
- sectores sinalizados: cement, lime, clinker
- A8: 'private healthcare sector' · A9: 'buildings'
- The paper defines and validates energy performance benchmark indicators for the Italian private healthcare sector (hospitals) using mandatory energy audit data; its application context is healthcare buildings, not continuous-flow industrial production.
- p.16: `From Energy Audit to
Energy Performance Indicators (EnPI): A Methodology to Characterize Productive Sectors. The Italian Cement Industry Case
Study. Energies 2021, 14, 8436.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536454 — `mentioned_only`
- sectores sinalizados: generic continuous production (cited reference), pulp & paper
- A8: 'food industry' · A9: 'discrete manufacturing'
- The paper develops and applies an energy end-use taxonomy, performance indicators, and a planning framework to the Swedish food industry (meat, beer, biscuit, dairy, fruit/vegetable, sauces, flour, pasta), which is batch/discrete food processing; Corpus-B sectors (pulp & paper, continuous production) appear only as cited references.
- p.3: `The same boundary levels are adopted in the study by Andersson and Thollander on the Swedish pulp and paper industry [30]`
- p.17: `Andersson E, Thollander P. Key performance indicators for energy management in the Swedish pulp and paper industry. Energy Strategy Rev 2019;24:229–35.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536494 — `mentioned_only`
- sectores sinalizados: steel and other primary-metals continuous production
- A8: 'lead-acid battery manufacturing' · A9: 'discrete manufacturing'
- The paper develops and applies an energy-management/benchmarking procedure for compressed air systems, empirically demonstrated in a lead-acid battery manufacturing plant (discrete manufacturing); a blast-furnace/iron-production case appears only as a cited literature example.
- p.4: `The
simulation techniques were also used to deﬁne the optimal pres-
sure in a CAS during in a blast furnace operation in an iron pro-
duction plant [21]. Results showed that reduci`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536522 — `none`
- sectores sinalizados: cogeneration / CHP / power generation, pulp & paper, steel and other primary-metals continuous production
- A8: 'engineering industry' · A9: 'discrete manufacturing'
- The paper develops and validates an energy end-use taxonomy, CO2 analysis, and energy performance indicators for the Swedish engineering industry (discrete manufacturing of metal products such as machined tools, automotive parts, springs, fasteners, and sheet metal), not continuous-flow production.
- p.23: `Keyperformance indicators for energy management in the Swedish pulp and
paper industry. Energy Strategy Rev. 2019, 24, 229–235.`
- p.22: `Analysis of the Most Eﬀective Energy Eﬃciency Opportunities in Manufacturing
Primary Metals, Plastics, and Textiles Small- and Medium-Sized Enterprises.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536589 — `mentioned_only`
- sectores sinalizados: continuous chemical production / petrochemicals, glass (continuous melting, float lines)
- A8: 'medical devices' · A9: 'discrete manufacturing'
- The paper develops and applies energy KPIs (EnPC, CUSUM, normalised data) in a discrete, batch-based Medical Devices production facility, tracking production steps and value streams; chemical-industry and glass-plant references appear only as cited comparators.
- p.5: `Energy intensity indicators in the chemical industry are calculated with regard to the Best Practice Technology (BPT) available; e.g. total energy consumption versus BPT.`
- p.6: `Song et al. (2014) describe the energy efficiency (EE) index of a chemical plant as the ratio of
target (Best Practice) energy consumption over actual energy consumption.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536690 — `mentioned_only`
- sectores sinalizados: petroleum refining / petrochemicals
- A8: 'biomedical device manufacturing' · A9: 'discrete manufacturing'
- The paper develops and applies energy performance indicators (metering of compressed air, chilled water, HVAC) in a multinational biomedical device manufacturing facility involving casting, grinding, cleaning and polishing — discrete manufacturing, not continuous-flow production; petroleum/petrochemical sectors appear only as a passing benchmarking citation.
- p.3: `the primary
industries where it exists: the petroleum and petrochemical
sectors [26]`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536756 — `mentioned_only`
- sectores sinalizados: cement / glass, corn wet milling / corn refining, petroleum refining / petrochemicals
- A8: 'automobile manufacturing' · A9: 'discrete manufacturing'
- The paper develops and applies a statistically-based ENERGY STAR plant energy performance indicator for U.S. automobile assembly plants (discrete manufacturing); petroleum, petrochemical, cement, glass and corn refining are only mentioned in passing.
- p.2: `The petroleum and petrochemical industries each support plant-wide surveys 
conducted by a private company and are provided with benchmarks that address energy use and 
other opera`
- p.9: `Finally, EPA is working with additional industries (including cement, 
corn refining, and glass) to create EPI's to help motivate greater energy efficiency and to enable 
them to c`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536757 — `mentioned_only`
- sectores sinalizados: corn refining / wet corn milling, corn refining / wet corn milling (food & agricultural processing), steel and other primary-metals continuous production / cement, lime, clinker
- A8: 'corn refining' · A9: 'continuous process'
- The paper empirically applies stochastic frontier analysis to build an ENERGY STAR energy-performance benchmarking tool for the U.S. wet corn milling (corn refining) industry, a continuous food/agricultural processing sector not among the eight registered Corpus B sectors; steel and cement are only mentioned illustratively.
- p.5: `is less likely to be the case for process industries, like steel or cement.`
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

## Amostra IIb

### rayyan-472535415 — `mentioned_only`
- sectores sinalizados: continuous industrial operation (cooling utility), oleochemical / glycerin production, oleochemical / soap-glycerin processing
- A8: 'soap plant' · A9: 'continuous process'
- The paper applies and validates an ISO-50001-based methodology to quantify energy savings from replacing motors and adding variable speed drives in a cooling-tower pumping system at a soap/glycerin (oleochemical) plant, with the continuous-process units (distillation towers, soap vacuum systems) mentioned only as the heat source.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472535704 — `none`
- sectores sinalizados: upstream oil & gas drilling, upstream oil & gas drilling (extraction, not continuous processing)
- A8: 'drilling industry' · A9: 'continuous process'
- The paper reports an energy-management program by a drilling contractor (NDC) to optimize diesel-engine deployment on 55 upstream oil & gas drilling rigs, saving fuel, cost and CO2 — an extraction/drilling context, not continuous-flow industrial processing.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536340 — `mentioned_only`
- sectores sinalizados: continuous production processes (generic, via cited work)
- A8: 'chemical and pharmaceutical industries' · A9: 'not specified'
- The paper proposes a conceptual Energy Management System Plug-&-Monitor architecture using an Asset Administration Shell for flexible, reconfigurable Modular Plants in the chemical and pharmaceutical/specialty-chemical industries (batch/recipe-based, not continuous-flow); continuous production is only referenced via a cited aggregation method.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536353 — `none`
- sectores sinalizados: rubber glove manufacturing (continuous 24/7 dipping line), rubber glove manufacturing (latex dipping line), rubber glove manufacturing (process line)
- A8: 'glove manufacturing' · A9: 'discrete manufacturing'
- The paper empirically develops and validates deep-learning-based energy Measurement & Verification (IPMVP with anomaly detection) using real SCADA/SEMS data from a 24/7 rubber-glove manufacturing plant in Malaysia — a continuous-operation but discrete-product facility that is not one of the eight registered Corpus B sectors.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536444 — `mentioned_only`
- sectores sinalizados: cogeneration
- A8: None · A9: 'buildings'
- The paper designs and evaluates a microgrid (PV, BESS, CHP, backup gensets) to minimize grid energy imports for the Olympic Athletic Center of Athens sports complex — a large-scale building/facility energy context, not continuous-flow industrial production.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536466 — `mentioned_only`
- sectores sinalizados: desalination
- A8: 'water distribution networks' · A9: 'continuous process'
- A state-of-art review and conceptual framework for energy performance indicators and benchmarking (Energy Sustainability Score) in urban water distribution networks, demonstrated on a real district metered area in Kolkata — municipal water infrastructure, not continuous-flow industrial production.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536493 — `none`
- sectores sinalizados: cogeneration, cogeneration/trigeneration
- A8: 'airport terminal building' · A9: 'buildings'
- The paper is a case study on energy performance indicators and global-warming potential for an airport terminal building (Dalaman International Airport), a commercial/service building context, using regression and LCA methods — no continuous-flow industrial production is studied.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`

### rayyan-472536540 — `mentioned_only`
- sectores sinalizados: LNG
- A8: None · A9: 'not specified'
- Aspen Plus thermodynamic simulation and sensitivity analysis of a novel trigeneration (CCHP) cycle with two-phase expanders and compressors, targeting heating/cooling end-uses such as building climate control, food-industry sterilization, and cold storage; no continuous-production sector is empirically demonstrated.
- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`
