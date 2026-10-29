"""Registered extension points: no synthetic data or inference from missing fields."""
import csv,json
from pathlib import Path
from .data import FIELDS,items
from .analysis import frequencies,cross

EXTRA_FIELDS={
 'dependent_variable':'Variável dependente', 'normalisation_variables':'Variáveis de normalização',
 'application_scale':'Escala de aplicação','energy_carriers':'Vetores energéticos','data_origin':'Origem dos dados',
 'sampling_frequency':'Frequência de amostragem','sample_size':'Número de observações',
 'series_duration':'Duração da série','baseline_period':'Período da baseline','baseline_update':'Atualização da baseline',
 'algorithm':'Algoritmo específico','validation_design':'Desenho de validação','reported_metrics':'Métricas reportadas',
 'uncertainty_treatment':'Tratamento da incerteza','residual_diagnostics':'Diagnósticos de resíduos',
 'nonstationarity_treatment':'Tratamento da não estacionariedade','applicability_limits':'Limites de aplicabilidade',
 'implementation_barriers':'Barreiras à implementação','data_code_availability':'Disponibilidade de dados/código',
 'standard_role':'Papel das normas','standard_edition':'Edição das normas'}

def templates(config):
    config=Path(config);config.mkdir(exist_ok=True)
    specs={'verified_level_a.csv':['paper_id','field','value_json','verified','reviewer','evidence'],
           'extended_content.csv':['paper_id','field','value_json','verified','reviewer','evidence'],
           'source_strings.csv':['paper_id','source_string','source_evidence'],
           'external_metrics.csv':['paper_id','metric','value','provider','retrieved_at','source_url']}
    for filename,headers in specs.items():
        p=config/filename
        if not p.exists():
            with p.open('w',newline='',encoding='utf-8') as f:csv.writer(f).writerow(headers)

def extended(report,records,config):
    byid={r['paper_id']:r for r in records};path=Path(config)/'extended_content.csv'
    if path.exists():
        with path.open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):
                if row['verified'].lower()!='true':continue
                if row['paper_id'] not in byid:continue
                if row['field'] not in EXTRA_FIELDS:raise ValueError('Unknown extension field: '+row['field'])
                if not row['reviewer'] or not row['evidence']:raise ValueError('Extended verified fields require reviewer and evidence')
                byid[row['paper_id']]['extended_'+row['field']]=json.loads(row['value_json'])
    for field,label in EXTRA_FIELDS.items():
        key='extended_'+field;k=sum(r.get(key) is not None for r in records)
        if not k:report.skip(key,'Requer nova extração comparável em Corpus A; tabela de entrada: config/extended_content.csv.');continue
        report.bars(key,frequencies(records,key),label,f'Extração verificada disponível em {k}/{len(records)} publicações; não generalizar ao restante conjunto.',provisional=k<len(records))
        m,coverage=cross(records,'enpi_enb_model_types',key)
        report.heatmap(key+'_by_model',m,label+' × família de modelo',f'{coverage} artigos com ambos os campos.',True)
    external=Path(config)/'external_metrics.csv'
    if external.exists():
        with external.open(encoding='utf-8-sig',newline='') as f:rows=[r for r in csv.DictReader(f) if r['paper_id'] in byid]
        for metric,provider,date in sorted(set((r['metric'],r['provider'],r['retrieved_at']) for r in rows)):
            selected=[r for r in rows if (r['metric'],r['provider'],r['retrieved_at'])==(metric,provider,date)]
            report.bars('external_'+__import__('hashlib').sha256((metric+provider+date).encode()).hexdigest()[:10],{r['paper_id']:float(r['value']) for r in selected},metric,f'Fonte: {provider}; data: {date}; {len(selected)} publicações observadas.',denominator=1)
    for name,reason in [('patents_policy_attention','Exige métricas externas com fonte e data; config/external_metrics.csv.'),
                        ('unique_studies_sites','A unidade extraída é publicação; é necessário ligar artigos do mesmo estudo e enumerar instalações.'),
                        ('global_author_h_index','O corpus não é a produção completa de cada autor; índices de carreira exigem consulta própria.')]:report.skip(name,reason)
