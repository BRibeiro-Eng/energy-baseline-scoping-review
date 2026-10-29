"""Bibliographic networks; methods and coverage travel with every export."""
from __future__ import annotations
from collections import Counter,defaultdict
from itertools import combinations
from difflib import SequenceMatcher
import re
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from .data import read_json,items,doi
from .enrich import abstract
from .plots import COLORS,wrap
from .analysis import cross,frequencies

def attach_metadata(records,cache,report):
    mismatch=[];coverage=[]
    for r in records:
        r['oa']=None;r['cr']=None
        for provider,key in [('openalex','oa'),('crossref','cr')]:
            p=cache/provider/(r['paper_id']+'.json')
            if not p.exists():continue
            envelope=read_json(p);work=envelope['work'];title=work.get('title','');title=title[0] if isinstance(title,list) and title else title
            clean=lambda s:re.sub(r'\W+','',str(s).casefold())
            ratio=SequenceMatcher(None,clean(r['title']),clean(title)).ratio()
            if doi(work.get('doi',work.get('DOI')))!=r['doi'] or ratio<.6:
                mismatch.append({'paper_id':r['paper_id'],'provider':provider,'title_csv':r['title'],'title_provider':title,'similarity':ratio});continue
            r[key]=work;r[key+'_date']=envelope['retrieved_at']
        w=r['oa'] or {};cr=r['cr'] or {}
        r['abstract_enriched']=abstract(w) or re.sub('<[^>]+>',' ',cr.get('abstract',''))
        r['citations_oa']=w.get('cited_by_count');r['citations_cr']=cr.get('is-referenced-by-count')
        r['affiliation_countries']=sorted(set(c for a in w.get('authorships',[]) for c in a.get('countries',[])))
        inst={i['id']:i for a in w.get('authorships',[]) for i in a.get('institutions',[]) if i.get('id')}
        r['institutions_ids']=list(inst);r['institutions_names']=[i['display_name'] for i in inst.values()]
        r['institution_types']=sorted(set(i.get('type','unknown') for i in inst.values()))
        r['funders']=sorted(set(x.get('display_name') or x.get('name') or x.get('id','') for x in (w.get('funders') or cr.get('funder') or [])))
        r['oa_status']=(w.get('open_access') or {}).get('oa_status')
        r['references_oa']=list(dict.fromkeys(w.get('referenced_works') or []))
        r['references_doi']=sorted(set(doi(x.get('DOI')) for x in cr.get('reference',[]) if x.get('DOI')))
        r['fwci']=w.get('fwci')
        coverage.append({'paper_id':r['paper_id'],'openalex':bool(w),'crossref':bool(cr),'abstract':bool(r['abstract_enriched']),
                         'affiliations':bool(inst),'references_openalex':len(r['references_oa']),'reference_dois_crossref':len(r['references_doi']),
                         'openalex_retrieved_at':r.get('oa_date'),'crossref_retrieved_at':r.get('cr_date')})
    report.table('metadata_title_mismatch',mismatch,index=False);report.table('metadata_enrichment_coverage',coverage,index=False)
    return records

def projection(lists,min_occurrence=2,max_nodes=70):
    frequencies=Counter(x for seq in lists for x in set(seq));keep={x for x,_ in frequencies.most_common(max_nodes) if frequencies[x]>=min_occurrence}
    g=nx.Graph()
    for x in sorted(keep):g.add_node(x,occurrences=frequencies[x])
    for seq in lists:
        for a,b in combinations(sorted(set(seq)&keep),2):
            if g.has_edge(a,b):g[a][b]['weight']+=1
            else:g.add_edge(a,b,weight=1)
    return g,frequencies

