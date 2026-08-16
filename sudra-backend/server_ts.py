import hashlib
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import numpy as np
import pandas as pd
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("ai_server")

BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", BASE_DIR / "artifacts"))
MODEL_PATH = ARTIFACT_DIR / "model_traced.pt"
CONFIG_PATH = ARTIFACT_DIR / "config.json"
MODEL_ARTIFACT = MODEL_PATH.name


with CONFIG_PATH.open() as config_file:
    cfg = json.load(config_file)

LABELS: List[str] = cfg["label_names"]
DEFAULT_THRESHOLD: float = float(cfg.get("threshold", 0.45))
LABEL_THRESHOLDS: Dict[str, float] = cfg.get("label_thresholds", {})
TAKES_MASK: bool = bool(cfg.get("takes_mask", True))

FEATURE_COLUMNS: List[str] = cfg.get("feature_columns", [])
if not FEATURE_COLUMNS:
    raise RuntimeError("artifacts/config.json must include feature_columns")

N_FEATURES = len(FEATURE_COLUMNS)
N_BUCKETS = int(cfg.get("n_buckets", 32))

PREPROCESS_STATS = cfg.get("preprocess_stats", {})
MEANS: Dict[str, float] = PREPROCESS_STATS.get("train_means", {}) or {}
STDS: Dict[str, float] = PREPROCESS_STATS.get("train_std", {}) or {}
if not MEANS or not STDS:
    logger.warning("preprocess_stats missing in config; using identity normalization")

# TorchScript is safe to serve directly and loads once when the app starts.
model = torch.jit.load(str(MODEL_PATH), map_location="cpu").eval()
logger.info(
    "model_loaded artifact=%s labels=%s features=%s takes_mask=%s",
    MODEL_ARTIFACT,
    len(LABELS),
    N_FEATURES,
    TAKES_MASK,
)


def cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class RawTrade(BaseModel):
    trade_id: str = Field(..., min_length=1)
    trader_id: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    side: Literal["long", "short"]
    timestamp_open: datetime
    timestamp_close: datetime
    entry_price: float = Field(..., gt=0)
    exit_price: float = Field(..., gt=0)
    qty: float = Field(..., gt=0)
    position_value: Optional[float] = Field(default=None, gt=0)


class TradesInput(BaseModel):
    trades: List[RawTrade]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_artifact: str
    n_labels: int
    n_features_expected: int


class PredictionItem(BaseModel):
    trade_id: str
    trader_id: str
    symbol: str
    timestamp_open: str
    timestamp_close: str
    probs: Dict[str, float]
    labels_above_threshold: List[str]


class PredictionResponse(BaseModel):
    threshold_default: float
    thresholds_per_label: Dict[str, float]
    n_traders: int
    n_trades: int
    feature_dim: int
    labels: List[str]
    preds: List[PredictionItem]


