import unittest
from pathlib import Path
from biblio.data import read_json,equivalent,authors,doi
from biblio.analysis import cross,frequencies
from biblio.networks import projection
from biblio.prisma import counts
from biblio.normalize import countries

BASE=Path(__file__).resolve().parents[1]

class AnalysisIntegrity(unittest.TestCase):
    def test_roster_includes_every_b_without_duplicates(self):
        s=read_json(BASE/'cache/input_snapshot.json');r=s['records']
        self.assertEqual(len(r),len({x['paper_id'] for x in r}))
        self.assertEqual(sum(x['in_corpus_a'] for x in r),331)
        self.assertEqual(sum(x['in_corpus_b'] for x in r),42)
        self.assertEqual({x['paper_id'] for x in r if x['in_corpus_b'] and not x['in_corpus_a']},set(s['membership_conflicts']))
    def test_no_unilateral_model_precedence(self):
        s=read_json(BASE/'cache/input_snapshot.json')
        for r in s['records']:
            for field,status in r['status'].items():
                if status in ['uma única extração IA','divergência IA por resolver','sem extração']:
                    self.assertIsNone(r[field])
    def test_multilabel_counts_each_article_once_per_cell(self):
        rows=[{'a':['x','x','y'],'b':['z','z']},{'a':['x'],'b':None}]
        m,n=cross(rows,'a','b');self.assertEqual(n,1);self.assertEqual(m.loc['x','z'],1);self.assertEqual(m.loc['y','z'],1)
    def test_author_parser_preserves_surname_initials(self):
        self.assertEqual(authors('Silva, A. and Ribeiro, B. and Silva, A.'),['Silva, A.','Ribeiro, B.'])
    def test_order_invariance_not_null_agreement(self):
        self.assertTrue(equivalent(['a','b'],['b','a']))
        self.assertFalse(equivalent(None,None))
    def test_projection_is_cooccurrence_not_transitivity(self):
        g,_=projection([['a','b'],['a','c']],1,20)
        self.assertTrue(g.has_edge('a','b'));self.assertTrue(g.has_edge('a','c'));self.assertFalse(g.has_edge('b','c'))
    def test_prisma_conserves_reports_and_keeps_unknowns(self):
        c,e=counts(read_json(BASE/'cache/input_snapshot.json'),BASE/'config/prisma_pending.json')
        self.assertEqual(c['reports_sought'],596);self.assertEqual(c['reports_not_retrieved'],137)
        self.assertEqual(c['fulltext_excluded'],128);self.assertEqual(c['included_publications'],331)
        self.assertIsNone(e['scopus_identified']);self.assertEqual(c['b_outside_a'],2)
    def test_doi_normalization(self):self.assertEqual(doi('https://doi.org/10.1000/ABC'),'10.1000/abc')
    def test_country_missing_is_not_not_applicable(self):
        self.assertEqual(countries(None),[])
        self.assertEqual(countries('not applicable'),['Não aplicável'])
        self.assertEqual(countries('not reported'),['Não reportado no artigo'])

if __name__=='__main__':unittest.main()
