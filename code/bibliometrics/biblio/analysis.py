"""Descriptive analyses with publication-level denominators and explicit missingness."""
from __future__ import annotations
from collections import Counter,defaultdict
from itertools import product,combinations
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .data import FIELDS,MULTI,MISSING,items
from .plots import COLORS,wrap

TITLES={'paper_type':'Tipo de estudo','multi_site':'Estudos com várias instalações',
 'country_region':'Localização dos casos — texto original','sector_of_activity':'Setores — texto original',
 'type_of_organisation':'Tipos de organização','ems_standard':'Normas de gestão de energia',
 'mv_protocol':'Protocolos de medição e verificação','regulatory_driver':'Enquadramento regulamentar',
 'enpi_enb_model_types':'Famílias de modelos EnPI/EnB','complementary_methodologies':'Metodologias complementares',
 'document_type':'Tipos de documento','source':'Fontes de publicação','countries_case':'Países dos casos estudados',
 'sectors_derived':'Setores — agrupamento exploratório','source_string':'Origem nas strings de pesquisa'}

def observed(v): return v is not None and (not isinstance(v,list) or len(v)>0)

def frequencies(records,field,missing=True):
    c=Counter()
    for r in records:
        value=r.get(field)
        if not observed(value):
            if missing:c[MISSING]+=1
        else:c.update(str(x) for x in items(value))
    return c

def cross(records,rowfield,colfield,include_missing=False):
    cells=defaultdict(Counter);eligible=0
    for r in records:
        a,b=r.get(rowfield),r.get(colfield)
        if not observed(a) or not observed(b):
            if not include_missing:continue
        eligible+=1
        aa=items(a) or [MISSING];bb=items(b) or [MISSING]
        for x,y in product(aa,bb):cells[str(x)][str(y)]+=1
    return pd.DataFrame.from_dict(cells,orient='index').fillna(0),eligible

