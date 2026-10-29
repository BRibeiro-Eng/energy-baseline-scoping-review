"""Read-only adapters. Disagreement is missing data, never automatic adjudication."""
from __future__ import annotations
import csv, hashlib, importlib.util, json, re, unicodedata
from pathlib import Path
from collections import Counter

FIELDS = ['paper_type','multi_site','country_region','sector_of_activity',
          'type_of_organisation','ems_standard','mv_protocol','regulatory_driver',
          'enpi_enb_model_types','complementary_methodologies']
MULTI = set(FIELDS[5:])
MISSING = 'Por resolver / sem extração'

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_json(path, data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')

def norm(value):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(value))).strip()

def doi(value):
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)','',str(value or '').strip(),flags=re.I).lower()

def authors(value):
    # Rayyan export is BibTeX-style; a comma is surname/initial separator, NOT author separator.
    return list(dict.fromkeys(norm(x) for x in re.split(r'\s+and\s+|;',value or '') if x.strip()))

def items(value):
    if value is None: return []
    return list(dict.fromkeys(value if isinstance(value,list) else [str(value)]))

def val(record,field):
    stage='stage1' if field=='paper_type' else 'stage2'
    cell=(record.get(stage) or {}).get(field)
    return cell.get('value') if isinstance(cell,dict) else cell

# 2026-09-21: a concordancia passou a ser avaliada sobre a forma canonica.
# Ate aqui comparavam-se as strings em bruto e so os valores sobreviventes
# iam ao normalize.py. Duas escritas da mesma coisa ("automotive sector" e
# "automotive manufacturing sector", "Ecuador" e "coast of Ecuador") eram
# declaradas divergentes e descartadas antes de chegarem ao normalizador que
# as teria resolvido. Passa a normalizar-se antes de comparar, com as mesmas
# funcoes do normalize.py: nao se introduz vocabulario novo nem juizo humano.
# Exige-se igualdade exacta da forma canonica; intersecao parcial continua a
# ser divergencia por resolver. O balde residual do mapeador de sectores
# ("Por classificar / outro") nao estabelece equivalencia -- dois textos
# diferentes que o regex nao cobre cairiam ambos la e seriam dados como
# concordantes sem o ser; nesse caso compara-se o texto em bruto.
RESIDUAL_NAO_EQUIVALE = {'Por classificar / outro'}

def canonical(value, field=None):
    if value is None: return None
    from .normalize import sector, countries, keyword  # tardio: normalize importa data
    if field == 'sector_of_activity': return tuple(sorted(sector(value)))
    if field == 'country_region':     return tuple(sorted(countries(value)))
    if field in MULTI:                return tuple(sorted({keyword(x) for x in items(value)}))
    if isinstance(value,list):        return tuple(sorted({norm(x).casefold() for x in value}))
    return (norm(value).casefold(),)

def equivalent(a,b,field=None):
    if a is None or b is None:return False
    if field is None:
        if isinstance(a,list) and isinstance(b,list): return sorted(set(map(norm,a)))==sorted(set(map(norm,b)))
        return norm(a).casefold()==norm(b).casefold()
    ca,cb=canonical(a,field),canonical(b,field)
    if not ca or not cb: return False
    if set(ca)-RESIDUAL_NAO_EQUIVALE or set(cb)-RESIDUAL_NAO_EQUIVALE:
        return ca==cb
    return norm(a).casefold()==norm(b).casefold()

