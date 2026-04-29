import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import yfinance as yf

################################################################################

# ---- Yahoo Finance price helpers (U.S. stocks, New York time) ----

YAHOO_TICKER_MAP = {
    # Tech
    "AAPL": "AAPL", "MSFT": "MSFT", "GOOG": "GOOG", "AMZN": "AMZN", "TSLA": "TSLA",
    "NVDA": "NVDA", "META": "META", "ORCL": "ORCL", "ADBE": "ADBE", "INTC": "INTC",
    "CSCO": "CSCO", "IBM": "IBM", "CRM": "CRM", "QCOM": "QCOM",

    # Financials
    "JPM": "JPM", "BAC": "BAC", "C": "C", "GS": "GS", "MS": "MS",
    "WFC": "WFC", "AXP": "AXP", "SCHW": "SCHW", "BLK": "BLK", "PYPL": "PYPL",

    # Healthcare
    "JNJ": "JNJ", "PFE": "PFE", "MRK": "MRK", "UNH": "UNH", "ABBV": "ABBV",
    "LLY": "LLY", "BMY": "BMY", "TMO": "TMO",

    # Industrials / Energy
    "GE": "GE", "CAT": "CAT", "BA": "BA", "XOM": "XOM", "CVX": "CVX",
    "COP": "COP", "SLB": "SLB", "DE": "DE",

    # Consumer / Retail
    "NFLX": "NFLX", "DIS": "DIS", "NKE": "NKE", "SBUX": "SBUX", "MCD": "MCD",
    "PG": "PG", "KO": "KO", "PEP": "PEP", "WMT": "WMT", "COST": "COST"
}

# ---- Global in-memory price cache ----
PRICE_CACHE = {}  # { "AAPL": DataFrame indexed in America/New_York with a "Close" column }

def build_price_cache(symbols, period="60d", interval="5m"):
    """
    Pre-download price history once per symbol, store in PRICE_CACHE.
    The index is converted to America/New_York for fast local lookups.
    """
    for sym in symbols:
        ysym = YAHOO_TICKER_MAP.get(sym, sym)
        try:
            df = yf.download(ysym, period=period, interval=interval, auto_adjust=False, progress=False)
            if df is None or df.empty:
                continue
            # Ensure tz-aware NY index
            df = _tz_convert_index_to_ny(df)
            PRICE_CACHE[sym] = df
        except Exception:
            # Skip on errors; fall back to live calls later
            pass

def _lookup_cached_close(symbol, when_ts):
    """
    Return the last cached Close at or before when_ts (both NY tz), or None if unavailable.
    """
    df = PRICE_CACHE.get(symbol)
    if df is None or df.empty:
        return None
    # df is already NY tz; ensure when_ts is NY tz as well
    when_ts = _ensure_tz(when_ts, tz="America/New_York")
    df_cut = df[df.index <= when_ts]
    if df_cut.empty:
        return None
    val = df_cut["Close"].iloc[-1]
    try:
        return float(val)
    except Exception:
        return None

def _ensure_tz(ts, tz="America/New_York"):
    ts = pd.Timestamp(ts)
    if ts.tzinfo is None:
        ts = ts.tz_localize(tz)
    else:
        ts = ts.tz_convert(tz)
    return ts

def _tz_convert_index_to_ny(df):
    """Ensure price index is timezone-aware in America/New_York."""
    if df is None or df.empty:
        return df
    idx = df.index
    # yfinance intraday often returns UTC tz-aware; daily can be naive
    if idx.tz is None:
        # assume UTC for safety, then convert to NY
        idx = idx.tz_localize("UTC")
    df.index = idx.tz_convert("America/New_York")
    return df

