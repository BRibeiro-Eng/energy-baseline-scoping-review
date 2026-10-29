"""Conservative, reviewable derivations; original fields are always retained."""
import re
from pathlib import Path
from .data import norm,items,read_json

SECTORS={
 'Refinação de petróleo':r'oil refin|petroleum refin|crude oil',
 'Petroquímica / polímeros':r'petrochem|ethylene|propylene|polymer|plastic|rubber',
 'Cimento / cal':r'cement|clinker|lime production',
 'Pasta e papel':r'pulp|paper mill|paper industr|paper manufact',
 'Metais / metalomecânica':r'steel|metal|alumin|foundr|forg|machining|die.cast',
 'Química / farmacêutica':r'chemical|pharma|ammonia|fertili',
 'Vidro / cerâmica':r'glass|ceramic|brick',
 'Alimentação / bebidas / agricultura':r'food|beverage|dairy|milk|sugar|brew|agric|coffee|corn|wine|aquacult',
 'Têxtil / couro':r'textile|leather|garment',
 'Água / resíduos':r'wastewater|water treatment|waste treatment|sewage',
 'Energia / utilidades':r'power plant|power generat|district heat|electricity generat|boiler',
 'Edifícios / serviços públicos':r'building|universit|school|office|hospital|municipal|public organ|educat',
 'Transportes / logística':r'transport|airport|rail|logistic|distribution cent',
 'Automóvel / componentes':r'automotive|automobile|car manufact|vehicle',
 'Indústria não especificada':r'^manufacturing$|^industrial sector$|^industry$|^consumer goods$',
}
ALIASES={'enpi':'energy performance indicator','enpis':'energy performance indicator',
 'energy performance indicators':'energy performance indicator','enb':'energy baseline',
 'energy baselines':'energy baseline','iso50001':'iso 50001','iso 50001:2011':'iso 50001',
 'iso 50001:2018':'iso 50001','iso50006':'iso 50006','specific energy consumption (sec)':'specific energy consumption',
 'sec':'specific energy consumption','energy management systems':'energy management system',
 'neural networks':'neural network','artificial neural networks':'artificial neural network',
 'regression models':'regression model'}

def keyword(s,aliases=None):
    s=norm(s).casefold().replace('iso-','iso ')
    return (aliases or ALIASES).get(s,s)

def sector(s):
    if s is None:return []
    if str(s).casefold()=='not applicable':return ['Não aplicável']
    if str(s).casefold() in ['not specified','not reported']:return ['Não reportado no artigo']
    matches=[k for k,pattern in SECTORS.items() if re.search(pattern,str(s),re.I)]
    return matches or ['Por classificar / outro']

def countries(s):
    if not s:return []
    if str(s).casefold()=='not applicable':return ['Não aplicável']
    if str(s).casefold() in ['not specified','not reported']:return ['Não reportado no artigo']
    # 2026-09-21: rebenta em vez de degradar em silencio. A versao anterior
    # devolvia a string em bruto se o pycountry faltasse, sem aviso, o que
    # produzia uma tabela de paises silenciosamente errada.
    try:import pycountry
    except ImportError as e:
        raise RuntimeError('pycountry em falta: a normalizacao de paises nao pode correr') from e
    text=norm(s).casefold();found=[]
    special={'uk':'United Kingdom','u.k.':'United Kingdom','usa':'United States','u.s.':'United States',
             'iran':'Iran, Islamic Republic of','south korea':'Korea, Republic of','russia':'Russian Federation',
             'taiwan':'Taiwan, Province of China','czech republic':'Czechia','turkey':'Türkiye',
             'vietnam':'Viet Nam','bolivia':'Bolivia, Plurinational State of','venezuela':'Venezuela, Bolivarian Republic of'}
    for country in pycountry.countries:
        if re.search(r'(?<!\w)'+re.escape(country.name.casefold())+r'(?!\w)',text):found.append(country.name)
    for alias,name in special.items():
        if re.search(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',text):found.append(name)
    return sorted(set(found))

def derive(records,config):
    aliases=dict(ALIASES)
    custom=Path(config)/'keyword_aliases.json'
    if custom.exists():aliases.update(read_json(custom))
    for r in records:
        r['keywords_clean']=sorted(set(keyword(k,aliases) for k in r['keywords']))
        r['sectors_derived']=sector(r['sector_of_activity'])
        r['countries_case']=countries(r['country_region'])
        r['country_unmapped']=r['country_region'] is not None and not r['countries_case']
        if r['country_unmapped']:r['countries_case']=['Por normalizar: localização em texto']
        r['period']=f'{r["year"]//5*5}–{r["year"]//5*5+4}'
        r['author_count']=len(r['authors'])
        r['model_count']=len([x for x in items(r['enpi_enb_model_types']) if x not in ['none','not applicable']]) if r['enpi_enb_model_types'] is not None else None
    return records