def draw_network(report,g,name,title,caption,labels=None,provisional=False):
    report.table(name,[{'from':a,'to':b,'weight':d.get('weight',1)} for a,b,d in g.edges(data=True)],index=False)
    if not g.nodes or not g.edges:report.skip(name,'Rede sem ligações suficientes com os limiares definidos.');return {}
    nx.write_gexf(g,report.out/'networks'/f'{name}.gexf')
    und=g.to_undirected();communities=list(nx.community.greedy_modularity_communities(und,weight='weight'))
    cmap={node:i for i,c in enumerate(communities) for node in c}
    pos=nx.spring_layout(g,seed=44,weight='weight',iterations=120,k=1.3/max(1,np.sqrt(len(g))))
    fig,(ax,keyax)=plt.subplots(1,2,figsize=(14,9),gridspec_kw={'width_ratios':[1.2,1]})
    maxw=max(d.get('weight',1) for _,_,d in g.edges(data=True))
    nx.draw_networkx_edges(g,pos,ax=ax,alpha=.2,width=[.4+2*d.get('weight',1)/maxw for _,_,d in g.edges(data=True)],arrows=g.is_directed(),arrowsize=10)
    nx.draw_networkx_nodes(g,pos,ax=ax,node_color=[COLORS[cmap[n]%len(COLORS)] for n in g],node_size=[55+65*np.sqrt(g.nodes[n].get('occurrences',1)) for n in g],edgecolors='white',linewidths=.6)
    ranked=sorted(g,key=lambda n:g.degree(n,weight='weight'),reverse=True)[:12]
    keyax.axis('off');keyax.text(0,1,'Nós identificados (maior força)',fontweight='bold',fontsize=10,transform=keyax.transAxes)
    legend_y=.95
    for number,node in enumerate(ranked,1):
        x,y=pos[node];ax.text(x,y,str(number),fontsize=9,ha='center',va='center',fontweight='bold',bbox={'facecolor':'white','alpha':.9,'edgecolor':'none','pad':1})
        label=wrap(f'{number}. '+(labels or {}).get(node,node),49)
        keyax.text(0,legend_y,label,fontsize=8.5,va='top',transform=keyax.transAxes)
        legend_y-=.027*(label.count('\n')+2)
    ax.axis('off');ax.margins(.15)
    report.save(fig,name,title,caption+f' Rede: {len(g)} nós, {g.number_of_edges()} ligações; 12 nós identificados na legenda; restantes no CSV/GEXF. Layout seed=44; comunidades exploratórias.',provisional)
    bet=nx.betweenness_centrality(g,weight=None)
    report.table(name+'_nodes',[{'node':n,'label':(labels or {}).get(n,n),'occurrences':g.nodes[n].get('occurrences'),
         'degree':g.degree(n),'strength':g.degree(n,weight='weight'),'betweenness_unweighted':bet[n],'community':cmap[n]} for n in g],index=False)
    report.table(name+'_summary',[{'nodes':len(g),'edges':g.number_of_edges(),'density':nx.density(g),'components':nx.number_connected_components(und),'communities':len(communities)}],index=False)
    return cmap