def _nearest_close_at_or_before(df_px, when_ts):
    """Find the last available Close at or before when_ts (both in NY tz)."""
    if df_px is None or df_px.empty:
        return None
    df_px = _tz_convert_index_to_ny(df_px)
    if df_px is None or df_px.empty:
        return None

    df_cut = df_px[df_px.index <= when_ts]
    if df_cut.empty:
        return None

    # Be robust to possible MultiIndex/1-col DataFrame returns
    if "Close" in df_cut.columns:
        close_series_or_df = df_cut["Close"]
    else:
        # fallback if column name casing differs
        close_cols = [c for c in df_cut.columns if str(c).lower() == "close"]
        if not close_cols:
            return None
        close_series_or_df = df_cut[close_cols[0]]

    # Get the last row’s close as a scalar
    val = close_series_or_df.iloc[-1]
    if isinstance(val, (pd.Series, pd.DataFrame, np.ndarray)):
        val = np.squeeze(val)

    try:
        return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
    except Exception:
        return None

def get_price_at_yahoo(symbol, when, tz="America/New_York"):
    """
    Fetch the price at/just before 'when' using cache first; if missing, hit Yahoo.
    """
    ysym = YAHOO_TICKER_MAP.get(symbol, symbol)
    when_ts = _ensure_tz(when, tz)

    # 1) Try local cache first
    cached_px = _lookup_cached_close(symbol, when_ts)
    if cached_px is not None:
        return cached_px

    tries = []
    if age_days <= 7:
        tries.append(("7d",  "1m"))
    if age_days <= 60:
        tries.append(("60d", "5m"))
    if age_days <= 730:
        tries.append(("730d", "1h"))
    tries.append(("10y", "1d"))

    for period, interval in tries:
        try:
            df = yf.download(ysym, period=period, interval=interval, auto_adjust=False, progress=False)
            px = _nearest_close_at_or_before(df, when_ts)
            if px is not None:
                return px
        except Exception:
            pass

    return None

def get_entry_exit_prices(symbol, open_time, close_time, tz="America/New_York"):
    entry = get_price_at_yahoo(symbol, open_time, tz=tz)
    exit_ = get_price_at_yahoo(symbol, close_time, tz=tz)
    return entry, exit_


################################################################################



def generate_fake_trade_logs(num_traders=2000, trades_per_trader=50):
    rows = []
    symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NVDA", "META", "JPM", "BAC", "NFLX"]
    sides = ["long", "short"]
    month_start = datetime(2025, 7, 1, 9, 0)
    month_end = datetime(2025, 7, 31, 23, 59, 59)
        # Build cache once for these symbols (covers the whole month at 5m resolution)
    build_price_cache(symbols, period="60d", interval="5m")

    for trader_id in range(num_traders):
        for t in range(trades_per_trader):
            trade_id = f"{trader_id}_{t}"

            symbol = random.choice(symbols)
            side = random.choices(["long", "short"], weights=[0.65, 0.35])[0]

            open_time = month_start + timedelta(
                seconds=random.randint(0, int((month_end - month_start).total_seconds()))
            )

            max_holding = (month_end - open_time).total_seconds()
            holding = random.randint(1, int(max_holding))
            close_time = open_time + timedelta(seconds=holding)

            # Fetch entry/exit from Yahoo (New York time). If missing, fall back to a nearby daily price.
            entry_price, exit_price = get_entry_exit_prices(symbol, open_time, close_time, tz="America/New_York")

            # Fallbacks (keep your generator robust if Yahoo has gaps)
            if entry_price is None:
                # use close price of open day as rough proxy
                entry_price = get_price_at_yahoo(symbol, open_time.replace(hour=16, minute=0, second=0), tz="America/New_York")
            if exit_price is None:
                exit_price = get_price_at_yahoo(symbol, close_time.replace(hour=16, minute=0, second=0), tz="America/New_York")

            # If still None (e.g., symbol holiday), last resort: random but bounded
            if entry_price is None:
                entry_price = float(np.random.uniform(5, 500))  # conservative fallback
            if exit_price is None:
                exit_price = float(np.random.uniform(5, 500))

            position_value_target = np.random.uniform(1_000, 20_000)   # realistic $ exposure
            qty = max(1, int(position_value_target / entry_price))     # shares = dollars / price

            rows.append({
                "trade_id": trade_id,
                "trader_id": f"T{trader_id}",
                "symbol": symbol,
                "side": side,
                "timestamp_open": open_time,
                "timestamp_close": close_time,
                "entry_price": entry_price,
                "exit_price": round(exit_price, 2),
                "qty": qty
            })


    df = pd.DataFrame(rows)
    df["position_value"] = df["entry_price"] * df["qty"]

    # 1) Sort rows by close time (and then trader to keep ties tidy)
    df = df.sort_values(["timestamp_close", "trader_id"]).reset_index(drop=True)

    # 2) Reassign trade_id to be sequential per trader in this sorted order
    df["trade_id"] = df.groupby("trader_id").cumcount().astype(str)
    df["trade_id"] = df["trader_id"].str.replace("T", "") + "_" + df["trade_id"]

    for col in ["entry_price", "exit_price", "qty", "position_value"]:
      df[col] = df[col].astype(np.float32)



    return df

