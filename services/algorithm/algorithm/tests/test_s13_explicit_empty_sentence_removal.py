"""S13 deletion tombstones must not delete a supported Chapter or invent facts."""
from copy import deepcopy
from diary_one_ci import product_editor as p


def example():
    memory={'id':'C02','kind':'CHAPTER',
        'source_sentences':[{'source_index':i} for i in range(4)]}
    raw={'items':[{'id':'C02','title':'岩石区街头乐手',
        'title_fact_ids':['F038'],'decision':'PUBLISH','reason':'删去不支持的混合来源句子',
        'voice_issues':[],'sentences':[
          {'text':'弹奏吉他的乐手出现在画面里。','fact_ids':['F038'],'source_index':0},
          {'text':'','fact_ids':[],'source_index':1},
          {'text':'糖果店门口有彩色的装饰。','fact_ids':['F031'],'source_index':2},
          {'text':'','fact_ids':[],'source_index':3}]}]}
    return memory,raw


def test_explicit_empty_sentence_tombstones_can_be_omitted_with_full_audit():
    m,raw=example()
    before=deepcopy(raw)
    result,audit=p.normalize_explicit_empty_copy_removals(raw,[m],stage='S13_PRODUCT_COPY_REPAIR')
    assert raw==before
    assert [z['source_index'] for z in result['items'][0]['sentences']]==[0,2]
    assert [z['fact_ids'] for z in result['items'][0]['sentences']]==[['F038'],['F031']]
    assert len(audit)==1
    assert audit[0]['removed_source_indices']==[1,3]
    assert audit[0]['rule']=='EXPLICIT_EMPTY_SENTENCE_TOMBSTONE_OMITTED_NO_FACT_CREATED'


def test_never_drop_nonempty_claim_without_citation_or_protected_local_repair():
    m,raw=example()
    raw['items'][0]['sentences'][1]['text']='没有事实支撑的动作'
    kept,audit=p.normalize_explicit_empty_copy_removals(raw,[m],stage='S13')
    assert kept['items'][0]['sentences'][1]['text']=='没有事实支撑的动作'
    assert len(kept['items'][0]['sentences'])==3
    assert audit[0]['removed_source_indices']==[3]
    m['local_repair_scope']={'target_indices':[1,3]}
    local,audit=p.normalize_explicit_empty_copy_removals(raw,[m],stage='S13')
    assert local==raw and not audit


def test_cannot_omit_all_sentences_or_unknown_source_index():
    m,raw=example()
    raw['items'][0]['sentences']=[
      {'text':'','fact_ids':[],'source_index':0},
      {'text':'','fact_ids':[],'source_index':1}]
    normalized,audit=p.normalize_explicit_empty_copy_removals(raw,[m],stage='S13')
    assert normalized==raw and not audit
    raw['items'][0]['sentences'][0]['source_index']=999
    normalized,audit=p.normalize_explicit_empty_copy_removals(raw,[m],stage='S13')
    assert normalized['items'][0]['sentences'][0]['source_index']==999
    assert len(normalized['items'][0]['sentences'])==1


def test_no_implicit_tombstones_in_regular_writer_or_semantic_review():
    m,raw=example()
    assert p.normalize_explicit_empty_copy_removals(raw,[{'id':'C02','kind':'AHA'}],stage='S13')==(raw,[])