def descriptive(report,records):
    n=len(records);years=sorted({r['year'] for r in records});annual=pd.Series(Counter(r['year'] for r in records)).reindex(range(min(years),max(years)+1),fill_value=0)
    report.table('annual',pd.DataFrame({'n':annual,'cumulative':annual.cumsum(),'growth_pct':annual.pct_change().replace([np.inf,-np.inf],np.nan)*100}))
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    axes[0].bar(annual.index,annual.values,color=COLORS[0]);axes[1].plot(annual.index,annual.cumsum(),color=COLORS[2],marker='o',ms=3)
    for ax in axes:ax.set_xlabel('Ano de publicação');ax.set_ylabel('Publicações');ax.tick_params(axis='x',rotation=45)
    axes[0].set_title('Publicações anuais');axes[1].set_title('Publicações acumuladas')
    report.save(fig,'annual','Evolução da literatura','Cobertura temporal definida pela pesquisa; não interpretar o último ano como ano completo.')
    for field in ['source','document_type','paper_type','multi_site','type_of_organisation','country_region','countries_case','sector_of_activity','sectors_derived','ems_standard','mv_protocol','regulatory_driver','enpi_enb_model_types','complementary_methodologies']:
        k=sum(observed(r.get(field)) for r in records)
        caption=f'Campo disponível em {k}/{n} publicações. Contagem integral por publicação; múltiplas etiquetas podem somar mais de 100%.'
        if field in ['sectors_derived','countries_case']:caption+=' Normalização derivada a rever; não altera o texto original.'
        report.bars(field,frequencies(records,field),TITLES[field],caption,provisional=field not in ['source','document_type'])
    if any(r.get('source_string') for r in records):report.bars('source_string',frequencies(records,'source_string'),TITLES['source_string'])
    else:report.skip('source_string_and_crosses','A12 está vazio em todos os registos. Null não identifica snowballing: consultar a flag própria e o log de pesquisa.')
    for field,label in [('author_count','Dimensão das equipas'),('model_count','Número de famílias de modelos por artigo')]:
        report.bars(field,frequencies(records,field),label,'Distribuição por publicação; categorias não resolvidas mantidas.',provisional=field=='model_count')
    c=frequencies(records,'source',False);s=pd.Series(c).sort_values(ascending=False)
    fig,ax=plt.subplots(figsize=(10,5));ranks=np.arange(1,len(s)+1);ax.plot(ranks,100*s.cumsum()/s.sum(),color=COLORS[0]);ax.set(xlabel='Fontes, ordenadas por frequência',ylabel='% acumulada de publicações',ylim=(0,102))
    report.table('source_concentration',pd.DataFrame({'source':s.index,'n':s.values,'cumulative_pct':100*s.cumsum().values/s.sum()}),index=False)
    report.save(fig,'source_concentration','Concentração das fontes','Distribuição empírica; não é um teste da lei de Bradford.')
    source_share=s/s.sum();report.table('concentration_summary',[{'sources_n':len(s),'top5_share':source_share.head(5).sum(),'top10_share':source_share.head(10).sum(),'hhi':sum(source_share**2),'shannon_nats':-sum(source_share*np.log(source_share))}],index=False)
    # Source zones are descriptive, with boundaries on whole sources.
    report.table('bradford_descriptive',pd.DataFrame({'source':s.index,'n':s.values,'zone_end_cumulative':np.minimum(3,np.ceil(3*s.cumsum().values/s.sum())).astype(int)}),index=False)
    author_counts=Counter(a for r in records for a in set(r['authors']))
    report.bars('authors_productivity',author_counts,'Autores mais presentes','Nomes do export, sem desambiguação completa; não representa a produção total dos autores.')
    lotka=Counter(author_counts.values());report.bars('author_productivity_distribution',lotka,'Distribuição da produtividade dos autores','Número de autores por número de artigos no corpus; descrição, sem ajuste à lei de Lotka.',denominator=1)
    byauthor=defaultdict(list)
    for r in records:
        for a in set(r['authors']):byauthor[a].append(r['year'])
    report.table('authors_timeline',[{'author':a,'papers_n':len(y),'first_year':min(y),'last_year':max(y)} for a,y in byauthor.items()],index=False)
    topauthors=[a for a,_ in author_counts.most_common(18)]
    fig,ax=plt.subplots(figsize=(11,8))
    for i,a in enumerate(topauthors):
        yc=Counter(byauthor[a]);ax.plot([min(yc),max(yc)],[i,i],color='#aaaaaa',lw=1)
        ax.scatter(list(yc),[i]*len(yc),s=[30*v for v in yc.values()],color=COLORS[0])
    ax.set_yticks(range(len(topauthors)),topauthors);ax.invert_yaxis();ax.set_xlabel('Ano; área do ponto proporcional à contagem')
    report.save(fig,'authors_timeline','Continuidade dos autores no corpus','18 nomes com mais publicações; não representa a carreira completa; identidade nominal por rever.')
    annual_types,_=cross(records,'year','paper_type',True)
    annual_types=annual_types.sort_index(key=lambda x:x.astype(int));report.table('annual_study_types',annual_types)
    fig,ax=plt.subplots(figsize=(12,7));annual_types.plot.bar(stacked=True,ax=ax,color=COLORS+['#999999']);ax.set(xlabel='Ano',ylabel='Publicações');ax.legend(fontsize=8,loc='upper left')
    report.save(fig,'annual_study_types','Evolução por tipo de estudo','Categorias não resolvidas incluídas; último ano de pesquisa pode ser parcial.',True)