def load_snapshot(root:Path, snapshot_path:Path, refresh=False):
    """Freeze exact inputs once. Upstream stores are never edited by this package."""
    if snapshot_path.exists() and not refresh:return read_json(snapshot_path)
    spec=importlib.util.spec_from_file_location('_corpus_profile_readonly',root/'output/corpus_profile.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    R=module.rosters(); A=set(R['corpus_a']);B=set(R['corpus_b'])
    assert len(A)==331 and len(B)==42, 'Roster changed: inspect before refreshing this frozen analysis.'
    population=A|B  # preserve inconsistent membership explicitly, never silently drop B articles
    csvpath=root/'data/articles.csv'
    with csvpath.open(encoding='utf-8-sig',newline='') as f: raw={r['key']:r for r in csv.DictReader(f)}
    assert population<=raw.keys()
    records=[]; lineage=[]; paths={csvpath,root/'output/corpus_profile.py',root/'CORPUS_CLOSURE_2026-09-12.md'}
    for key in sorted(population):
        row=raw[key]; stage0path=root/f'output/stage0/{key}.json';paths.add(stage0path)
        s0=read_json(stage0path);md=s0['metadata']
        rec={'paper_id':key,'in_corpus_a':key in A,'in_corpus_b':key in B,'group':'B' if key in B else 'A sem B',
             'title':row['title'],'year':int(row['year']), 'source':norm(row['journal']).casefold(),
             'authors':authors(row['authors']),'doi':doi(row['doi']),
             'keywords':list(dict.fromkeys(norm(x).casefold() for x in row['keywords'].split(';') if x.strip())),
             'abstract':row['abstract'],'language':row['language'],
             'document_type':md.get('document_type'), 'source_string':md.get('source_string'),
             'via_snowballing':s0.get('flags',{}).get('via_snowballing',False)}
        # Historical export counts remain a distinct series; never merge with live counts.
        hit=re.search(r'Cited By:\s*(\d+)',row['notes']);date=re.search(r'Export Date:\s*([^;|]+)',row['notes'])
        rec['export_citations']=int(hit.group(1)) if hit else None
        rec['export_date']=date.group(1).strip() if date else None
        rec['views']={}; rec['status']={}
        for model,store in [('claude',R['C']),('chatgpt',R['G'])]:
            rec['views'][model]={f:val(store.get(key,{}),f) for f in FIELDS}
            path=root/f'production/{model}/outputs/validated/{key}.json'
            if path.exists():paths.add(path)
        for field in FIELDS:
            a,b=rec['views']['claude'][field],rec['views']['chatgpt'][field]
            if equivalent(a,b,field): chosen=a;status='concordância IA; sem validação humana integral'
            elif a is None and b is None:chosen=None;status='sem extração'
            elif a is None or b is None:chosen=None;status='uma única extração IA'
            else:chosen=None;status='divergência IA por resolver'
            rec[field]=chosen;rec['status'][field]=status
            lineage.append({'paper_id':key,'field':field,'status':status,'claude':a,'chatgpt':b})
        records.append(rec)
    # Membership review files are provenance of roster, not proof of verified Level-A cells.
    reviewdir=root/'production/reviewer_workspace/reviews/membership/blind'
    paths.update(f for f in reviewdir.glob('rayyan-*.json') if f.name.count('.')==1)
    flags={k:read_json(root/f'data/{k}.json') for k in ['excluded_duplicates','excluded_records','non_retrieved_records']}
    paths.update(root/f'data/{k}.json' for k in flags)
    decisions=Counter()
    for row in raw.values():
        m=re.search(r'RAYYAN-INCLUSION:.*?=>"([^"]+)"',row['notes'])
        decisions[m.group(1) if m else 'unknown']+=1
    modelkeys=set(R['C'])&set(R['G'])
    assert len(modelkeys)==448 and A<=modelkeys
    nonretrieved={r['key'] for r in flags['non_retrieved_records']['records']}
    excluded0={r['key'] for r in flags['excluded_records']['entries']}
    duplicates={r['excluded'] for r in flags['excluded_duplicates']['entries']}
    assert not A&(nonretrieved|excluded0|duplicates)
    result={'schema_version':1,'root':str(root),'corpus_a_n':len(A),'corpus_b_n':len(B),
            'records':records,'membership_conflicts':sorted(B-A),
            'cell_provenance':lineage,'screening_counts':dict(decisions),
            'export_n':len(raw),'stage1_n':len(modelkeys),'registries':flags,
            'input_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}
    write_json(snapshot_path,result);return result

def apply_overrides(records,path):
    """Only explicitly verified imported cells override provisional values."""
    if not path.exists():return records
    bykey={r['paper_id']:r for r in records}
    with path.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            if row.get('verified','').lower()!='true':continue
            if row['paper_id'] not in bykey or row['field'] not in FIELDS:raise ValueError('Invalid override key/field')
            if not row.get('evidence') or not row.get('reviewer'):raise ValueError('Verified overrides require evidence and reviewer')
            value=json.loads(row['value_json']);rec=bykey[row['paper_id']]
            rec[row['field']]=value;rec['status'][row['field']]='verificado: '+row['reviewer']
    return records