def keyword_analyses(report,records):
    lists=[r['keywords_clean'] for r in records];coverage=sum(bool(x) for x in lists)
    g,freq=projection(lists,3,65);report.bars('keywords',freq,'Palavras-chave mais frequentes',f'{coverage}/{len(records)} artigos com palavras-chave; origem autor/indexação não separada no export.')
    cmap=draw_network(report,g,'keyword_network','Coocorrência de palavras-chave','Presença por artigo; mínimo 3 ocorrências, máximo 65 termos; pesos = coocorrências.',provisional=True)
    for r in records:r['keyword_clusters']=sorted(set(f'C{cmap[k]+1}' for k in r['keywords_clean'] if k in cmap))
    report.table('keyword_alias_result',[{'paper_id':r['paper_id'],'raw':' | '.join(r['keywords']),'normalized':' | '.join(r['keywords_clean'])} for r in records],index=False)
    for field in ['period','sectors_derived','enpi_enb_model_types','ems_standard']:
        m,k=cross(records,field,'keyword_clusters');report.heatmap('themes_'+field,m,'Temas exploratórios × '+field,f'{k} artigos representados. Um artigo pode pertencer a vários clusters.',True)
    # Defined exploratory indicators, not a causal or evaluative classification of themes.
    themes=[]
    for cluster in sorted(set(cmap.values())):
        nodes={n for n,c in cmap.items() if c==cluster};inside=sum(d['weight'] for a,b,d in g.edges(data=True) if a in nodes and b in nodes)
        outside=sum(d['weight'] for a,b,d in g.edges(data=True) if (a in nodes)!=(b in nodes))
        themes.append({'cluster':f'C{cluster+1}','terms':len(nodes),'internal_mean_weight':inside/max(1,len(nodes)*(len(nodes)-1)/2),
                       'external_weight_per_term':outside/len(nodes),'top_terms':'; '.join(sorted(nodes,key=lambda x:freq[x],reverse=True)[:5])})
    report.table('thematic_map',themes,index=False)
    if themes:
        fig,ax=plt.subplots(figsize=(11,7))
        for t in themes:
            ax.scatter(t['external_weight_per_term'],t['internal_mean_weight'],s=60*t['terms'],alpha=.6)
            ax.annotate(t['cluster']+': '+wrap(t['top_terms'],35),(t['external_weight_per_term'],t['internal_mean_weight']),fontsize=8)
        ax.set(xlabel='Peso externo / número de termos',ylabel='Peso interno / pares possíveis')
        report.save(fig,'thematic_map','Posição dos clusters temáticos','Indicadores exploratórios definidos nos eixos; não atribuir automaticamente rótulos de maturidade, emergência ou importância.',True)
    periods=sorted({r['period'] for r in records});top=[x for x,_ in freq.most_common(25)]
    trend=[]
    for period in periods:
        subset=[r for r in records if r['period']==period];den=sum(bool(r['keywords_clean']) for r in subset)
        c=Counter(k for r in subset for k in set(r['keywords_clean']))
        for k in top:trend.append({'period':period,'keyword':k,'n':c[k],'papers_with_keywords':den,'pct':100*c[k]/den if den else np.nan})
    report.table('keyword_temporal_prevalence',trend,index=False)
    if trend:report.heatmap('keyword_temporal_map',pd.DataFrame(trend).pivot(index='keyword',columns='period',values='n'),'Palavras-chave por período','Janelas fixas de 5 anos; consultar CSV de prevalência com denominadores por período.',True)
    # Vocabulary of titles/abstracts stays independent from manually coded methodological evidence.
    from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
    from sklearn.decomposition import NMF
    for field,label in [('title','Títulos'),('abstract_enriched','Resumos enriquecidos')]:
        docs=[r for r in records if r.get(field)]
        if len(docs)<12:report.skip('text_'+field,'Menos de 12 textos disponíveis.');continue
        vec=CountVectorizer(stop_words='english',ngram_range=(1,2),min_df=3,max_df=.85,max_features=400,binary=True)
        try:mat=vec.fit_transform([r[field] for r in docs])
        except ValueError:report.skip('text_'+field,'Vocabulário insuficiente.');continue
        report.bars('text_'+field,dict(zip(vec.get_feature_names_out(),np.asarray(mat.sum(axis=0)).ravel())),label+': termos frequentes',f'{len(docs)} documentos; stopwords em inglês; 1–2 palavras; min_df=3; presença por documento.')
        if field=='abstract_enriched':
            tf=TfidfVectorizer(stop_words='english',min_df=3,max_df=.8,max_features=1200,ngram_range=(1,2));x=tf.fit_transform([r[field] for r in docs]);k=min(6,x.shape[0]-1,x.shape[1]-1)
            nmf=NMF(n_components=k,random_state=44,init='nndsvda',max_iter=500);scores=nmf.fit_transform(x);terms=tf.get_feature_names_out()
            report.table('abstract_topics',[{'topic':i+1,'top_terms':'; '.join(terms[comp.argsort()[-10:][::-1]])} for i,comp in enumerate(nmf.components_)],index=False)
            report.table('abstract_topic_assignments',[{'paper_id':r['paper_id'],'topic':int(scores[i].argmax()+1),'dominant_weight':float(scores[i].max())} for i,r in enumerate(docs)],index=False)
            report.bars('abstract_topics_distribution',Counter(int(row.argmax()+1) for row in scores),'Resumos: tópicos exploratórios NMF',f'{len(docs)} resumos; TF-IDF; {k} tópicos; seed=44. Atribuição dominante, sujeita a interpretação.',provisional=True)