def cross_analyses(report,records):
    pairs=[('sectors_derived','enpi_enb_model_types'),('type_of_organisation','enpi_enb_model_types'),
      ('enpi_enb_model_types','enpi_enb_model_types'),('ems_standard','ems_standard'),
      ('period','enpi_enb_model_types'),('period','sectors_derived'),('period','paper_type'),
      ('period','ems_standard'),('period','mv_protocol'),('ems_standard','enpi_enb_model_types'),
      ('mv_protocol','enpi_enb_model_types'),('sectors_derived','ems_standard'),('sectors_derived','mv_protocol'),
      ('paper_type','enpi_enb_model_types'),('multi_site','enpi_enb_model_types'),
      ('countries_case','sectors_derived'),('countries_case','enpi_enb_model_types'),
      ('source','sectors_derived'),('source','enpi_enb_model_types'),
      ('enpi_enb_model_types','complementary_methodologies'),('ems_standard','mv_protocol'),
      ('regulatory_driver','ems_standard'),('regulatory_driver','enpi_enb_model_types'),
      ('source_string','type_of_organisation'),('source_string','enpi_enb_model_types'),('source_string','ems_standard')]
    for x,y in pairs:
        m,k=cross(records,x,y);name=f'cross_{x}__{y}'
        report.heatmap(name,m,f'{TITLES.get(x,x)} × {TITLES.get(y,y)}',
            f'Pares de campos disponíveis em {k}/{len(records)} artigos. Etiquetas múltiplas; cada artigo contado uma vez por célula.',provisional=True)
    # Fixed denominators for disjoint groups; B is never appended twice.
    for field in ['paper_type','type_of_organisation','ems_standard','mv_protocol','enpi_enb_model_types','sectors_derived']:
        m,k=cross(records,field,'group',True);groups=Counter(r['group'] for r in records)
        pct=m.copy()
        for g in pct.columns:pct[g]=pct[g]*100/groups[g]
        report.table('comparison_'+field,pct)
        fig,ax=plt.subplots(figsize=(11,max(5,.42*len(pct)+2)));pct.sort_values(by=pct.columns[0]).plot.barh(ax=ax,color=COLORS[:len(pct.columns)],width=.8)
        ax.set_xlabel('% de publicações no respetivo grupo');ax.set_ylabel('');ax.set_yticklabels([wrap(x,38) for x in pct.index[pct.iloc[:,0].argsort()]])
        report.save(fig,'comparison_'+field,f'B e restante conjunto: {TITLES.get(field,field)}',f'Denominadores: {dict(groups)}. Grupos disjuntos; não inferir representatividade setorial.',True)

def intersections(report,records,field):
    combos=Counter(tuple(sorted(set(items(r[field])))) for r in records if r[field] is not None)
    name='upset_'+field
    report.table(name,[{'combination':' | '.join(k) or '(lista vazia)','n':v} for k,v in combos.most_common()],index=False)
    shown=combos.most_common(18)
    if not shown:report.skip(name,'Campo sem valores.');return
    labels=sorted(set(x for k,_ in shown for x in k))
    fig=plt.figure(figsize=(max(10,.5*len(shown)+4),max(6,.33*len(labels)+4)));gs=fig.add_gridspec(2,1,height_ratios=[2,max(1,len(labels)/5)],hspace=.08)
    top=fig.add_subplot(gs[0]);bottom=fig.add_subplot(gs[1],sharex=top)
    top.bar(range(len(shown)),[n for _,n in shown],color=COLORS[0]);top.set_ylabel('Publicações');top.tick_params(axis='x',labelbottom=False)
    for x,(combo,cnt) in enumerate(shown):
        top.text(x,cnt,str(cnt),ha='center',va='bottom',fontsize=8)
        ys=[labels.index(label) for label in combo]
        bottom.scatter([x]*len(labels),range(len(labels)),s=18,color='#dddddd')
        if ys:bottom.plot([x,x],[min(ys),max(ys)],color='#333333',lw=1.4);bottom.scatter([x]*len(ys),ys,s=32,color=COLORS[0])
    bottom.set_yticks(range(len(labels)),[wrap(x,36) for x in labels]);bottom.set_xticks([]);bottom.invert_yaxis()
    report.save(fig,name,'Combinações: '+TITLES[field],f'Interseções exatas. {sum(combos.values())}/{len(records)} artigos com campo disponível; {len(shown)} combinações mostradas, tabela completa em CSV.',True)