fake_df = generate_fake_trade_logs()


#####################################

import numpy as np
import pandas as pd

# Expanded data sample – every row still represents a single completed trade,
# but now we capture ~40 columns that feed behavioural-bias analytics.

def add_features_simple(df):

    df = df.copy()

    df["timestamp_open"] = pd.to_datetime(df["timestamp_open"])
    df["timestamp_close"] = pd.to_datetime(df["timestamp_close"])

    df["side"] = df["side"].astype(str).str.lower()

    df = df.sort_values(["trader_id", "timestamp_close"]).reset_index(drop=True)

    df["holding_time_min"] = np.nan
    df["pnl_abs"]          = np.nan
    df["pnl_pct"]          = np.nan
    df["prev_pnl_pct"]     = np.nan
    df["size_vs_prev"]     = np.nan
    df["time_since_prev_close_min"] = np.nan
    df["streak_wins"]      = 0
    df["streak_losses"]    = 0
    df["cum_pnl_abs"]      = np.nan   # running sum of pnl_abs per trader
    df["cum_pnl_pct"]      = np.nan   # running % pnl over cumulative capital per trader
    df["avg_position_value_so_far"] = np.nan
    df["side_switch_prev"] = np.nan

    last_info = {}

    for idx, row in df.iterrows():

        tid = row["trader_id"]

        time_open  = row["timestamp_open"]      #holding time
        time_close = row["timestamp_close"]
        holding_sec = (time_close - time_open).total_seconds()
        holding_minutes = holding_sec / 60
        df.at[idx, "holding_time_min"] = holding_minutes

        side = row["side"].lower()      # pnl absolute
        sign = 1 if side == "long" else -1
        pnl_abs = (row["exit_price"] - row["entry_price"]) * row["qty"] * sign
        df.at[idx, "pnl_abs"] = pnl_abs

        position_val = row["position_value"]        #pnl percentage
        df.at[idx, "pnl_pct"] = ( pnl_abs / position_val ) * 100
        side_switch_prev = 0
        if tid in last_info:
            prev = last_info[tid]

            df.at[idx, "prev_pnl_pct"] = prev["pnl_pct"]
            df.at[idx, "size_vs_prev"] = position_val / prev["position_value"]
            time_gap_sec = (row["timestamp_close"] - prev["timestamp_close"]).total_seconds()
            df.at[idx, "time_since_prev_close_min"] = time_gap_sec / 60

            if prev.get("side") in ("long", "short") and side in ("long", "short"):
              side_switch_prev = int(
                  (prev["side"] == "long" and side == "short") or
                   (prev["side"] == "short" and side == "long")
                   )

            if prev["pnl_pct"] > 0:
                win_streak = prev["streak_wins"] + 1
                loss_streak = 0
            elif prev["pnl_pct"] < 0:
                win_streak = 0
                loss_streak = prev["streak_losses"] + 1
            else:
                win_streak = loss_streak = 0

            cum_pnl_abs = prev["cum_pnl_abs"] + pnl_abs
            cum_position_value = prev["cum_position_value"] + position_val
            n_trades = prev["n_trades"] + 1
            avg_position_value = ((prev["avg_position_value_so_far"] * prev["n_trades"]) + position_val) / n_trades
        else:
            win_streak = loss_streak = 0

            cum_pnl_abs = pnl_abs
            cum_position_value = position_val
            n_trades = 1
            avg_position_value = position_val

        df.at[idx, "streak_wins"] = win_streak
        df.at[idx, "streak_losses"] = loss_streak
        df.at[idx, "side_switch_prev"] = side_switch_prev
        df.at[idx, "cum_pnl_abs"] = cum_pnl_abs
        df.at[idx, "cum_pnl_pct"] = (cum_pnl_abs / cum_position_value) * 100 if cum_position_value != 0 else 0.0

        df.at[idx, "avg_position_value_so_far"] = avg_position_value

        last_info[tid] = {
            "pnl_pct": df.at[idx, "pnl_pct"],
            "timestamp_close": row["timestamp_close"],
            "position_value": position_val,
            "streak_wins": win_streak,
            "streak_losses": loss_streak,
            "cum_pnl_abs": cum_pnl_abs,
            "cum_position_value": cum_position_value,
            "avg_position_value_so_far": avg_position_value,
            "n_trades": n_trades,
            "side": side
        }

        float_cols = [
            "holding_time_min", "pnl_abs", "pnl_pct", "prev_pnl_pct", "size_vs_prev",
            "time_since_prev_close_min", "streak_wins", "streak_losses", "cum_pnl_abs", "cum_pnl_pct",
            "avg_position_value_so_far", "side_switch_prev"
        ]
        df[float_cols] = df[float_cols].astype(np.float32)
    return df

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

