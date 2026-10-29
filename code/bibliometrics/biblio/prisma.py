"""PRISMA 2020-style draft with provenance, conserved counts and explicit unknowns."""
import json
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from .data import read_json

def counts(snapshot,config):
    regs=snapshot['registries'];dec=snapshot['screening_counts']
    duplicates=len(regs['excluded_duplicates']['entries']);not_retrieved=len(regs['non_retrieved_records']['records'])
    stage0=Counter(x['reason'] for x in regs['excluded_records']['entries'])
    sought=dec['Included']+dec['Maybe']-duplicates
    retrieved=sought-not_retrieved;reviewed=snapshot['stage1_n'];included=snapshot['corpus_a_n']
    c={'export_screened':snapshot['export_n'],'screening_excluded':dec['Excluded'],
       'candidate_reports':dec['Included']+dec['Maybe'],'late_duplicates':duplicates,'reports_sought':sought,
       'reports_not_retrieved':not_retrieved,'reports_assessed':retrieved,'deterministic_excluded':sum(stage0.values()),
       'language_excluded':stage0['language'],'retracted_excluded':stage0['retracted'],
       'methodological_assessed':reviewed,'methodological_excluded':reviewed-included,
       'fulltext_excluded':retrieved-included,'included_publications':included,
       'corpus_b_recorded':snapshot['corpus_b_n'],'b_outside_a':len(snapshot['membership_conflicts'])}
    assert c['export_screened']==c['screening_excluded']+c['candidate_reports']
    assert c['candidate_reports']==c['late_duplicates']+c['reports_sought']
    assert c['reports_sought']==c['reports_not_retrieved']+c['reports_assessed']
    assert c['reports_assessed']==c['deterministic_excluded']+c['methodological_assessed']
    assert c['reports_assessed']==c['fulltext_excluded']+c['included_publications']
    extras=read_json(config) if config.exists() else {}
    return c,extras

def draw(report,snapshot,config):
    c,extra=counts(snapshot,config)
    report.table('prisma_counts',[{'node':k,'n':v,'status':'documentado ou derivado por conservação','source':'input_snapshot.json; articles.csv; registos de exclusão; nota de fecho'} for k,v in c.items()],index=False)
    fig,ax=plt.subplots(figsize=(12,15));ax.set(xlim=(0,12),ylim=(0,15));ax.axis('off')
    def box(x,y,w,h,text,unknown=False):
        patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08,rounding_size=0.08',linewidth=1.1,
                            edgecolor='#C17D11' if unknown else '#48738F',facecolor='#FFF5DE' if unknown else '#F2F7FA')
        ax.add_patch(patch);ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10.5,linespacing=1.45)
    def arrow(a,b,dashed=False):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,color='#526879',lw=1.2,linestyle='--' if dashed else '-'))
    def value(key):return extra.get(key) if extra.get(key) is not None else 'por confirmar'
    box(.25,12.9,5.7,1.35,f'Identificação nas bases de dados\nScopus: {value("scopus_identified")} · WoS: {value("wos_identified")}\nDuplicados antes da triagem: {value("early_duplicates")}',True)
    box(7.2,12.9,4.25,1.35,'Outros métodos / snowballing\nContagens e fecho por documentar\nNão assumir n = 0',True)
    arrow((3.1,12.85),(3.1,12.25),True)
    box(.65,11.25,4.9,.9,f'Registos no export de triagem\nn = {c["export_screened"]}')
    box(7.2,11.25,4.25,.9,f'Registos excluídos na triagem\nn = {c["screening_excluded"]}')
    arrow((5.65,11.7),(7.1,11.7));arrow((3.1,11.15),(3.1,10.5))
    box(.65,9.55,4.9,.85,f'Candidatos a texto integral\nn = {c["candidate_reports"]}')
    box(7.2,9.55,4.25,.85,f'Duplicados identificados nesta fase\nn = {c["late_duplicates"]}')
    arrow((5.65,9.98),(7.1,9.98));arrow((3.1,9.45),(3.1,8.8))
    box(.65,7.85,4.9,.85,f'Publicações procuradas\nn = {c["reports_sought"]}')
    box(7.2,7.85,4.25,.85,f'Textos integrais não recuperados\nn = {c["reports_not_retrieved"]}')
    arrow((5.65,8.28),(7.1,8.28));arrow((3.1,7.75),(3.1,7.05))
    box(.65,6.05,4.9,.9,f'Textos integrais avaliados\nn = {c["reports_assessed"]}')
    box(7.2,5.75,4.25,1.6,f'Publicações excluídas: n = {c["fulltext_excluded"]}\nIdioma: {c["language_excluded"]} · Retratação: {c["retracted_excluded"]}\nElegibilidade metodológica: {c["methodological_excluded"]}\nDesagregar motivos: por fechar',True)
    arrow((5.65,6.5),(7.1,6.5));arrow((3.1,5.95),(3.1,5.05))
    box(.65,4.05,4.9,.9,f'Publicações incluídas — Corpus A\nn = {c["included_publications"]}')
    if c['b_outside_a']:
        box(6.5,3.75,4.95,1.55,f'Corpus B registado: {c["corpus_b_recorded"]}\nInterseção com A: {c["corpus_b_recorded"]-c["b_outside_a"]}\n{c["b_outside_a"]} registos B=true / A=false\nComposição final por reconciliar',True)
        arrow((5.65,4.5),(6.4,4.5),True)
        box(.65,1.9,10.8,1.05,f'Vista exploratória inclusiva A∪B: {len(snapshot["records"])} publicações\nConserva todos os artigos registados em B; não altera a elegibilidade de origem.',True)
    else:
        box(6.5,4.05,4.95,.9,f'Subconjunto para síntese narrativa — B\nn = {c["corpus_b_recorded"]} (incluído em A)');arrow((5.65,4.5),(6.4,4.5))
    ax.text(.65,.95,'Unidade de contagem: publicações/registos. Número de estudos independentes não estabelecido.\nOs 331 incluídos não são a soma de A com B. Não recuperados não são excluídos por elegibilidade.',fontsize=9,color='#374F62',linespacing=1.5)
    report.save(fig,'prisma_flow','PRISMA — rascunho com as contagens existentes',
        'Adaptado de PRISMA 2020 (CC BY 4.0): prisma-statement.org/prisma-2020-flow-diagram. Caixas âmbar: pontos por fechar; setas tracejadas: ligação provisória.',True)
    (report.out/'prisma_ledger.json').write_text(json.dumps({'counts':c,'pending':extra,'membership_conflicts':snapshot['membership_conflicts'],
        'status':'draft','source_documents':['data/articles.csv','data/MISSINGNESS.md','data/excluded_records.json','data/excluded_duplicates.json','CORPUS_CLOSURE_2026-09-12.md'],
        'notes':['331 publicações, não 331 estudos independentes','599-3=596; 596-137=459; 459-11=448; 448-331=117','331/42 não formam conjuntos aninhados nos ficheiros: dois conflitos','Fecho do censo de falsos negativos não substitui o log de snowballing']},ensure_ascii=False,indent=2),encoding='utf-8')
    return c
