"""The editable file for a trading autoresearch loop. Contract (see evaluate.py):
    PARAMS                         tunable values
    fit(train) -> state            optional; learn from TRAINING bars only
    positions(bars, state)         one position in [-1, 1] per bar; position i may use only bars[0..i]
Each bar is {"date": "YYYY-MM-DD", "open": float, "close": float}.
"""

PARAMS = {"lookback": 20}


def fit(train):
    return None  # nothing learned in this baseline


def positions(bars, state):
    # Baseline: time-series momentum - long if the close is above its N-day average, short if below.
    n = PARAMS["lookback"]
    closes = [b["close"] for b in bars]
    out, running = [], 0.0
    for i, c in enumerate(closes):
        running += c
        if i >= n:
            running -= closes[i - n]
        if i < n - 1:
            out.append(0.0)
        else:
            out.append(1.0 if c > running / n else -1.0)
    return out
