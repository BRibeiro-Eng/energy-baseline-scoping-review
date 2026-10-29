"""Accessible static exports, complete underlying tables and a local HTML gallery."""
from __future__ import annotations
import html,json,re,textwrap
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#56B4E9','#D55E00','#333333']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':13,
    'axes.labelsize':10,'figure.dpi':110,'savefig.dpi':300,'pdf.fonttype':42,
    'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})

def slug(s):return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def wrap(s,width=36):return '\n'.join(textwrap.wrap(str(s),width=width))

class Report:
    def __init__(self,out,population,n):
        self.out=Path(out);self.n=n;self.population=population;self.catalog=[];self.skipped=[]
        for p in ['figures','tables','networks']: (self.out/p).mkdir(parents=True,exist_ok=True)
        self.book=PdfPages(self.out/'figures/atlas.pdf')
    def table(self,name,data,index=True):
        if not isinstance(data,pd.DataFrame):data=pd.DataFrame(data)
        data.to_csv(self.out/'tables'/f'{name}.csv',index=index,encoding='utf-8-sig')
    def save(self,fig,name,title,caption='',provisional=False):
        stamp=f'{self.population} · n={self.n}'
        if provisional:stamp+=' · CONTEÚDO PROVISÓRIO / EXPLORATÓRIO'
        fig.suptitle(title,x=.02,ha='left',fontweight='bold',fontsize=14,y=.985)
        fig.text(.02,.018,wrap(stamp+'\n'+caption,135),ha='left',va='bottom',fontsize=8,color='#444444')
        fig.tight_layout(rect=(0,.12,1,.91))
        for fmt in ['png','pdf','svg']:
            fig.savefig(self.out/'figures'/f'{name}.{fmt}',bbox_inches='tight',facecolor='white')
        self.book.savefig(fig,bbox_inches='tight',facecolor='white');plt.close(fig)
        self.catalog.append({'id':name,'title':title,'caption':caption,'provisional':provisional,
                             'png':f'figures/{name}.png','pdf':f'figures/{name}.pdf','svg':f'figures/{name}.svg'})
    def skip(self,name,reason):self.skipped.append({'analysis':name,'reason':reason})
    def bars(self,name,series,title,caption='',top=20,provisional=False,denominator=None):
        s=pd.Series(series,dtype=float).sort_values(ascending=False)
        self.table(name,pd.DataFrame({'n':s,'percent_of_population':100*s/self.n}) if denominator is None else pd.DataFrame({'value':s}))
        if s.empty or s.sum()==0:self.skip(name,'Sem observações suficientes.');return
        t=s.head(top).sort_values();fig,ax=plt.subplots(figsize=(10,max(4.7,.38*len(t)+2)))
        y=np.arange(len(t));ax.barh(y,t.values,color=COLORS[0]);ax.set_yticks(y,[wrap(x,40) for x in t.index])
        ax.set_xlabel('Número de publicações' if denominator is None else 'Valor / contagem (ver legenda)')
        ax.set_xlim(0,max(t.values)*1.22)
        for i,v in enumerate(t.values):ax.text(v+max(t.values)*.015,i,f'{v:g}',va='center',fontsize=9)
        self.save(fig,name,title,caption+f' Mostradas {len(t)} de {len(s)} categorias; tabela CSV completa.',provisional)
    def heatmap(self,name,matrix,title,caption='',provisional=False,normalize=False):
        matrix=matrix.fillna(0);self.table(name,matrix)
        if matrix.empty or matrix.to_numpy().sum()==0:self.skip(name,'Sem pares de observações suficientes.');return
        if normalize:
            shown=matrix.div(matrix.sum(axis=1).replace(0,np.nan),axis=0)*100
        else:shown=matrix
        # All cells remain in CSV; limit display by marginal count, never silently drop from table.
        rows=matrix.sum(axis=1).nlargest(18).index;cols=matrix.sum(axis=0).nlargest(16).index
        temporal=lambda values: all(re.fullmatch(r'\d{4}(?:[–-]\d{4})?',str(v)) for v in values)
        if temporal(rows):rows=sorted(rows,key=str)
        if temporal(cols):cols=sorted(cols,key=str)
        t=shown.loc[rows,cols].fillna(0)
        fig,ax=plt.subplots(figsize=(max(9,.6*len(cols)+4),max(5,.45*len(rows)+3)))
        im=ax.imshow(t.to_numpy(),aspect='auto',cmap='cividis',vmin=0)
        ax.set_xticks(range(len(cols)),[wrap(x,22) for x in cols],rotation=45,ha='right')
        ax.set_yticks(range(len(rows)),[wrap(x,34) for x in rows])
        if len(rows)*len(cols)<=230:
            threshold=t.to_numpy().max()*.55
            for i in range(len(rows)):
                for j in range(len(cols)):
                    v=t.iloc[i,j];ax.text(j,i,f'{v:.0f}',ha='center',va='center',fontsize=8,color='white' if v<threshold else 'black')
        fig.colorbar(im,ax=ax,shrink=.7,label='% por linha' if normalize else 'Publicações / pares')
        self.save(fig,name,title,caption+' Tabela completa em CSV; seleção visual por contagem marginal.',provisional)
    def finish(self,summary):
        self.book.close();self.table('analyses_pending',self.skipped,index=False)
        (self.out/'catalog.json').write_text(json.dumps(self.catalog,ensure_ascii=False,indent=2),encoding='utf-8')
        intro=html.escape(summary).replace('\n','<br>')
        cards=[]
        for x in self.catalog:
            data_link=f' · <a href="tables/{x["id"]}.csv">Dados CSV</a>' if (self.out/'tables'/f'{x["id"]}.csv').exists() else ''
            cards.append(f'<article><h2>{html.escape(x["title"])}</h2><a href="{x["png"]}"><img loading="lazy" src="{x["png"]}" alt="{html.escape(x["title"])}"></a><p>{html.escape(x["caption"])}</p><a href="{x["pdf"]}">PDF</a> · <a href="{x["svg"]}">SVG editável</a>{data_link}</article>')
        pending=''.join(f'<li>{html.escape(x["analysis"])}: {html.escape(x["reason"])}</li>' for x in self.skipped)
        content='''<!doctype html><html lang="pt"><meta charset="utf-8"><title>Corpus A · Bibliometria</title><style>body{max-width:1450px;margin:40px auto;padding:0 24px;font:16px/1.5 system-ui;color:#193047;background:#f3f6f8}header{padding:24px;background:white;border-left:5px solid #0072B2}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:24px}article{background:white;padding:20px;border-radius:8px}img{width:100%;height:auto}h1{font-size:32px}h2{font-size:19px}a{color:#0072B2}input{padding:12px;margin:20px 0;width:90%;max-width:500px}</style>'''
        content+=f'<header><h1>Bibliometria e PRISMA</h1><p>{intro}</p><a href="figures/atlas.pdf">Atlas completo em PDF</a> · <a href="catalog.json">Catálogo</a></header><input id="search" placeholder="Filtrar figuras por título ou legenda"><main>'+''.join(cards)+f'</main><h2>Análises condicionadas por dados</h2><ul>{pending}</ul>'
        content+='''<script>document.querySelector('#search').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('article').forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(q))})</script></html>'''
        (self.out/'index.html').write_text(content,encoding='utf-8')
