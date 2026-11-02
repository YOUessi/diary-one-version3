"""The V05 13+ image route must preserve all per-frame clue identities."""

from diary_one_ci import frame_observation as f

def test_batched_clues_return_one_flat_structured_envelope(monkeypatch):
    calls = []
    candidates=[{"candidate_id":f"P{i:03d}"} for i in range(1,26)]
    evidence=[object() for _ in candidates]
    def fake_review(batch, facts, ask, *, evidence, stage, stage_runs=None):
        calls.append(stage)
        assert len(batch)==len(evidence)
        return {"candidate_scene_clues": {
            c["candidate_id"]:[{"scene_observation_id":"FO:"+c["candidate_id"]}]
            for c in batch}, "issues":[], "evidence_scope":"fixture"}, {
                "frame_claim_supports":[], "frame_ledger":[
                    {"candidate_id":c["candidate_id"],"status":"VERIFIED_REFERENCE_SCOPE"}
                    for c in batch], "whole_response_invalid":False}
    monkeypatch.setattr(f,"review_frame_observations",fake_review)
    clues,audit=f.review_frame_observations_batched(
        candidates, {}, None, evidence=evidence, batch_size=12)
    assert len(calls)==3
    assert set(clues["candidate_scene_clues"])=={c["candidate_id"] for c in candidates}
    assert len(clues["candidate_scene_clues"]["P025"])==1
    assert not any("candidate_scene_clues" in row for row in clues["candidate_scene_clues"].values())
    assert audit["partial_failures"] is False
    assert audit["all_candidate_ids"]==[c["candidate_id"] for c in candidates]
