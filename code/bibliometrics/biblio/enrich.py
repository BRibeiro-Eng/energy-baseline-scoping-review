"""Public metadata retrieval with DOI identity checks, local cache and bounded retries."""
from __future__ import annotations
import argparse, time, re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import requests
from .data import read_json,write_json,doi

def fetch(session,url,params=None):
    for attempt in range(3):
        try:
            r=session.get(url,params=params,timeout=40)
            if r.status_code in (429,500,502,503,504):
                time.sleep(min(20,2**attempt+1));continue
            r.raise_for_status();return r.json()
        except requests.RequestException:
            if attempt==2:raise
            time.sleep(2**attempt)
    raise RuntimeError('Provider unavailable after retries')

def run(snapshot,cache):
    cache.mkdir(parents=True,exist_ok=True);records=read_json(snapshot)['records']
    targets={doi(r['doi']):r['paper_id'] for r in records if r['doi']}
    session=requests.Session();session.headers['User-Agent']='CorpusA-Bibliometrics/1.0 (academic metadata analysis)'
    missing=[d for d,key in targets.items() if not (cache/f'{key}.json').exists()]
    for start in range(0,len(missing),20):
        batch=missing[start:start+20]
        try:
            result=fetch(session,'https://api.openalex.org/works',{'filter':'doi:'+'|'.join(batch),'per_page':100})
            for work in result['results']:
                d=doi(work.get('doi'))
                if d in batch:
                    write_json(cache/f'{targets[d]}.json',{'provider':'OpenAlex','retrieved_at':datetime.now(timezone.utc).isoformat(),
                                                        'lookup_doi':d,'work':work})
            print(f'OpenAlex: batch {start+1}–{min(start+20,len(missing))}/{len(missing)}; cached {len(list(cache.glob("rayyan-*.json")))}',flush=True)
        except Exception as e:
            write_json(cache/f'error_batch_{start}.json',{'dois':batch,'error':str(e),'retrieved_at':datetime.now(timezone.utc).isoformat()})
            print('OpenAlex batch unavailable:',type(e).__name__,flush=True)
        time.sleep(0.3)
    # Crossref DOI lookups add deposited reference DOIs, dates, funders and a separate citation source.
    crdir=cache.parent/'crossref';crdir.mkdir(exist_ok=True)
    for i,(d,key) in enumerate(targets.items()):
        target=crdir/f'{key}.json'
        if target.exists():continue
        try:
            work=fetch(session,'https://api.crossref.org/works/'+requests.utils.quote(d,safe=''))['message']
            if doi(work.get('DOI'))!=d:raise ValueError('DOI mismatch')
            write_json(target,{'provider':'Crossref','retrieved_at':datetime.now(timezone.utc).isoformat(),'lookup_doi':d,'work':work})
        except Exception as e:
            write_json(crdir/f'error_{key}.json',{'doi':d,'error':str(e)})
        if (i+1)%25==0:print(f'Crossref: {i+1}/{len(targets)}',flush=True)
        time.sleep(0.22)
    refdir=cache.parent/'cited_reference_metadata';refdir.mkdir(exist_ok=True)
    frequencies=Counter()
    for path in cache.glob('rayyan-*.json'):
        frequencies.update(set(read_json(path)['work'].get('referenced_works') or []))
    for i,(ref,count) in enumerate(frequencies.most_common(80)):
        target=refdir/(ref.rsplit('/',1)[-1]+'.json')
        if target.exists():continue
        try:
            work=fetch(session,'https://api.openalex.org/works/'+ref.rsplit('/',1)[-1])
            if work.get('id')!=ref:raise ValueError('Reference ID mismatch')
            write_json(target,{'provider':'OpenAlex','retrieved_at':datetime.now(timezone.utc).isoformat(),'work':work})
        except Exception as e:print('Reference metadata unavailable',ref,type(e).__name__,flush=True)
        if (i+1)%20==0:print(f'Cited-reference metadata: {i+1}/80',flush=True)
        time.sleep(.25)

def abstract(work):
    inv=work.get('abstract_inverted_index') or {}
    return ' '.join(word for _,word in sorted((pos,word) for word,positions in inv.items() for pos in positions))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--cache',type=Path,required=True)
    a=p.parse_args();run(a.snapshot,a.cache)
