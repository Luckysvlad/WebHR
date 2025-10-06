from app.services.weights import normalize_weights

def test_normalize_weights_even():
    pairs=[(1,0.0),(2,0.0),(3,0.0)]; out=normalize_weights(pairs); assert all(abs(w-1/3)<1e-9 for _,w in out)

def test_normalize_weights_sum1():
    pairs=[(1,1.0),(2,2.0)]; out=normalize_weights(pairs); assert abs(sum(w for _,w in out)-1.0)<1e-9