def collaboration(report,records):
    g,_=projection([r['authors'] for r in records],2,70)
    draw_network(report,g,'coauthorship','Rede de coautoria','Nomes do export; mínimo 2 artigos por nome. Homónimos e variantes não totalmente resolvidos.')
    for field,label in [('affiliation_countries','Países de afiliação'),('institutions_names','Instituições'),('institution_types','Tipos de instituições'),('funders','Entidades financiadoras'),('oa_status','Acesso aberto')]:
        c=frequencies(records,field,False);k=sum(bool(r.get(field)) for r in records)
        report.bars('enriched_'+field,c,label,f'Metadados enriquecidos disponíveis em {k}/{len(records)} artigos; ausências não significam inexistência.')
    names={i['id']:i['display_name'] for r in records for a in (r['oa'] or {}).get('authorships',[]) for i in a.get('institutions',[]) if i.get('id')}
    for field,label in [('affiliation_countries','Colaboração internacional'),('institutions_ids','Colaboração interinstitucional')]:
        g,_=projection([r[field] for r in records],2,60);draw_network(report,g,'network_'+field,label,'Coocorrência por publicação; afiliações do OpenAlex. Geografia distinta da localização dos casos.',names)
    rows=[]
    for r in records:
        types=r['institution_types'];rows.append({'paper_id':r['paper_id'],'countries_n':len(r['affiliation_countries']),
            'institutions_n':len(r['institutions_ids']),'international':len(r['affiliation_countries'])>1 if r['affiliation_countries'] else None,
            'education_company':('education' in types and 'company' in types) if types else None})
    report.table('collaboration_indicators',rows,index=False)
    report.bars('international_collaboration',Counter(str(x['international']) for x in rows),'Colaboração internacional','True: pelo menos dois países de afiliação; None: afiliações não disponíveis.')
    report.bars('education_company',Counter(str(x['education_company']) for x in rows),'Colaboração educação–empresa','Tipos institucionais declarados pelo OpenAlex; ausência de empresa nos metadados não exclui participação industrial.')