def quality(report,records,snapshot):
    matrix=pd.DataFrame([{f:r['status'][f] for f in FIELDS} for r in records]).apply(pd.Series.value_counts).fillna(0).T
    report.table('field_status',matrix);fig,ax=plt.subplots(figsize=(12,7));matrix.plot.barh(stacked=True,ax=ax,color=COLORS)
    ax.set_xlabel('Publicações');ax.set_ylabel('');ax.legend(loc='lower left',bbox_to_anchor=(0,1.02),ncol=2,fontsize=8)
    report.save(fig,'field_status','Estado de verificação dos campos','Concordância entre IA não é validação humana. Divergências e extrações únicas não recebem precedência automática.',True)
    rows=[]
    for field in FIELDS:
        ca=frequencies([dict(r,**{field:r['views']['claude'].get(field)}) for r in records],field)
        cb=frequencies([dict(r,**{field:r['views']['chatgpt'].get(field)}) for r in records],field)
        for category in sorted(set(ca)|set(cb)):
            rows.append({'field':field,'category':category,'claude_n':ca[category],'chatgpt_n':cb[category],'difference_n':ca[category]-cb[category]})
    report.table('model_surface_sensitivity',rows,index=False)
    t=pd.DataFrame(rows);t=t[t.field=='enpi_enb_model_types'].set_index('category')[['claude_n','chatgpt_n']]
    report.heatmap('model_surface_sensitivity_plot',t,'Sensibilidade à superfície de extração','Duas pré-extrações independentes mantidas separadas. Este gráfico não mede fiabilidade.',True)
    report.table('membership_conflicts',[{'paper_id':k,'issue':'B=true e A=false nos registos de origem'} for k in snapshot['membership_conflicts']],index=False)
    report.table('normalization_country_queue',[{'paper_id':r['paper_id'],'raw':r['country_region']} for r in records if r.get('country_unmapped')],index=False)
    report.table('normalization_sector_mapping',[{'paper_id':r['paper_id'],'raw':r['sector_of_activity'],'derived':' | '.join(r['sectors_derived'])} for r in records],index=False)

def alluvial(report,records):
    from matplotlib.patches import PathPatch,Rectangle
    from matplotlib.path import Path
    fields=['sectors_derived','enpi_enb_model_types','ems_standard'];top={f:set(k for k,_ in frequencies(records,f,False).most_common(6)) for f in fields}
    edges=[Counter(),Counter()];covered=0
    for r in records:
        lists=[items(r.get(f)) for f in fields]
        if not all(lists):continue
        covered+=1;lists=[[x if x in top[f] else 'Outros' for x in seq] for f,seq in zip(fields,lists)]
        for a,b,c in product(*lists):
            w=1/np.prod([len(x) for x in lists]);edges[0][(a,b)]+=w;edges[1][(b,c)]+=w
    if not covered:report.skip('alluvial','Sem artigos com os três campos.');return
    masses=[Counter(),Counter(),Counter()]
    for (a,b),w in edges[0].items():masses[0][a]+=w;masses[1][b]+=w
    for (b,c),w in edges[1].items():masses[2][c]+=w
    positions=[];scale=.78/covered
    for counts in masses:
        y=.05;pos={};gap=.16/max(len(counts),1)
        for label,mass in counts.most_common():pos[label]=(y,mass*scale);y+=mass*scale+gap
        positions.append(pos)
    fig,ax=plt.subplots(figsize=(14,9));xs=[.06,.49,.91];width=.014
    for j,ed in enumerate(edges):
        usedleft=Counter();usedright=Counter()
        for (a,b),w in sorted(ed.items()):
            y0=positions[j][a][0]+usedleft[a]*scale;y1=positions[j+1][b][0]+usedright[b]*scale;h=w*scale
            x0=xs[j]+width;x1=xs[j+1];mid=(x0+x1)/2
            verts=[(x0,y0),(mid,y0),(mid,y1),(x1,y1),(x1,y1+h),(mid,y1+h),(mid,y0+h),(x0,y0+h),(x0,y0)]
            codes=[Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.LINETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts,codes),facecolor=COLORS[j],alpha=.22,edgecolor='none'));usedleft[a]+=w;usedright[b]+=w
    for j,pos in enumerate(positions):
        for label,(y,h) in pos.items():
            ax.add_patch(Rectangle((xs[j],y),width,h,color=COLORS[j]));ax.text(xs[j]-.006 if j==0 else xs[j]+.023,y+h/2,wrap(label,23),ha='right' if j==0 else 'left',va='center',fontsize=8)
        ax.text(xs[j],1.01,TITLES[fields[j]],ha='center',fontweight='bold',fontsize=10)
    ax.set(xlim=(-.18,1.18),ylim=(0,1.06));ax.axis('off')
    report.table('alluvial',[{'transition':j,'from':a,'to':b,'fractional_publications':w} for j,ed in enumerate(edges) for (a,b),w in ed.items()],index=False)
    report.save(fig,'alluvial','Setor → modelo → enquadramento normativo',f'{covered} artigos com os três campos. Cada artigo distribui peso total 1 pelas combinações; larguras fracionadas, não contagens integrais.',True)