result_df = add_features_simple(fake_df)


#######################

import numpy as np
import pandas as pd

def make_bias_labels_strict(df, ensure_nonzero=True, **kw_thresholds):
    """
    Weak labels for trading biases using only the provided columns.
    Works with 1 or many traders (batch). Returns a copy of df with bias_* columns.
    Thresholds can be overridden via kwargs (see THRESHOLDS keys below).
    """
    out = df.copy()

    # ---- Ensure types & ordering ----
    out["timestamp_open"]  = pd.to_datetime(out["timestamp_open"])
    out["timestamp_close"] = pd.to_datetime(out["timestamp_close"])
    out = out.sort_values(["trader_id", "timestamp_close"]).reset_index(drop=True)

    # ---- Defaults (tunable) ----
    THRESHOLDS = {
    # Overconfidence (frequent but not “every trade”)
    "OVERCONF_SIZE_AFTER_WIN": 1.40,          # was 1.50
    "OVERCONF_QUICK_REENTRY_PCTL": 0.25,      # new: trader's own 25th pct wait
    "OVERCONF_MIN_WAIT_MIN": 120.0,           # new: and < 2h absolute floor
    "OVERCONF_REQUIRE_PREV_WIN": True,        # new: reentry is only risky after a win

    # Recency (keep as you have; medians already added)
    "RECENCY_WAIT_MULT": 2.0,
    "RECENCY_SIZE_MULT": 1.30,

    # Disposition (very common; use medians and per-trade flags)
    "DISP_HOLD_MULT": 1.40,                   # was 1.50 (slightly easier to trigger)
    "DISP_LOSS_MAG_MULT": 1.80,               # was 2.0 (slightly easier)

    # Loss aversion (common; remove “mark all trades”)
    "LOSS_AVG_RATIO": 1.80,                   # was 2.0
    "LOSS_MAX_RATIO": 1.80,                   # was 2.0
    "LOSS_SIZE_UP_AFTER_LOSS": 1.20,

    # Anchoring (moderate; avoid flagging every near-BE)
    "ANCHOR_NEAR_BE_PCT": 1.0,
    "ANCHOR_FRAC_NEAR_BE": 0.25,              # was 0.30 (harder at account level)
    "ANCHOR_BIG_LOSS_PCT": -10.0,
    "ANCHOR_HOLD_PCTL": 0.65,                 # new: near-BE + long hold

    # Sunk cost (rare; slightly easier to catch, but still specific)
    "SUNK_SIZE_AFTER_LOSS": 1.30,             # was 1.50
    "SUNK_SAME_SYMBOL_FAST_MIN": 1440.0,       # was 1440 (12h window)

    # Gambler’s fallacy (rare)
    "GF_STREAK_LOSSES": 3,
    "GF_SIZE_INCREASE": 1.50,
    "GF_QUICK_REENTRY_MIN": 60.0,

    # Hot hand (occasional)
    "HOT_STREAK_WINS": 3,
    "HOT_SIZE_INCREASE": 1.50,
    "HOT_QUICK_REENTRY_MIN": 60.0,

    # House money (should fire only at *new* equity highs)
    "HOUSE_SIZE_INCREASE_AT_NEW_HIGH": 1.30,

    # Endowment (avoid blanketing frequent symbols)
    "ENDOW_TOP_SYMBOL_RATIO": 0.60,           # was 0.50 (recognize focus),
    "ENDOW_QUICK_REENTRY_DAYS": 5,
    "ENDOW_MIN_QUICK_REENTRIES": 4
    }
    THRESHOLDS.update(kw_thresholds)

    # ---- Helpers ----
    out["is_win"]  = (out["pnl_abs"] > 0).astype(int)
    out["is_loss"] = (out["pnl_abs"] < 0).astype(int)

    g = out.groupby("trader_id", group_keys=False)
    out["prev_symbol"]    = g["symbol"].shift(1)
    out["prev_side"]      = g["side"].shift(1)
    out["prev_pos_value"] = g["position_value"].shift(1)

    # Robust size change (fallback if size_vs_prev missing/NaN)
    size_change = out["position_value"] / out["prev_pos_value"]
    size_change = pd.to_numeric(size_change, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(1.0)
    out["size_change"] = out["size_vs_prev"].where(out["size_vs_prev"].notna(), size_change)

    # Ensure numeric
    for col in ["pnl_pct","prev_pnl_pct","time_since_prev_close_min","holding_time_min","cum_pnl_abs"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Per-trader cumulative PnL if missing
    if "cum_pnl_abs" not in out.columns or out["cum_pnl_abs"].isna().all():
        out["cum_pnl_abs"] = out.groupby("trader_id")["pnl_abs"].cumsum()

    # Convenience
    same_symbol_side = (out["symbol"] == out["prev_symbol"]) & (out["side"] == out["prev_side"])

    # ========= 1) Overconfidence (trade-level) =========
    out["bias_overconfidence"] = 0
    for tid, grp in out.groupby("trader_id"):
        idx = grp.index
        q = grp["time_since_prev_close_min"].dropna()
        if len(q) == 0:
            continue

        # quick = faster than trader's own 25th pct, but never count waits > 120m as "quick"
        p25_wait = q.quantile(THRESHOLDS["OVERCONF_QUICK_REENTRY_PCTL"])
        if pd.isna(p25_wait):
            p25_wait = THRESHOLDS["OVERCONF_MIN_WAIT_MIN"]
        p25_wait = min(p25_wait, THRESHOLDS["OVERCONF_MIN_WAIT_MIN"])

        if THRESHOLDS["OVERCONF_REQUIRE_PREV_WIN"]:
            after_win = (grp["prev_pnl_pct"] > 0)
        else:
            after_win = grp["prev_pnl_pct"].notna()

        size_jump     = after_win & (grp["size_change"] > THRESHOLDS["OVERCONF_SIZE_AFTER_WIN"])
        quick_reentry = after_win & (grp["time_since_prev_close_min"] <= p25_wait)

        out.loc[idx[size_jump | quick_reentry], "bias_overconfidence"] = 1

    # ========= 2) Confirmation Bias (first retry only) =========
    out["bias_confirmation"] = 0
    for tid, grp in out.groupby("trader_id"):
        idx = grp.index
        prev_loss = grp["prev_pnl_pct"] < 0
        same_symbol_side = (grp["symbol"] == grp["prev_symbol"]) & (grp["side"] == grp["prev_side"])

        # Confirmation = first retry: trade after a loss on the same symbol/side
        first_retry = prev_loss & same_symbol_side

        # But exclude cases where it's the 2nd, 3rd, etc. retry
        # Only flag if the *previous* trade wasn't already a retry
        prev_retry = first_retry.shift(1, fill_value=False)
        just_first_retry = first_retry & ~prev_retry

        out.loc[idx[just_first_retry], "bias_confirmation"] = 1

    # ========= 3) Recency Bias (per-trade local checks) =========
    out["bias_recency"] = 0

    for tid, grp in out.groupby("trader_id"):
        idx = grp.index
        after_win  = grp["prev_pnl_pct"] > 0
        after_loss = grp["prev_pnl_pct"] < 0

        # Medians create robust "typical" baselines (less noisy than means)
        median_wait_win   = grp.loc[after_win,  "time_since_prev_close_min"].median()
        median_size_loss  = grp.loc[after_loss, "size_change"].median()

        # Flag ONLY trades that exceed per-trade thresholds relative to the opposite baseline
        # Wait effect: THIS trade occurs after a loss AND waits > 2x the typical wait after wins
        long_after_loss = after_loss & (grp["time_since_prev_close_min"] >
                                        THRESHOLDS["RECENCY_WAIT_MULT"] * max(1e-9, median_wait_win))

        # Size effect: THIS trade occurs after a win AND size > 1.3x the typical size after losses
        sizeup_after_win = after_win & (grp["size_change"] >
                                        THRESHOLDS["RECENCY_SIZE_MULT"] * max(1e-9, median_size_loss))

        out.loc[idx[long_after_loss | sizeup_after_win], "bias_recency"] = 1

    out["bias_recency"] = out["bias_recency"].astype(int)

    # ========= 4) Disposition Effect =========
    out["bias_disposition"] = 0
    for tid, grp in out.groupby("trader_id"):
        winners = grp[grp["pnl_abs"] > 0]
        losers  = grp[grp["pnl_abs"] < 0]
        if len(winners) == 0 or len(losers) == 0:
            continue

        med_hold_win  = winners["holding_time_min"].median()
        med_hold_loss = losers["holding_time_min"].median()
        med_pnl_win   = winners["pnl_pct"].median()
        med_pnl_loss  = losers["pnl_pct"].median()

        # Flag losers that are held "too long" vs winner baseline
        too_long_loss = (grp["pnl_abs"] < 0) & (grp["holding_time_min"] >
                        THRESHOLDS["DISP_HOLD_MULT"] * max(1e-9, med_hold_win))

        # Flag accounts where average loss severity >> average gain;
        # then mark only the outlier losers (not every trade)
        loss_mag_condition = (abs(med_pnl_loss) > THRESHOLDS["DISP_LOSS_MAG_MULT"] * max(1e-9, abs(med_pnl_win)))
        if loss_mag_condition:
            severe_loss = (grp["pnl_pct"] < 0) & (abs(grp["pnl_pct"]) >
                          THRESHOLDS["DISP_LOSS_MAG_MULT"] * max(1e-9, abs(med_pnl_win)))
        else:
            severe_loss = pd.Series(False, index=grp.index)

        out.loc[grp.index[too_long_loss | severe_loss], "bias_disposition"] = 1

    # ========= 5) Loss Aversion (per-trade) =========
    out["bias_loss_aversion"] = 0
    for tid, grp in out.groupby("trader_id"):
        winners = grp[grp["pnl_abs"] > 0]
        if len(winners) == 0:
            continue
        med_gain = winners["pnl_pct"].median()
        max_gain = winners["pnl_pct"].max()

        # Trade-level magnitude check: loss bigger than 1.8x typical gain or 1.8x max gain marker
        big_vs_avg = (grp["pnl_pct"] < 0) & (abs(grp["pnl_pct"]) > THRESHOLDS["LOSS_AVG_RATIO"] * max(1e-9, abs(med_gain)))
        big_vs_max = (grp["pnl_pct"] < 0) & (abs(grp["pnl_pct"]) > THRESHOLDS["LOSS_MAX_RATIO"] * max(1e-9, abs(max_gain)))

        # Size up right after a loss (classic get-even tell)
        size_up_after_loss = (grp["prev_pnl_pct"] < 0) & (grp["size_change"] > THRESHOLDS["LOSS_SIZE_UP_AFTER_LOSS"])

        out.loc[grp.index[big_vs_avg | big_vs_max | size_up_after_loss], "bias_loss_aversion"] = 1

    # ========= 6) Anchoring (trade-level + mild account pattern) =========
    out["bias_anchoring"] = 0
    for tid, grp in out.groupby("trader_id"):
        if len(grp) == 0:
            continue
        near_be = grp["pnl_pct"].between(-THRESHOLDS["ANCHOR_NEAR_BE_PCT"], THRESHOLDS["ANCHOR_NEAR_BE_PCT"])

        # Long hold baseline
        hold_q75 = grp["holding_time_min"].quantile(THRESHOLDS["ANCHOR_HOLD_PCTL"]) if grp["holding_time_min"].notna().any() else np.nan
        long_hold_near_be = near_be & (grp["holding_time_min"] > hold_q75)

        # Account-level "anchoring prone" pattern — stricter than before
        frac_near_be = float(near_be.mean())
        small_losses = grp[(grp["pnl_pct"] < 0) & (grp["pnl_pct"] > THRESHOLDS["ANCHOR_BIG_LOSS_PCT"])]
        big_losses   = grp[grp["pnl_pct"] <= THRESHOLDS["ANCHOR_BIG_LOSS_PCT"]]
        prone = (frac_near_be > THRESHOLDS["ANCHOR_FRAC_NEAR_BE"]) and (len(big_losses) <= len(small_losses))

        if prone:
            out.loc[grp.index[long_hold_near_be], "bias_anchoring"] = 1
        else:
            # Only mark the clearly anchored executions (near-BE + long hold)
            out.loc[grp.index[long_hold_near_be], "bias_anchoring"] = 1

    # ========= 7) Sunk Cost =========
    same_symbol = (out["symbol"] == out["prev_symbol"])
    sunk_fast   = out["time_since_prev_close_min"] <= THRESHOLDS["SUNK_SAME_SYMBOL_FAST_MIN"]
    sunk_size   = out["size_change"] > THRESHOLDS["SUNK_SIZE_AFTER_LOSS"]
    sunk_rule   = (out["prev_pnl_pct"] < 0) & same_symbol & sunk_fast & sunk_size
    out["bias_sunk_cost"] = sunk_rule.astype(int)

    # ========= 8) Gambler’s Fallacy =========
    gf_cond = (
        (out["streak_losses"] >= THRESHOLDS["GF_STREAK_LOSSES"]) &
        (
            (out["size_change"] > THRESHOLDS["GF_SIZE_INCREASE"]) |
            (out["time_since_prev_close_min"] < THRESHOLDS["GF_QUICK_REENTRY_MIN"])
        )
    )
    out["bias_gamblers_fallacy"] = gf_cond.astype(int)

    # ========= 9) Hot-Hand Bias =========
    hot_cond = (
        (out["streak_wins"] >= THRESHOLDS["HOT_STREAK_WINS"]) &
        (
            (out["size_change"] > THRESHOLDS["HOT_SIZE_INCREASE"]) |
            (out["time_since_prev_close_min"] < THRESHOLDS["HOT_QUICK_REENTRY_MIN"])
        )
    )
    out["bias_hot_hand"] = hot_cond.astype(int)

    # ========= 10) House-Money Effect =========
    out["cum_pnl_high_water"] = out.groupby("trader_id")["cum_pnl_abs"].cummax()
    prev_high = out.groupby("trader_id")["cum_pnl_high_water"].shift(1)
    new_high_event = out["cum_pnl_abs"] > prev_high.fillna(-np.inf)  # strictly greater
    house_jump  = out["size_change"] > THRESHOLDS["HOUSE_SIZE_INCREASE_AT_NEW_HIGH"]
    out["bias_house_money"] = (new_high_event & house_jump).astype(int)

    # ========= 11) Endowment Effect (focused, event-based) =========
    counts = out.groupby(["trader_id", "symbol"])["trade_id"].transform("count")
    totals = out.groupby("trader_id")["trade_id"].transform("count")
    share  = counts / totals.replace(0, np.nan)
    heavy_symbols = share >= THRESHOLDS["ENDOW_TOP_SYMBOL_RATIO"]

    reentry_window = pd.Timedelta(days=THRESHOLDS["ENDOW_QUICK_REENTRY_DAYS"])
    quick_reentries = np.zeros(len(out), dtype=int)
    last_close = {}

    for i, row in out.iterrows():
        key = (row["trader_id"], row["symbol"])
        prev_close = last_close.get(key, pd.NaT)
        if pd.notna(prev_close) and (row["timestamp_open"] - prev_close) <= reentry_window:
            quick_reentries[i] = 1
        last_close[key] = row["timestamp_close"]

    out["bias_endowment"] = 0
    quick_series = pd.Series(quick_reentries, index=out.index)

    for tid, grp in out.groupby("trader_id"):
        idx = grp.index
        # Count quick re-entries by symbol
        by_sym_quick = quick_series.loc[idx].groupby(grp["symbol"]).sum()
        # Symbols that show BOTH heavy use and >= threshold quick re-entries
        attached_syms = set(by_sym_quick[by_sym_quick >= THRESHOLDS["ENDOW_MIN_QUICK_REENTRIES"]].index)

        # Flag only the trades that are either (a) quick re-entries in attached symbols,
        # or (b) trades on heavy symbols AFTER the attachment threshold is reached.
        is_quick_in_attached = quick_series.loc[idx].astype(bool) & grp["symbol"].isin(attached_syms)
        is_heavy_after_attach = grp["symbol"].isin(attached_syms) & heavy_symbols.loc[idx]

        out.loc[idx[is_quick_in_attached | is_heavy_after_attach], "bias_endowment"] = 1

    return out


def summarize_bias_counts(biased_df):
    """
    Build per-trader bias count and rate tables + overall totals.
    Returns:
      per_trader_counts (DataFrame),
      per_trader_rates  (DataFrame),
      overall_counts    (Series),
      overall_rates     (Series)
    """
    bias_cols = [c for c in biased_df.columns if c.startswith("bias_")]
    # Per-trader counts
    per_trader_counts = (
        biased_df
        .groupby("trader_id")[bias_cols]
        .sum()
        .astype(int)
        .sort_index()
    )
    # Per-trader rates (counts / number of trades for that trader)
    trades_per_trader = biased_df.groupby("trader_id").size().rename("n_trades")
    per_trader_rates = (per_trader_counts
                        .div(trades_per_trader, axis=0)
                        .sort_index())

    # Overall totals / rates
    overall_counts = biased_df[bias_cols].sum().astype(int).sort_values(ascending=False)
    overall_rates  = (overall_counts / len(biased_df)).sort_values(ascending=False)

    return per_trader_counts, per_trader_rates, overall_counts, overall_rates


# ---- Example usage (batch-safe) ----
biased_df = make_bias_labels_strict(result_df)  # result_df can contain many traders
bias_cols = [c for c in biased_df.columns if c.startswith("bias_")]
pd.set_option("display.max_rows", None)     # show all rows
pd.set_option("display.max_columns", None)  # show all columns

per_trader_counts, per_trader_rates, overall_counts, overall_rates = summarize_bias_counts(biased_df)

print("\nPer-trader bias counts:")
print(per_trader_counts)

print("\nPer-trader bias rates:")
print(per_trader_rates)

print("\nOverall bias counts (all traders):")
print(overall_counts)

print("\nOverall bias rates (all traders):")
print(overall_rates)

# (Optional) Save artifacts
per_trader_counts.to_csv("bias_counts_per_trader.csv")
per_trader_rates.to_csv("bias_rates_per_trader.csv")
overall_counts.to_csv("bias_counts_overall.csv")
overall_rates.to_csv("bias_rates_overall.csv")

############################

# ---- Merge pre-computed features with heuristic labels ----

# Run heuristics function on result_df
biased_df = make_bias_labels_strict(result_df)

# Identify bias columns only (avoid duplication)
bias_cols = [c for c in biased_df.columns if c.startswith("bias_")]

# Merge both: keep all feature columns + add bias flags
merged_df = pd.concat([result_df.reset_index(drop=True), biased_df[bias_cols].reset_index(drop=True)], axis=1)

# Replace side column: long=1, short=-1
merged_df["side"] = merged_df["side"].map({"long": 1, "short": -1}).astype(np.float32)

# Drop unwanted columns
merged_df = merged_df.drop(columns=["cum_pnl_abs", "timestamp_open", "timestamp_close"], errors="ignore")

# Show full merged table (all rows/cols)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
print(merged_df)


# Optional: save merged dataset
merged_df.to_csv("merged_trades_with_biases.csv", index=False)

df = merged_df
