#!/usr/bin/env python3
"""Run offline from cached metadata; use --enrich explicitly to refresh missing metadata."""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
from biblio.data import load_snapshot,apply_overrides,write_json
from biblio.normalize import derive
from biblio.plots import Report
from biblio import analysis,networks,prisma,extensions,enrich

BASE=Path(__file__).resolve().parent

def run(output=None,population='union',enrich_missing=False):
    config=BASE/'config';cache=BASE/'cache';extensions.templates(config)
    snapshot=load_snapshot(BASE.parent,cache/'input_snapshot.json')
    if enrich_missing:enrich.run(cache/'input_snapshot.json',cache/'openalex')
    records=snapshot['records']
    if population=='a':records=[r for r in records if r['in_corpus_a']]
    elif population!='union':raise ValueError('population must be a or union')
    assert len({r['paper_id'] for r in records})==len(records)
    if population=='union':assert sum(r['in_corpus_b'] for r in records)==snapshot['corpus_b_n']
    records=derive(apply_overrides(records,config/'verified_level_a.csv'),config)
    with (config/'source_strings.csv').open(encoding='utf-8-sig',newline='') as f:
        source_rows={r['paper_id']:r for r in csv.DictReader(f)}
    for r in records:
        if r['paper_id'] in source_rows:
            x=source_rows[r['paper_id']]
            if x['source_string'] not in ['A','B','both'] or not x['source_evidence']:raise ValueError('Invalid source provenance')
            r['source_string']=x['source_string']
    out=Path(output) if output else BASE/'results'/('union_inclusiva' if population=='union' else 'corpus_a_registado')
    label='A∪B exploratório' if population=='union' and snapshot['membership_conflicts'] else 'Corpus A registado'
    report=Report(out,label,len(records))
    print(f'{label}: {len(records)} publicações; B incluído: {sum(r["in_corpus_b"] for r in records)}',flush=True)
    networks.attach_metadata(records,cache,report)
    report.table('analysis_dataset',pd.DataFrame([{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items() if k not in ['oa','cr']} for r in records]),index=False)
    report.table('cell_provenance',[r for r in snapshot['cell_provenance'] if r['paper_id'] in {x['paper_id'] for x in records}],index=False)
    for name,fn in [('Caracterização',lambda:analysis.descriptive(report,records)),
                    ('Cruzamentos',lambda:analysis.cross_analyses(report,records)),
                    ('Interseções',lambda:[analysis.intersections(report,records,f) for f in ['enpi_enb_model_types','ems_standard','mv_protocol']]),
                    ('Aluvial',lambda:analysis.alluvial(report,records)),
                    ('Qualidade',lambda:analysis.quality(report,records,snapshot)),
                    ('Colaboração',lambda:networks.collaboration(report,records)),
                    ('Temas',lambda:networks.keyword_analyses(report,records)),
                    ('Citações',lambda:networks.citations(report,records,cache)),
                    ('PRISMA',lambda:prisma.draw(report,snapshot,config/'prisma_pending.json')),
                    ('Extensões',lambda:extensions.extended(report,records,config))]:
        print(name,flush=True);fn()
    summary=(f'{label}: {len(records)} publicações; registos de B nesta vista: {sum(r["in_corpus_b"] for r in records)}.\n'
        f'Listas de origem: A={snapshot["corpus_a_n"]}, B={snapshot["corpus_b_n"]}; conflitos B fora de A: {len(snapshot["membership_conflicts"])}.\n'
        'Level A: valores concordantes entre IA, sujeitos a verificação; divergências e extrações únicas ficam por resolver.\n'
        'Metadados bibliográficos enriquecidos são observações de OpenAlex/Crossref, com cobertura e data; não constituem avaliação de qualidade.\n'
        'PRISMA é um rascunho: identificação inicial, snowballing, motivos detalhados e composição A/B por fechar.')
    report.finish(summary)
    files=[p for folder in [BASE/'biblio',config,cache/'openalex',cache/'crossref',cache/'cited_reference_metadata'] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in str(p)]
    files += [cache/'input_snapshot.json',BASE/'run_analysis.py']
    manifest={'created_at':datetime.now(timezone.utc).isoformat(),'population':population,'n':len(records),
      'b_included':sum(r['in_corpus_b'] for r in records),'figures_n':len(report.catalog),'pending_n':len(report.skipped),
      'membership_conflicts':snapshot['membership_conflicts'],'python':sys.version,
      'inputs_sha256':{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}}
    write_json(out/'run_manifest.json',manifest)
    versions={}
    import importlib.metadata
    for package in ['numpy','pandas','matplotlib','networkx','scikit-learn','requests','pycountry','nbformat','nbclient']:
        try:versions[package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:versions[package]='not installed'
    write_json(out/'package_versions.json',versions)
    print(f'Concluído: {len(report.catalog)} figuras → {out}',flush=True)
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--population',choices=['a','union'],default='union');p.add_argument('--enrich',action='store_true')
    args=p.parse_args();run(args.output,args.population,args.enrich)
