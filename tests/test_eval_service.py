from app.core.services.evaluation_service import normalize_weights, normalize_value

def test_normalize_weights_auto_and_manual():
    pairs = [(1, 0.5), (2, None), (3, None)]
    auto_ids = [2, 3]
    out = normalize_weights(pairs, auto_ids)
    assert round(out[1], 3) == 0.5
    assert round(out[2], 3) == round(out[3], 3) == 0.25
    assert round(sum(out.values()), 6) == 1.0

def test_normalize_value_defaults():
    assert normalize_value(None, "binary", 1) == 1.0
    assert normalize_value(None, "one_to_five", 3.0) == 0.5
    assert normalize_value(None, "percent", 50.0) == 0.5