def add_trade_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp_open"] = pd.to_datetime(df["timestamp_open"])
    df["timestamp_close"] = pd.to_datetime(df["timestamp_close"])

    computed_position_value = df["entry_price"] * df["qty"]
    if "position_value" not in df.columns:
        df["position_value"] = computed_position_value
    else:
        df["position_value"] = df["position_value"].where(
            df["position_value"].notna(),
            computed_position_value,
        )
    df["position_value"] = df["position_value"].astype(np.float32)

    df["side"] = df["side"].astype(str).str.lower()
    df = df.sort_values(["trader_id", "timestamp_close"]).reset_index(drop=True)

    feature_defaults = {
        "holding_time_min": np.nan,
        "pnl_abs": np.nan,
        "pnl_pct": np.nan,
        "prev_pnl_pct": np.nan,
        "size_vs_prev": np.nan,
        "time_since_prev_close_min": np.nan,
        "streak_wins": 0,
        "streak_losses": 0,
        "cum_pnl_abs": np.nan,
        "cum_pnl_pct": np.nan,
        "avg_position_value_so_far": np.nan,
        "side_switch_prev": np.nan,
    }
    for column, default in feature_defaults.items():
        df[column] = default

    last_trade_by_trader: Dict[str, Dict[str, Any]] = {}

    for idx, row in df.iterrows():
        trader_id = row["trader_id"]
        position_value = row["position_value"]
        side = row["side"]
        sign = 1 if side == "long" else -1

        holding_minutes = (
            row["timestamp_close"] - row["timestamp_open"]
        ).total_seconds() / 60.0
        pnl_abs = (row["exit_price"] - row["entry_price"]) * row["qty"] * sign
        pnl_pct = (pnl_abs / position_value) * 100.0 if position_value else 0.0

        side_switch_prev = 0
        previous = last_trade_by_trader.get(trader_id)
        if previous:
            df.at[idx, "prev_pnl_pct"] = previous["pnl_pct"]
            df.at[idx, "size_vs_prev"] = (
                position_value / previous["position_value"]
                if previous["position_value"]
                else 1.0
            )
            df.at[idx, "time_since_prev_close_min"] = (
                row["timestamp_close"] - previous["timestamp_close"]
            ).total_seconds() / 60.0

            side_switch_prev = int(previous["side"] != side)
            if previous["pnl_pct"] > 0:
                streak_wins = previous["streak_wins"] + 1
                streak_losses = 0
            elif previous["pnl_pct"] < 0:
                streak_wins = 0
                streak_losses = previous["streak_losses"] + 1
            else:
                streak_wins = 0
                streak_losses = 0

            cum_pnl_abs = previous["cum_pnl_abs"] + pnl_abs
            cum_position_value = previous["cum_position_value"] + position_value
            n_trades = previous["n_trades"] + 1
            avg_position_value = (
                (previous["avg_position_value_so_far"] * previous["n_trades"])
                + position_value
            ) / n_trades
        else:
            streak_wins = 0
            streak_losses = 0
            cum_pnl_abs = pnl_abs
            cum_position_value = position_value
            n_trades = 1
            avg_position_value = position_value

        df.at[idx, "holding_time_min"] = holding_minutes
        df.at[idx, "pnl_abs"] = pnl_abs
        df.at[idx, "pnl_pct"] = pnl_pct
        df.at[idx, "streak_wins"] = streak_wins
        df.at[idx, "streak_losses"] = streak_losses
        df.at[idx, "side_switch_prev"] = side_switch_prev
        df.at[idx, "cum_pnl_abs"] = cum_pnl_abs
        df.at[idx, "cum_pnl_pct"] = (
            (cum_pnl_abs / cum_position_value) * 100.0 if cum_position_value else 0.0
        )
        df.at[idx, "avg_position_value_so_far"] = avg_position_value

        last_trade_by_trader[trader_id] = {
            "pnl_pct": pnl_pct,
            "timestamp_close": row["timestamp_close"],
            "position_value": position_value,
            "streak_wins": streak_wins,
            "streak_losses": streak_losses,
            "cum_pnl_abs": cum_pnl_abs,
            "cum_position_value": cum_position_value,
            "avg_position_value_so_far": avg_position_value,
            "n_trades": n_trades,
            "side": side,
        }

    float_cols = [
        "holding_time_min",
        "pnl_abs",
        "pnl_pct",
        "prev_pnl_pct",
        "size_vs_prev",
        "time_since_prev_close_min",
        "streak_wins",
        "streak_losses",
        "cum_pnl_abs",
        "cum_pnl_pct",
        "avg_position_value_so_far",
        "side_switch_prev",
    ]
    df[float_cols] = df[float_cols].astype(np.float32)

    is_win = df["pnl_abs"] > 0
    is_loss = df["pnl_abs"] < 0
    overall_hold_med = df.groupby("trader_id")["holding_time_min"].transform("median")
    overall_pnl_med = df.groupby("trader_id")["pnl_pct"].transform("median")

    df["med_hold_win"] = (
        df["holding_time_min"].where(is_win).groupby(df["trader_id"]).transform("median")
    )
    df["med_hold_loss"] = (
        df["holding_time_min"].where(is_loss).groupby(df["trader_id"]).transform("median")
    )
    df["med_pnl_win"] = (
        df["pnl_pct"].where(is_win).groupby(df["trader_id"]).transform("median")
    )
    df["med_pnl_loss"] = (
        df["pnl_pct"].where(is_loss).groupby(df["trader_id"]).transform("median")
    )

    df["med_hold_win"] = df["med_hold_win"].fillna(overall_hold_med).fillna(0.0)
    df["med_hold_loss"] = df["med_hold_loss"].fillna(overall_hold_med).fillna(0.0)
    df["med_pnl_win"] = df["med_pnl_win"].fillna(overall_pnl_med).fillna(0.0)
    df["med_pnl_loss"] = df["med_pnl_loss"].fillna(overall_pnl_med).fillna(0.0)

    df["trade_month"] = df["timestamp_close"].map(lambda ts: pd.Timestamp(ts).strftime("%Y-%m"))
    df["trades_per_month"] = (
        df.groupby(["trader_id", "trade_month"])["trade_id"].transform("count")
    )

    symbol_value_month = df.groupby(["trader_id", "trade_month", "symbol"])[
        "position_value"
    ].transform("sum")
    total_value_month = df.groupby(["trader_id", "trade_month"])[
        "position_value"
    ].transform("sum")
    df["symbol_share_month"] = (
        (symbol_value_month / total_value_month)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    df["max_symbol_share_month"] = df.groupby(["trader_id", "trade_month"])[
        "symbol_share_month"
    ].transform("max")

    df = df.drop(columns=["trade_month", "symbol_share_month"], errors="ignore")
    df["side"] = df["side"].map({"long": 1, "short": -1}).astype(np.float32)
    return df


def add_ticker_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def ticker_bucket(symbol: Any) -> int:
        normalized = "" if pd.isna(symbol) else str(symbol).upper()
        return int(hashlib.md5(normalized.encode()).hexdigest(), 16) % N_BUCKETS

    buckets = df["symbol"].map(ticker_bucket)
    for bucket_idx in range(N_BUCKETS):
        df[f"tickh_{bucket_idx}"] = (buckets == bucket_idx).astype(np.float32)

    df = df.sort_values(["trader_id", "timestamp_close"], kind="stable")
    previous_symbol = df.groupby("trader_id")["symbol"].shift(1)
    same_symbol = (
        df["symbol"].astype(str).str.upper()
        == previous_symbol.astype(str).str.upper()
    ).fillna(False)
    df["ticker_same_prev"] = same_symbol.astype(np.float32)
    return df


def standardize_features(df: pd.DataFrame) -> np.ndarray:
    features = df.copy()
    for column in FEATURE_COLUMNS:
        if column not in features.columns:
            features[column] = 0.0

    x = features[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    if MEANS and STDS:
        means = np.array([MEANS.get(column, 0.0) for column in FEATURE_COLUMNS], dtype=np.float32)
        stds = np.array([STDS.get(column, 1.0) for column in FEATURE_COLUMNS], dtype=np.float32)
        stds = np.where(stds == 0.0, 1.0, stds)
        x = (x - means) / stds

    return np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)


def collate_trader_sequences(sequences: List[np.ndarray]) -> tuple[torch.Tensor, torch.Tensor]:
    batch_size = len(sequences)
    feature_count = sequences[0].shape[1]
    max_length = max(sequence.shape[0] for sequence in sequences)

    padded = np.zeros((batch_size, max_length, feature_count), dtype=np.float32)
    pad_mask = np.zeros((batch_size, max_length), dtype=bool)

    for index, sequence in enumerate(sequences):
        sequence_length = sequence.shape[0]
        padded[index, :sequence_length, :] = sequence
        pad_mask[index, sequence_length:] = True

    return torch.from_numpy(padded), torch.from_numpy(pad_mask)


def build_attention_mask(pad_mask: torch.Tensor) -> torch.Tensor:
    sequence_length = pad_mask.shape[1]
    causal_mask = torch.triu(
        torch.ones(sequence_length, sequence_length, dtype=torch.bool),
        diagonal=1,
    )
    causal_mask = causal_mask.unsqueeze(0).unsqueeze(0)
    padding_mask = pad_mask[:, None, None, :]
    return causal_mask | padding_mask


def predict_dataframe(df: pd.DataFrame) -> PredictionResponse:
    df = add_trade_features(df)
    df = add_ticker_features(df)
    df = df.sort_values(["trader_id", "timestamp_close"], kind="stable")

    sequences: List[np.ndarray] = []
    row_groups: List[np.ndarray] = []
    for _, group in df.groupby("trader_id", sort=False):
        sequences.append(standardize_features(group))
        row_groups.append(group.index.to_numpy())

    x_tensor, pad_mask = collate_trader_sequences(sequences)

    with torch.inference_mode():
        if TAKES_MASK:
            logits = model(x_tensor, build_attention_mask(pad_mask))
        else:
            logits = model(x_tensor)

        if logits.ndim == 2:
            logits = logits.unsqueeze(1)
        probabilities = torch.sigmoid(logits).cpu().numpy()

    predictions: List[PredictionItem] = []
    for batch_index, row_ids in enumerate(row_groups):
        trader_probs = probabilities[batch_index, : len(row_ids), :]
        for trade_index, row_id in enumerate(row_ids):
            probs = {
                label: float(value)
                for label, value in zip(LABELS, trader_probs[trade_index, :])
            }
            labels_above_threshold = [
                label
                for label, value in probs.items()
                if value >= LABEL_THRESHOLDS.get(label, DEFAULT_THRESHOLD)
            ]

            predictions.append(
                PredictionItem(
                    trade_id=str(df.loc[row_id, "trade_id"]),
                    trader_id=str(df.loc[row_id, "trader_id"]),
                    symbol=str(df.loc[row_id, "symbol"]),
                    timestamp_open=pd.Timestamp(df.loc[row_id, "timestamp_open"]).isoformat(),
                    timestamp_close=pd.Timestamp(df.loc[row_id, "timestamp_close"]).isoformat(),
                    probs=probs,
                    labels_above_threshold=labels_above_threshold,
                )
            )

    return PredictionResponse(
        threshold_default=DEFAULT_THRESHOLD,
        thresholds_per_label=LABEL_THRESHOLDS,
        n_traders=len(row_groups),
        n_trades=len(predictions),
        feature_dim=N_FEATURES,
        labels=LABELS,
        preds=predictions,
    )


app = FastAPI(title="Bias Demo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    logger.info("health_check status=ok")
    return HealthResponse(
        status="ok",
        model_loaded=True,
        model_artifact=MODEL_ARTIFACT,
        n_labels=len(LABELS),
        n_features_expected=N_FEATURES,
    )


@app.post("/predict", response_model=PredictionResponse)
def predict_trades(payload: TradesInput) -> PredictionResponse:
    trade_count = len(payload.trades)
    if trade_count == 0:
        logger.warning("prediction_rejected reason=empty_trades")
        raise HTTPException(status_code=400, detail="trades must contain at least one trade")

    started = time.perf_counter()
    logger.info("prediction_started trades=%s", trade_count)

    try:
        df = pd.DataFrame([trade.model_dump() for trade in payload.trades])
        response = predict_dataframe(df)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("prediction_failed trades=%s", trade_count)
        raise HTTPException(status_code=500, detail="prediction failed") from exc

    latency_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "prediction_completed trades=%s traders=%s latency_ms=%.2f",
        response.n_trades,
        response.n_traders,
        latency_ms,
    )
    return response
