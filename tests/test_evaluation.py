from app.core.services.evaluation_service import (
    TaskScore, CriterionScoreInput, criterion_score, function_score, competency_score, gating_ok
)

def test_scores_and_gating():
    # Build sample profile
    crit1 = CriterionScoreInput(weight=1.0, tasks=[TaskScore(1.0, 1.0)])
    crit2 = CriterionScoreInput(weight=1.0, tasks=[TaskScore(1.0, 0.75)])
    prof = [crit1, crit2]  # prof_oriented
    mgmt = [CriterionScoreInput(weight=1.0, tasks=[TaskScore(1.0, 0.5)])]
    ability = [CriterionScoreInput(weight=1.0, tasks=[TaskScore(1.0, 1.0)])]
    add = [CriterionScoreInput(weight=1.0, tasks=[TaskScore(1.0, 1.0)])]

    comp = competency_score({
        "prof_oriented": prof,
        "management": mgmt,
        "ability": ability,
        "additional": add,
    })
    assert 0.0 <= comp <= 1.0

    # Prof-oriented score alone
    prof_score = function_score(prof)
    assert 0.0 <= prof_score <= 1.0

    ok = gating_ok(completion_pct=85, prof_oriented_score=0.9, no_red_criteria=True, recommend_promotion=True)
    assert ok is True

    not_ok = gating_ok(completion_pct=70, prof_oriented_score=0.9, no_red_criteria=True, recommend_promotion=True)
    assert not_ok is False