def citations(report,records,cache=None):
    from datetime import datetime,timezone
    now=datetime.now(timezone.utc).year
    table=[]
    for r in records:
        table.append({'paper_id':r['paper_id'],'title':r['title'],'year':r['year'],
            'openalex':r['citations_oa'],'crossref':r['citations_cr'],'historical_export':r['export_citations'],
            'historical_export_date':r['export_date'],'openalex_date':r.get('oa_date'),
            'citations_per_elapsed_year':r['citations_oa']/max(1,int(r['oa_date'][:4])-r['year']+1) if r['citations_oa'] is not None else None,
            'fwci_openalex':r['fwci']})
    t=pd.DataFrame(table);report.table('citations_by_paper',t,index=False)
    labels={r['paper_id']:f"{r['year']} · {r['title'][:85]}" for r in records}
    for col,title in [('openalex','Citações recebidas — OpenAlex'),('crossref','Citações recebidas — Crossref'),('citations_per_elapsed_year','Citações por ano decorrido')]:
        s=t.dropna(subset=[col]).set_index('paper_id')[col];report.bars('citations_'+col,{labels[k]:v for k,v in s.items()},title,'Bases e datas mantidas separadas; contagens não equivalem a qualidade. Divisão por idade não é normalização por campo.',denominator=1)
    known=t.openalex.dropna().sort_values(ascending=False);h=sum(v>=i for i,v in enumerate(known,1));cum=known.cumsum().to_numpy();g=max([i for i,v in enumerate(cum,1) if v>=i*i],default=0)
    report.table('citation_summary',[{'coverage':len(known),'n_population':len(records),'sum_openalex':known.sum(),'median_openalex':known.median(),'h_within_observed_corpus':h,'g_within_observed_corpus':g}],index=False)
    if len(known):
        fig,ax=plt.subplots(figsize=(9,5));ax.hist(known,bins=min(25,len(known)),color=COLORS[0]);ax.set(xlabel='Citações por publicação — OpenAlex',ylabel='Publicações');report.save(fig,'citation_distribution','Distribuição das citações',f'{len(known)}/{len(records)} com contagens. Zero observado é distinto de metadado ausente.')
    hist=Counter()
    for r in records:
        for row in (r['oa'] or {}).get('counts_by_year',[]):hist[row['year']]+=row.get('cited_by_count',0)
    if hist:
        report.table('citations_year_received',[{'year':y,'citations':hist[y]} for y in sorted(hist)],index=False)
        fig,ax=plt.subplots(figsize=(10,5));ax.bar(sorted(hist),[hist[y] for y in sorted(hist)],color=COLORS[0]);ax.set(xlabel='Ano da citação',ylabel='Citações recebidas')
        report.save(fig,'citations_year_received','Citações recebidas por ano','Soma dos históricos disponíveis no OpenAlex; estes históricos podem cobrir apenas anos recentes.')
    # Direct edges among included publications; absence of references is a coverage limitation.
    byid={(r['oa'] or {}).get('id'):r['paper_id'] for r in records if r['oa']};g=nx.DiGraph();g.add_nodes_from(byid.values())
    for r in records:
        for ref in r['references_oa']:
            if ref in byid:g.add_edge(r['paper_id'],byid[ref],weight=1)
    g.remove_nodes_from(list(nx.isolates(g)));draw_network(report,g,'direct_citations','Citações diretas dentro do conjunto','Seta: publicação citante → citada. Apenas referências indexadas pelo OpenAlex.',labels)
    report.bars('local_citations',dict(g.in_degree()),'Citações locais recebidas','Citações provenientes de outras publicações deste conjunto; dependem da cobertura das bibliografias.')
    # Coupling uses references shared by the citing corpus publications, not co-citation.
    refs={r['paper_id']:set(r['references_oa']) for r in records if r['references_oa']};coupling=nx.Graph()
    for a,b in combinations(refs,2):
        shared=len(refs[a]&refs[b])
        if shared>=2:coupling.add_edge(a,b,weight=shared/np.sqrt(len(refs[a])*len(refs[b])),shared_references=shared)
    # Save the complete thresholded network; only strongest 65 nodes are displayed.
    nx.write_gexf(coupling,report.out/'networks/bibliographic_coupling_full.gexf')
    keep=sorted(coupling,key=lambda k:coupling.degree(k,weight='weight'),reverse=True)[:65]
    draw_network(report,coupling.subgraph(keep).copy(),'bibliographic_coupling','Acoplamento bibliográfico','Pelo menos 2 referências partilhadas; peso = partilhadas / √(nref₁ × nref₂). Subgrafo dos 65 nós de maior força.',labels)
    cocite,freq=projection([r['references_oa'] for r in records],3,65)
    reference_metadata={}
    if cache is not None:
        for p in (cache/'cited_reference_metadata').glob('*.json'):
            w=read_json(p)['work'];reference_metadata[w['id']]=w
    refnames={k:labels[v] for k,v in byid.items()}
    refnames.update({k:f"{w.get('publication_year','?')} · {w.get('title','')[:90]}" for k,w in reference_metadata.items()})
    draw_network(report,cocite,'cocitation','Cocitação de referências','Duas referências ligadas quando citadas pelo mesmo artigo; min. 3 artigos citantes. IDs externos não resolvidos conservados.',refnames)
    report.bars('cited_references', {refnames.get(k,k):v for k,v in freq.items()},'Referências mais citadas pelo conjunto','Frequência de citação nas bibliografias indexadas; nomes disponíveis apenas para referências identificadas.')
    counts={r['paper_id']:len(r['references_oa']) for r in records if r['references_oa']}
    report.bars('reference_list_length',Counter(counts.values()),'Dimensão das bibliografias indexadas','Número de referências no OpenAlex, que pode ser inferior ao número de referências no artigo.',denominator=1)
    # Crossref reference years: never claim a complete reference age distribution.
    ages=[]
    for r in records:
        for ref in (r['cr'] or {}).get('reference',[]):
            y=str(ref.get('year',''))
            if re.fullmatch(r'\d{4}',y):ages.append({'paper_id':r['paper_id'],'citing_year':r['year'],'reference_year':int(y),'age_years':r['year']-int(y)})
    report.table('reference_ages',ages,index=False)
    if ages:report.bars('reference_age_distribution',Counter(x['age_years'] for x in ages),'Idade das referências','Apenas referências Crossref com ano depositado; valores negativos devem ser auditados.',top=35,denominator=1)
    # Source and author co-citation cover ONLY resolved reference metadata, not full bibliographies.
    for unit in ['source','author']:
        lists=[];unit_names={};coverage=0
        for r in records:
            units=set()
            for ref in r['references_oa']:
                w=reference_metadata.get(ref)
                if not w:continue
                if unit=='source':
                    source=(w.get('primary_location') or {}).get('source') or {}
                    if source.get('id'):units.add(source['id']);unit_names[source['id']]=source['display_name']
                else:
                    for author in w.get('authorships',[]):
                        a=author.get('author') or {}
                        if a.get('id'):units.add(a['id']);unit_names[a['id']]=a['display_name']
            if units:coverage+=1
            lists.append(list(units))
        graph,f=projection(lists,3,50)
        draw_network(report,graph,'cocitation_'+unit,'Cocitação por '+('fonte' if unit=='source' else 'autor'),
            f'Cobertura restrita às {len(reference_metadata)} referências de maior frequência com metadados resolvidos; {coverage} artigos contribuem.',unit_names,True)
        report.bars('cited_'+unit,{unit_names.get(k,k):v for k,v in f.items()},'Frequência de '+('fontes citadas' if unit=='source' else 'autores citados'),
            f'Presença por artigo citante; apenas {len(reference_metadata)} referências com metadados resolvidos. Não é um ranking de toda a bibliografia.',provisional=True)
    fwci={labels[r['paper_id']]:r['fwci'] for r in records if r['fwci'] is not None}
    report.bars('fwci_openalex',fwci,'Impacto normalizado por campo — OpenAlex','FWCI tal como fornecido pelo OpenAlex; definição e cobertura dependem da fonte; não mede adequação metodológica.',denominator=1)
    joined=t.dropna(subset=['openalex','crossref'])
    if len(joined):
        fig,ax=plt.subplots(figsize=(8,6));ax.scatter(joined.openalex,joined.crossref,s=22,alpha=.65,color=COLORS[0]);ax.set(xlabel='OpenAlex: citações recebidas',ylabel='Crossref: referências recebidas')
        report.table('citation_provider_comparison',joined,index=False);report.save(fig,'citation_provider_comparison','Sensibilidade à fonte das citações',f'{len(joined)} artigos com ambas as fontes. Contagens não fundidas; datas de cada consulta na tabela.')
    # Local self-citations: author-ID overlap where both publications have OpenAlex authorships.
    ids={r['paper_id']:{a['author']['id'] for a in (r['oa'] or {}).get('authorships',[]) if a.get('author',{}).get('id')} for r in records}
    selfrows=[{'citing':a,'cited':b,'overlapping_author_id':bool(ids[a]&ids[b]) if ids[a] and ids[b] else None} for a,b in g.edges()]
    report.table('local_self_citations',selfrows,index=False)
