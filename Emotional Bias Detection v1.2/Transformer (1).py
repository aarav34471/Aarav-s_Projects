import torch
import torch.nn as nn
from tqdm import tqdm
import math
import numpy as np
from collections import defaultdict
from sklearn.metrics import precision_recall_fscore_support

class TradeEmbedding(nn.Module):
    def __init__(self, input_dim=49, embedding_dim=64, max_len=500):
        super().__init__()
        self.embedding_dim = embedding_dim
        # First Linear layer makes 16D Vector to 64D
        self.linear = nn.Linear(input_dim, embedding_dim)
        # Saving the positional vector

        self.register_buffer("positional_encoding", self._generate_positional_encoding(max_len, embedding_dim))


    def _generate_positional_encoding(self, seq_len, dim):
        pe = torch.zeros(seq_len, dim, dtype = torch.float32)
        position = torch.arange(0, seq_len, dtype = torch.float32).unsqueeze(1)
        base = torch.tensor(10000.0, dtype=torch.float32)
        div_term = torch.exp(torch.arange(0, dim, 2, dtype = torch.float32).float() *
                             (-torch.log(base) / dim))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)  # [1, seq_len, emb_dim]

    def forward(self, x):
        # x shape: [batch_size, sequence_length, input_dim]
        B, L, _ = x.shape                                                           # WHY: get sequence length L for slicing/guard

        # (ADD) guard against sequences longer than precomputed PE
        # WHY: Fail fast with a clear error instead of silent misalignment or deep crash.
        max_len = self.positional_encoding.size(1)
        if L > max_len:
            raise ValueError(f"sequence_length={L} exceeds max_len={max_len} in TradeEmbedding")

        x_proj = self.linear(x)
        pos_enc = self.positional_encoding[:, :L, :]
        return x_proj + pos_enc

class MultiHeadSelfAttention(nn.Module):
    def __init__(self, embedding_dim=64, num_heads=4, dropout=0.1):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads #assigning values

        assert embedding_dim % num_heads == 0 #Embedding dimensions must be divisible by number of heads

        self.query_layer = nn.Linear(embedding_dim, embedding_dim)
        self.key_layer = nn.Linear(embedding_dim, embedding_dim)
        self.value_layer = nn.Linear(embedding_dim, embedding_dim)
        #Creating 64x64 vectors for Q, K, V

        self.output_layer = nn.Linear(embedding_dim, embedding_dim)

        self.attn_drop = nn.Dropout(dropout)  # drop on softmax weights
        self.out_drop  = nn.Dropout(dropout)  # drop on output projection

    def forward(self, trade_seq, mask=None):
        """
        trade_seq: Tensor of shape [batch_size, seq_len, embedding_dim]
        """
        batch_size, seq_len, embed_dim = trade_seq.size()

        # Step 1: Create Q, K, V
        Q = self.query_layer(trade_seq)  # [batch, seq_len, embed_dim]
        K = self.key_layer(trade_seq)
        V = self.value_layer(trade_seq)


        # Step 2: Split each embedding into multiple heads
        # Reshape to [batch, seq_len, num_heads, head_dim] then transpose to [batch, num_heads, seq_len, head_dim]
        def reshape_for_heads(x):
            return x.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        Q = reshape_for_heads(Q)
        K = reshape_for_heads(K)
        V = reshape_for_heads(V)

        if mask is None:
            # Default to causal look-back mask; True = BLOCK future
            mask = build_causal_mask(seq_len, trade_seq.device)  # [1,1,L,L]

        # Step 3: Compute scaled dot-product attention
        # Q . K^T --> [batch, heads, seq_len, seq_len]
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)

        if mask is not None:
            # True = BLOCK → set to -inf before softmax
            scores = scores.masked_fill(mask, float('-inf'))

        attention_weights = torch.softmax(scores, dim=-1)
        attention_weights = self.attn_drop(attention_weights)

        # Step 4: Multiply by V --> [batch, heads, seq_len, head_dim]
        attention_output = torch.matmul(attention_weights, V)

        # Step 5: Combine heads back into one
        # Transpose back and reshape to [batch, seq_len, embed_dim]
        attention_output = attention_output.transpose(1, 2).contiguous().view(batch_size, seq_len, embed_dim)


        # Step 6: Pass through final linear layer
        out = self.output_layer(attention_output)
        return self.out_drop(out)

class AddNorm(nn.Module):
    def __init__(self, embedding_dim, dropout=0.1):
        super().__init__()
        # Dropout randomly zeroes some elements to help prevent overfitting
        self.dropout = nn.Dropout(dropout)
        # LayerNorm will standardize each embedding vector (mean=0, std=1)
        self.norm = nn.LayerNorm(embedding_dim)

    def forward(self, x, sublayer_output):
        """
        x              : the original input to this sub-layer
                         shape [batch_size, seq_len, embedding_dim]
        sublayer_output: the output from the sub-layer (attention or feedforward)
                         same shape as x
        """
        # 1) Apply dropout to the sublayer output
        dropped = self.dropout(sublayer_output)
        # 2) Add the original input (residual connection)
        added   = x + dropped
        # 3) Normalize the summed tensor
        return self.norm(added)

class PositionWiseFFN(nn.Module):
    def __init__(self, emb_dim=64, ff_hidden=256, dropout=0.1):
        super().__init__()
        self.expand  = nn.Linear(emb_dim, ff_hidden)
        self.act     = nn.GELU()           # smoother activation than ReLU
        self.drop1   = nn.Dropout(dropout) # dropout after activation
        self.project = nn.Linear(ff_hidden, emb_dim)
        self.drop2   = nn.Dropout(dropout) # dropout after projecting back

    def forward(self, x):
        x2 = self.expand(x)    # expand from emb_dim → ff_hidden
        x2 = self.act(x2)      # non-linear transformation
        x2 = self.drop1(x2)    # regularize hidden layer
        x2 = self.project(x2)  # project back to emb_dim
        return self.drop2(x2)  # regularize before residual connection

class TransformerEncoderBlock(nn.Module):
    def __init__(self,
                 emb_dim=64,
                 num_heads=4,
                 ff_hidden=256,
                 dropout=0.1):
        super().__init__()

        # Updated attention now uses new mask helpers + separate dropouts
        self.attn     = MultiHeadSelfAttention(
                            embedding_dim=emb_dim,
                            num_heads=num_heads,
                            dropout=dropout
                        )
        self.addnorm1 = AddNorm(
                            embedding_dim=emb_dim,
                            dropout=dropout
                        )

        # Updated FFN with GELU + 2 dropouts
        self.ffn      = PositionWiseFFN(
                            emb_dim=emb_dim,
                            ff_hidden=ff_hidden,
                            dropout=dropout
                        )
        self.addnorm2 = AddNorm(
                            embedding_dim=emb_dim,
                            dropout=dropout
                        )

    def forward(self, x, attn_mask=None):
        """
        x        : [B, L, emb_dim]
        attn_mask: broadcastable to [B, H, L, L], True = block
        """

        # Multi-head attention with mask
        attn_out = self.attn(x, attn_mask)
        x = self.addnorm1(x, attn_out)  # residual + layer norm

        # Feed-forward network
        ffn_out = self.ffn(x)
        x = self.addnorm2(x, ffn_out)   # residual + layer norm

        return x

# ----------------------------
# 1) Stack N encoder blocks
# ----------------------------
class TransformerEncoder(nn.Module):
    def __init__(self, emb_dim=64, num_layers=3, num_heads=4, ff_hidden=256, dropout=0.1):
        super().__init__()
        self.layers = nn.ModuleList([
            TransformerEncoderBlock(emb_dim=emb_dim,
                                    num_heads=num_heads,
                                    ff_hidden=ff_hidden,
                                    dropout=dropout)
            for _ in range(num_layers)
        ])

    def forward(self, x, attn_mask=None):
        for layer in self.layers:
            x = layer(x, attn_mask=attn_mask)
        return x  # [B, L, D]

# ----------------------------
# 2) Classification Head - Simplified
# ----------------------------
class ClassificationHead(nn.Module):
    """
    Simple classification head that takes embeddings and outputs bias predictions.
    """
    def __init__(self, embedding_dim=64, num_bias_classes=11):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_classes = num_bias_classes
        
        # Layer normalization for stable training
        self.layer_norm = nn.LayerNorm(embedding_dim)
        
        # Final classification layer
        self.classifier = nn.Linear(embedding_dim, num_bias_classes)

    def forward(self, embeddings):
        """
        Convert embeddings to bias predictions.
        
        Args:
            embeddings: Tensor of shape [batch_size, embedding_dim] or [batch_size, seq_len, embedding_dim]
        
        Returns:
            logits: Raw prediction scores [batch_size, num_classes] or [batch_size, seq_len, num_classes]
        """
        # Normalize embeddings for stable training
        normalized_embeddings = self.layer_norm(embeddings)
        
        # Generate predictions
        predictions = self.classifier(normalized_embeddings)
        
        return predictions

# ----------------------------
# 3) Main Model - Simplified
# ----------------------------
class EmotionalBiasModel(nn.Module):
    """
    Complete model for detecting emotional biases in trading sequences.
    
    This model takes sequences of trading data and predicts which emotional
    biases are present at each time step.
    """
    
    def __init__(self,
                 input_dim=49,        # Number of features per trade
                 embedding_dim=64,    # Size of embeddings
                 max_sequence_length=500,  # Maximum sequence length for positional encoding
                 num_encoder_layers=3,     # Number of transformer encoder layers
                 num_attention_heads=4,    # Number of attention heads
                 feedforward_hidden=256,   # Hidden size in feedforward network
                 dropout_rate=0.1,         # Dropout rate for regularization
                 num_bias_classes=11,      # Number of bias types to predict
                 pooling_method="last"):   # How to pool sequence: "mean", "last", "token"
        super().__init__()
        
        # Store configuration
        self.input_dim = input_dim
        self.embedding_dim = embedding_dim
        self.num_bias_classes = num_bias_classes
        self.pooling_method = pooling_method
        
        # Model components
        self.embedding_layer = TradeEmbedding(
            input_dim=input_dim,
            embedding_dim=embedding_dim,
            max_len=max_sequence_length
        )
        
        self.transformer_encoder = TransformerEncoder(
            emb_dim=embedding_dim,
            num_layers=num_encoder_layers,
            num_heads=num_attention_heads,
            ff_hidden=feedforward_hidden,
            dropout=dropout_rate
        )
        
        self.classification_head = ClassificationHead(
            embedding_dim=embedding_dim,
            num_bias_classes=num_bias_classes
        )

    def _apply_pooling(self, sequence_embeddings):
        """
        Apply pooling to convert sequence embeddings to fixed-size representation.
        
        Args:
            sequence_embeddings: [batch_size, sequence_length, embedding_dim]
            
        Returns:
            pooled_embeddings: [batch_size, embedding_dim] or [batch_size, sequence_length, embedding_dim]
        """
        if self.pooling_method == "mean":
            # Average all positions in the sequence
            return sequence_embeddings.mean(dim=1)
        elif self.pooling_method == "last":
            # Use only the last position
            return sequence_embeddings[:, -1, :]
        elif self.pooling_method == "first":
            # Use only the first position (like BERT's [CLS] token)
            return sequence_embeddings[:, 0, :]
        elif self.pooling_method == "token":
            # Keep all positions for per-token classification
            return sequence_embeddings
        else:
            raise ValueError(f"Unknown pooling method: {self.pooling_method}")

    def forward(self, trade_sequences, attention_mask=None):
        """
        Forward pass through the complete model.
        
        Args:
            trade_sequences: [batch_size, sequence_length, input_dim] - Trading data
            attention_mask: Optional mask for attention mechanism
            
        Returns:
            bias_predictions: [batch_size, num_classes] or [batch_size, sequence_length, num_classes]
        """
        # Step 1: Convert raw features to embeddings
        embeddings = self.embedding_layer(trade_sequences)
        
        # Step 2: Process through transformer encoder
        encoded_sequences = self.transformer_encoder(embeddings, attention_mask)
        
        # Step 3: Apply pooling to get fixed-size representation
        pooled_representations = self._apply_pooling(encoded_sequences)
        
        # Step 4: Generate bias predictions
        bias_predictions = self.classification_head(pooled_representations)
        
        return bias_predictions

# ============================================
# CONFIGURATION AND DATA PROCESSING
# ============================================
import random
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
import hashlib

# -----------------------
# Configuration Class
# -----------------------
class ModelConfig:
    """Configuration settings for the emotional bias detection model."""
    
    # Data column names
    TRADER_ID_COLUMN = "trader_id"
    TRADE_ID_COLUMN = "trade_id"
    TICKER_COLUMN = "symbol"
    
    # Training parameters
    BATCH_SIZE = 32
    RANDOM_SEED = 42
    
    # Model architecture
    INPUT_DIM = 49
    EMBEDDING_DIM = 64
    MAX_SEQUENCE_LENGTH = 500
    NUM_ENCODER_LAYERS = 3
    NUM_ATTENTION_HEADS = 4
    FEEDFORWARD_HIDDEN = 256
    DROPOUT_RATE = 0.15  # Confirmed: explicitly set to 0.15
    
    # Training hyperparameters
    LEARNING_RATE = 0.002
    WEIGHT_DECAY = 1e-3
    NUM_EPOCHS = 85
    EARLY_STOPPING_PATIENCE = 12
    
    # Data split ratios
    TRAIN_RATIO = 0.70
    VALIDATION_RATIO = 0.15
    TEST_RATIO = 0.15
    
    # Ticker feature engineering
    NUM_TICKER_BUCKETS = 32
    
    # Feature columns (numeric features used for prediction)
    FEATURE_COLUMNS = [
    "entry_price", "exit_price", "qty", "position_value",
    "holding_time_min",
    "pnl_abs", "pnl_pct", "prev_pnl_pct",
    "size_vs_prev", "time_since_prev_close_min",
    "streak_wins", "streak_losses",
    "cum_pnl_pct", "avg_position_value_so_far",
    "side_switch_prev",     # already numeric (0/1)
        "side"                  # just created (+1/-1/0)
]

    # Label columns (bias types to predict)
    BIAS_LABEL_COLUMNS = [
    "bias_overconfidence", "bias_confirmation", "bias_recency",
    "bias_disposition", "bias_loss_aversion", "bias_anchoring",
    "bias_sunk_cost", "bias_gamblers_fallacy", "bias_hot_hand",
    "bias_house_money", "bias_endowment"
]
    
    @property
    def num_bias_classes(self):
        """Number of bias types to predict."""
        return len(self.BIAS_LABEL_COLUMNS)
    
    @property
    def total_feature_columns(self):
        """Total number of feature columns including ticker features."""
        return len(self.FEATURE_COLUMNS) + self.NUM_TICKER_BUCKETS + 1  # +1 for ticker_same_prev

# Create global config instance
config = ModelConfig()

# -----------------------
# Device Setup
# -----------------------
def setup_device():
    """Set up the computing device (GPU if available, otherwise CPU)."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")
    return device

device = setup_device()

# -----------------------
# Data Validation and Preparation
# -----------------------
def validate_dataframe(df):
    """Validate that the input DataFrame has all required columns."""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    # Check for missing feature columns
    missing_features = [col for col in config.FEATURE_COLUMNS if col not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")
    
    # Check for missing label columns
    missing_labels = [col for col in config.BIAS_LABEL_COLUMNS if col not in df.columns]
    if missing_labels:
        raise ValueError(f"Missing label columns: {missing_labels}")
    
    # Validate that feature columns are numeric
    for col in config.FEATURE_COLUMNS:
        if not np.issubdtype(df[col].dtype, np.number):
            raise ValueError(f"Feature column '{col}' must be numeric, got dtype={df[col].dtype}")
    
    print(f"DataFrame validation passed. Using {len(config.FEATURE_COLUMNS)} feature columns and {len(config.BIAS_LABEL_COLUMNS)} label columns.")

def prepare_data(df):
    """Prepare the raw DataFrame for model training."""
    validate_dataframe(df)
    return df.copy()

# Prepare the data
df = pd.read_csv("merged_trades_with_biases.csv")
data = prepare_data(df)

# -----------------------
# Data Splitting by Trader
# -----------------------
def split_data_by_trader(df):
    """
    Split data by trader to prevent data leakage.
    No trades from the same trader appear in both train and test sets.
    """
    # Get unique traders
    traders = df[config.TRADER_ID_COLUMN].dropna().unique().tolist()
    print(f"Found {len(traders)} unique traders: {traders}")
    
    # Shuffle traders for random split
    random.Random(config.RANDOM_SEED).shuffle(traders)
    
    # Calculate split sizes
    total_traders = len(traders)
    train_size = int(total_traders * config.TRAIN_RATIO)
    val_size = int(total_traders * config.VALIDATION_RATIO)
    
    # Split trader IDs
    train_traders = traders[:train_size]
    val_traders = traders[train_size:train_size + val_size]
    test_traders = traders[train_size + val_size:]
    
    # Create data splits
    train_data = df[df[config.TRADER_ID_COLUMN].isin(train_traders)].copy()
    val_data = df[df[config.TRADER_ID_COLUMN].isin(val_traders)].copy()
    test_data = df[df[config.TRADER_ID_COLUMN].isin(test_traders)].copy()
    
    print(f"Data split - Train: {len(train_traders)} traders, Val: {len(val_traders)} traders, Test: {len(test_traders)} traders")
    print(f"Trade counts - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
    
    return train_data, val_data, test_data

# Split the data
train_df, val_df, test_df = split_data_by_trader(data)

# -----------------------
# Ticker Feature Engineering
# -----------------------
def create_ticker_bucket(ticker_symbol, num_buckets):
    """
    Convert ticker symbol to a hash bucket for categorical encoding.
    
    Args:
        ticker_symbol: Stock ticker symbol (e.g., 'AAPL')
        num_buckets: Number of hash buckets to use
        
    Returns:
        Bucket index (0 to num_buckets-1)
    """
    # Normalize ticker symbol (handle NaN and case)
    normalized_ticker = "" if pd.isna(ticker_symbol) else str(ticker_symbol).upper()
    
    # Create hash bucket
    hash_value = int(hashlib.md5(normalized_ticker.encode()).hexdigest(), 16)
    return hash_value % num_buckets

def add_ticker_features(dataframe):
    """
    Add ticker-based features to the dataframe.
    
    Features added:
    1. One-hot encoded ticker buckets (tickh_0, tickh_1, ..., tickh_31)
    2. Continuity flag indicating if same ticker as previous trade
    """
    # Validate ticker column exists
    if config.TICKER_COLUMN not in dataframe.columns:
        raise ValueError(f"Missing ticker column '{config.TICKER_COLUMN}' in dataframe")
    
    df = dataframe.copy()
    
    # Create ticker buckets
    ticker_buckets = df[config.TICKER_COLUMN].map(
        lambda x: create_ticker_bucket(x, config.NUM_TICKER_BUCKETS)
    )
    
    # Create one-hot encoded ticker features
    for bucket_idx in range(config.NUM_TICKER_BUCKETS):
        df[f"tickh_{bucket_idx}"] = (ticker_buckets == bucket_idx).astype(np.float32)
    
    # Create continuity feature: same ticker as previous trade?
    previous_ticker = df.groupby(config.TRADER_ID_COLUMN)[config.TICKER_COLUMN].shift(1)
    df["ticker_same_prev"] = (
        df[config.TICKER_COLUMN].astype(str).str.upper() == 
        previous_ticker.astype(str).str.upper()
    ).fillna(False).astype(np.float32)

    return df

def add_ticker_features_to_splits(train_df, val_df, test_df):
    """Add ticker features to all data splits."""
    train_with_ticker = add_ticker_features(train_df)
    val_with_ticker = add_ticker_features(val_df)
    test_with_ticker = add_ticker_features(test_df)
    
    # Create list of new ticker feature columns
    ticker_feature_columns = [f"tickh_{i}" for i in range(config.NUM_TICKER_BUCKETS)] + ["ticker_same_prev"]
    
    print(f"Added {len(ticker_feature_columns)} ticker features to all data splits")
    
    return train_with_ticker, val_with_ticker, test_with_ticker

# Add ticker features to all splits
train_df, val_df, test_df = add_ticker_features_to_splits(train_df, val_df, test_df)

# -----------------------
# Data Preprocessing
# -----------------------
def get_all_feature_columns():
    """Get all feature columns including ticker features."""
    ticker_features = [f"tickh_{i}" for i in range(config.NUM_TICKER_BUCKETS)] + ["ticker_same_prev"]
    return config.FEATURE_COLUMNS + ticker_features

def fill_missing_values(train_df, val_df, test_df):
    """Fill missing values using training data statistics."""
    all_feature_cols = get_all_feature_columns()
    
    # Calculate means from training data only
    train_means = train_df[all_feature_cols].mean()
    
    # Fill missing values in all splits using training means
    for df in [train_df, val_df, test_df]:
        df.loc[:, all_feature_cols] = df[all_feature_cols].fillna(train_means)
    
    print("Filled missing values using training data statistics")
    return train_df, val_df, test_df

def standardize_features(train_df, val_df, test_df):
    """Standardize features using training data statistics."""
    all_feature_cols = get_all_feature_columns()
    
    # Calculate mean and std from training data only
    train_mean = train_df[all_feature_cols].mean()
    train_std = train_df[all_feature_cols].std().replace(0, 1.0)  # Avoid divide-by-zero
    
    # Standardize all splits using training statistics
    for df in [train_df, val_df, test_df]:
        df.loc[:, all_feature_cols] = ((df[all_feature_cols] - train_mean) / train_std).astype(np.float32)
    
    print("Standardized features using training data statistics")
    return train_df, val_df, test_df

# Apply preprocessing steps
train_df, val_df, test_df = fill_missing_values(train_df, val_df, test_df)
train_df, val_df, test_df = standardize_features(train_df, val_df, test_df)

# -----------------------
# Sequence Building
# -----------------------
def build_sequences_from_dataframe(dataframe):
    """
    Convert dataframe to sequences for each trader.
    
    Args:
        dataframe: DataFrame with features and labels
        
    Returns:
        feature_sequences: List of numpy arrays [trader_sequence_length, num_features]
        label_sequences: List of numpy arrays [trader_sequence_length, num_bias_classes]
    """
    feature_sequences = []
    label_sequences = []
    all_feature_cols = get_all_feature_columns()
    
    # Group by trader and create sequences
    for trader_id, trader_data in dataframe.groupby(config.TRADER_ID_COLUMN, sort=False):
        # Extract features and labels for this trader
        trader_features = trader_data[all_feature_cols].to_numpy(dtype=np.float32)
        trader_labels = trader_data[config.BIAS_LABEL_COLUMNS].to_numpy(dtype=np.float32)
        
        feature_sequences.append(trader_features)
        label_sequences.append(trader_labels)
    
    return feature_sequences, label_sequences

def build_all_sequences(train_df, val_df, test_df):
    """Build sequences for all data splits."""
    print("Building sequences from dataframes...")
    
    # Build sequences for each split
    train_features, train_labels = build_sequences_from_dataframe(train_df)
    val_features, val_labels = build_sequences_from_dataframe(val_df)
    test_features, test_labels = build_sequences_from_dataframe(test_df)
    
    # Calculate maximum sequence length across all splits
    all_sequences = train_features + val_features + test_features
    max_sequence_length = max(seq.shape[0] for seq in all_sequences)
    
    print(f"Built sequences - Train: {len(train_features)}, Val: {len(val_features)}, Test: {len(test_features)}")
    print(f"Maximum sequence length across all splits: {max_sequence_length}")
    
    return (train_features, train_labels, val_features, val_labels, 
            test_features, test_labels, max_sequence_length)

# Build all sequences
train_features, train_labels, val_features, val_labels, test_features, test_labels, max_seq_len = build_all_sequences(train_df, val_df, test_df)

# -----------------------
# Loss Function Setup
# -----------------------
def calculate_class_weights(train_labels):
    """
    Calculate class weights to handle class imbalance.
    
    Args:
        train_labels: List of label arrays for training data
        
    Returns:
        pos_weight: Tensor of positive class weights for each bias type
    """
    # Flatten all training labels
    all_train_labels = torch.from_numpy(np.concatenate(train_labels, axis=0))
    
    # Calculate positive and negative counts for each class
    positive_counts = all_train_labels.sum(0)  # [num_classes]
    negative_counts = all_train_labels.shape[0] - positive_counts
    
    # Calculate positive class weights (higher weight for rare classes)
    positive_weights = (negative_counts / positive_counts.clamp_min(1.0)).to(device)
    
    return positive_weights

def create_loss_function(class_weights):
    """Create the loss function with class weights."""
    return torch.nn.BCEWithLogitsLoss(pos_weight=class_weights, reduction="none")

# Calculate class weights and create loss function
class_weights = calculate_class_weights(train_labels)
loss_function = create_loss_function(class_weights)

print(f"Calculated class weights for {len(class_weights)} bias classes")


def calculate_masked_loss(predictions, targets, padding_mask):
    """
    Calculate loss only on non-padded positions.
    
    Args:
        predictions: [batch_size, sequence_length, num_classes] - Model predictions
        targets: [batch_size, sequence_length, num_classes] - True labels
        padding_mask: [batch_size, sequence_length] - True where padded
        
    Returns:
        Average loss over valid (non-padded) positions
    """
    # Calculate raw loss for all positions
    raw_loss = loss_function(predictions, targets)  # [B, L, C]
    
    # Create mask for valid positions (not padded)
    valid_mask = (~padding_mask).unsqueeze(-1).float()  # [B, L, 1]
    
    # Apply mask and calculate average loss
    masked_loss = raw_loss * valid_mask
    total_loss = masked_loss.sum()
    valid_positions = valid_mask.sum().clamp_min(1.0)
    
    return total_loss / valid_positions

print(f"Train sequences: {len(train_features)}")
print(f"Sample train sequence shape - Features: {train_features[0].shape}, Labels: {train_labels[0].shape}")

# -----------------------
# Dataset Classes
# -----------------------
class TradingSequenceDataset(Dataset):
    """
    Dataset for trading sequences with features and bias labels.
    """
    
    def __init__(self, feature_sequences, label_sequences):
        """
        Args:
            feature_sequences: List of numpy arrays [sequence_length, num_features]
            label_sequences: List of numpy arrays [sequence_length, num_bias_classes]
        """
        self.features = feature_sequences
        self.labels = label_sequences
        
        # Validate that features and labels have same length
        if len(self.features) != len(self.labels):
            raise ValueError("Number of feature and label sequences must match")
    
    def __len__(self):
        """Return number of sequences (traders)."""
        return len(self.features)
    
    def __getitem__(self, index):
        """Return features and labels for a single trader sequence."""
        return self.features[index], self.labels[index]

def create_datasets(train_features, train_labels, val_features, val_labels, test_features, test_labels):
    """Create PyTorch datasets for all splits."""
    train_dataset = TradingSequenceDataset(train_features, train_labels)
    val_dataset = TradingSequenceDataset(val_features, val_labels)
    test_dataset = TradingSequenceDataset(test_features, test_labels)
    
    print(f"Created datasets - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
    
    return train_dataset, val_dataset, test_dataset

# Create datasets
train_dataset, val_dataset, test_dataset = create_datasets(
    train_features, train_labels, val_features, val_labels, test_features, test_labels
)

# -----------------------
# Attention Mask Helpers
# -----------------------
def create_causal_mask(sequence_length, device):
    """
    Create a causal mask to prevent attention to future positions.
    
    Args:
        sequence_length: Length of the sequence
        device: Device to create the mask on
        
    Returns:
        mask: [1, 1, sequence_length, sequence_length] - True where attention should be blocked
    """
    # Create upper triangular matrix (True above diagonal = block future)
    causal_mask = torch.triu(
        torch.ones(sequence_length, sequence_length, dtype=torch.bool, device=device), 
        diagonal=1
    )
    
    # Add batch and head dimensions for broadcasting
    return causal_mask.unsqueeze(0).unsqueeze(0)  # [1, 1, L, L]

def create_padding_mask(padding_indicator):
    """
    Create a mask to block attention to padded positions.
    
    Args:
        padding_indicator: [batch_size, sequence_length] - True where padded
        
    Returns:
        mask: [batch_size, 1, 1, sequence_length] - True where attention should be blocked
    """
    return padding_indicator[:, None, None, :]

def combine_attention_masks(*masks):
    """
    Combine multiple attention masks using OR operation.
    
    Args:
        *masks: Variable number of attention masks
        
    Returns:
        combined_mask: Combined mask, or None if no masks provided
    """
    # Filter out None masks
    valid_masks = [mask for mask in masks if mask is not None]
    
    if not valid_masks:
        return None
    
    # Start with first mask and combine with others
    combined_mask = valid_masks[0]
    for mask in valid_masks[1:]:
        combined_mask = combined_mask | mask
    
    return combined_mask

# -----------------------
# Data Collation (Batching)
# -----------------------
def collate_sequences(batch):
    """
    Collate sequences of different lengths into batches with left padding.
    
    Args:
        batch: List of (features, labels) tuples where each sequence can have different length
        
    Returns:
        features: [batch_size, max_length, num_features] - Padded feature sequences
        labels: [batch_size, max_length, num_classes] - Padded label sequences  
        attention_mask: Combined causal and padding mask
        padding_mask: [batch_size, max_length] - True where padded
    """
    # Separate features and labels
    feature_sequences = [item[0] for item in batch]
    label_sequences = [item[1] for item in batch]
    
    # Get dimensions
    batch_size = len(feature_sequences)
    num_features = feature_sequences[0].shape[1]
    num_classes = label_sequences[0].shape[1]
    max_length = max(seq.shape[0] for seq in feature_sequences)
    
    # Initialize lists for padded sequences
    padded_features = []
    padded_labels = []
    padding_masks = []
    
    # Pad each sequence to the same length
    for features, labels in zip(feature_sequences, label_sequences):
        sequence_length = features.shape[0]
        padding_needed = max_length - sequence_length
        
        if padding_needed > 0:
            # Create padding (zeros on the left)
            feature_padding = np.zeros((padding_needed, num_features), dtype=np.float32)
            label_padding = np.zeros((padding_needed, num_classes), dtype=np.float32)
            
            # Concatenate padding with actual data
            padded_feature_seq = np.vstack([feature_padding, features])
            padded_label_seq = np.vstack([label_padding, labels])
            
            # Create padding mask (True where padded)
            padding_mask = np.zeros(max_length, dtype=bool)
            padding_mask[:padding_needed] = True
        else:
            # No padding needed
            padded_feature_seq = features
            padded_label_seq = labels
            padding_mask = np.zeros(max_length, dtype=bool)
        
        padded_features.append(padded_feature_seq)
        padded_labels.append(padded_label_seq)
        padding_masks.append(padding_mask)
    
    # Convert to tensors and move to device
    feature_tensor = torch.from_numpy(np.stack(padded_features, axis=0)).to(device)
    label_tensor = torch.from_numpy(np.stack(padded_labels, axis=0)).to(device)
    padding_mask_tensor = torch.from_numpy(np.stack(padding_masks, axis=0)).to(device)
    
    # Create combined attention mask
    causal_mask = create_causal_mask(max_length, device)
    padding_attention_mask = create_padding_mask(padding_mask_tensor)
    combined_attention_mask = combine_attention_masks(causal_mask, padding_attention_mask)
    
    return feature_tensor, label_tensor, combined_attention_mask, padding_mask_tensor

# -----------------------
# Data Loaders
# -----------------------
def create_data_loaders(train_dataset, val_dataset, test_dataset):
    """Create data loaders for training, validation, and testing."""
    train_loader = DataLoader(
        train_dataset, 
        batch_size=config.BATCH_SIZE, 
        shuffle=True,  # Shuffle training data
        pin_memory=(device.type == "cuda"),  # Faster GPU transfer on CUDA only
        collate_fn=collate_sequences
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=config.BATCH_SIZE, 
        shuffle=False,  # Don't shuffle validation data
        pin_memory=(device.type == "cuda"),
        collate_fn=collate_sequences
    )
    
    test_loader = DataLoader(
        test_dataset, 
        batch_size=config.BATCH_SIZE, 
        shuffle=False,  # Don't shuffle test data
        pin_memory=(device.type == "cuda"),
        collate_fn=collate_sequences
    )
    
    print(f"Created data loaders with batch size {config.BATCH_SIZE}")
    return train_loader, val_loader, test_loader

# Create data loaders
train_loader, val_loader, test_loader = create_data_loaders(train_dataset, val_dataset, test_dataset)

# -----------------------
# Model Creation and Setup
# -----------------------
def create_model():
    """Create and configure the emotional bias detection model."""
    all_feature_cols = get_all_feature_columns()
    
    model = EmotionalBiasModel(
        input_dim=len(all_feature_cols),
        embedding_dim=config.EMBEDDING_DIM,
        max_sequence_length=max_seq_len,
        num_encoder_layers=config.NUM_ENCODER_LAYERS,
        num_attention_heads=config.NUM_ATTENTION_HEADS,
        feedforward_hidden=config.FEEDFORWARD_HIDDEN,
        dropout_rate=config.DROPOUT_RATE,
        num_bias_classes=config.num_bias_classes,
        pooling_method="token"  # Per-token classification
    ).to(device)
    
    return model

def create_optimizer(model):
    """Create optimizer for the model."""
    return torch.optim.AdamW(
        model.parameters(), 
        lr=config.LEARNING_RATE, 
        weight_decay=config.WEIGHT_DECAY
    )

def test_data_loading():
    """Test that data loading works correctly."""
    print("Testing data loading...")
    
    # Get one batch from training data
    sample_batch = next(iter(train_loader))
    features, labels, attention_mask, padding_mask = sample_batch
    
    print(f"Feature tensor shape: {features.shape}")
    print(f"Label tensor shape: {labels.shape}")
    print(f"Attention mask shape: {attention_mask.shape}")
    print(f"Padding mask shape: {padding_mask.shape}")
    
    # Check that padding is on the left
    print(f"First sequence padding (True=padded): {padding_mask[0].tolist()}")
    print(f"Last position is real for all sequences: {bool(torch.all(~padding_mask[:, -1]))}")
    
    print("Data loading test passed!")

# Create model and optimizer
model = create_model()
optimizer = create_optimizer(model)

# Test data loading
test_data_loading()

print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")



# -----------------------
# Evaluation Metrics
# -----------------------
@torch.no_grad()
def calculate_micro_f1_score(predictions, targets, padding_mask, threshold=0.45):
    """
    Calculate micro-averaged F1 score across all classes and valid positions.
    
    Args:
        predictions: [batch_size, sequence_length, num_classes] - Model predictions
        targets: [batch_size, sequence_length, num_classes] - True labels
        padding_mask: [batch_size, sequence_length] - True where padded
        threshold: Threshold for converting probabilities to binary predictions
        
    Returns:
        micro_f1: Micro-averaged F1 score
    """
    # Convert logits to probabilities
    probabilities = torch.sigmoid(predictions)  # [B, L, C]
    
    # Convert to binary predictions
    binary_predictions = (probabilities >= threshold).int()  # [B, L, C]
    binary_targets = targets.int()  # [B, L, C]
    
    # Create mask for valid (non-padded) positions
    valid_positions = (~padding_mask).unsqueeze(-1)  # [B, L, 1]
    valid_positions = valid_positions.expand_as(binary_predictions)  # [B, L, C]
    
    # Apply mask to get only valid predictions and targets
    valid_predictions = binary_predictions[valid_positions]  # [N]
    valid_targets = binary_targets[valid_positions]  # [N]
    
    # Calculate true positives, false positives, false negatives
    true_positives = ((valid_predictions == 1) & (valid_targets == 1)).sum().item()
    false_positives = ((valid_predictions == 1) & (valid_targets == 0)).sum().item()
    false_negatives = ((valid_predictions == 0) & (valid_targets == 1)).sum().item()
    
    # Calculate F1 score
    denominator = 2 * true_positives + false_positives + false_negatives
    micro_f1 = (2 * true_positives / denominator) if denominator > 0 else 0.0
    
    return micro_f1

# -----------------------
# Advanced Evaluation/Calibration/Thresholding
# -----------------------
@torch.no_grad()
def collect_logits_labels(model, data_loader, device):
    model.eval()
    all_logits, all_labels, all_masks = [], [], []
    for feats, labels, attn_mask, pad_mask in data_loader:
        feats = feats.to(device)
        labels = labels.to(device)
        logits = model(feats, attention_mask=attn_mask)  # [B,L,C]
        all_logits.append(logits.cpu())
        all_labels.append(labels.cpu())
        all_masks.append(pad_mask.cpu())
    return torch.cat(all_logits, dim=0), torch.cat(all_labels, dim=0), torch.cat(all_masks, dim=0)

def per_class_metrics(logits, labels, pad_mask, thresholds=None, class_names=None):
    """
    logits   : [N, L, C]
    labels   : [N, L, C] (0/1)
    pad_mask : [N, L] (True=padded)
    thresholds: None or 1D array of shape [C]
    """
    probs = torch.sigmoid(logits)  # [N,L,C]
    N, L, C = probs.shape
    if thresholds is None:
        thresholds = np.full(C, 0.45, dtype=np.float32)

    # flatten valid positions
    probs_flat = probs.view(-1, C).numpy()
    labels_flat = labels.view(-1, C).numpy().astype(int)
    valid_flat  = (~pad_mask).view(-1).numpy().astype(bool)

    y_true = labels_flat[valid_flat]            # [M, C]
    y_prob = probs_flat[valid_flat]             # [M, C]
    y_pred = (y_prob >= thresholds[None, :]).astype(int)

    # per-class metrics
    p, r, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )

    # macro / weighted aggregates
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    results = {
        "per_class": [],
        "macro": {"precision": float(p_macro), "recall": float(r_macro), "f1": float(f1_macro)},
        "weighted": {"precision": float(p_weighted), "recall": float(r_weighted), "f1": float(f1_weighted)},
        "support": support.tolist(),
    }
    for i in range(len(p)):
        name = class_names[i] if class_names else f"class_{i}"
        results["per_class"].append({
            "class": name,
            "precision": float(p[i]),
            "recall": float(r[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        })
    return results

def tune_thresholds_on_validation(logits, labels, pad_mask, class_names=None, grid=None):
    """
    Returns a numpy array of best thresholds per class (length C)
    chosen to maximize per-class F1 on the validation set.
    """
    if grid is None:
        grid = np.linspace(0.05, 0.95, 19)

    probs = torch.sigmoid(logits).numpy()    # [N,L,C]
    y_true = labels.numpy().astype(int)      # [N,L,C]
    valid = (~pad_mask).numpy()              # [N,L]
    N, L, C = probs.shape

    probs_flat = probs.reshape(-1, C)[valid.reshape(-1)]
    y_flat     = y_true.reshape(-1, C)[valid.reshape(-1)]

    best_th = np.zeros(C, dtype=np.float32)
    for c in range(C):
        best_f1, best_t = -1.0, 0.5
        y_c = y_flat[:, c]
        p_c = probs_flat[:, c]
        for t in grid:
            y_pred = (p_c >= t).astype(int)
            _, _, f1, _ = precision_recall_fscore_support(
                y_c, y_pred, average="binary", zero_division=0
            )
            if f1 > best_f1:
                best_f1, best_t = f1, t
        best_th[c] = best_t
        # name = class_names[c] if class_names else c
        # print(f"Best threshold for {name}: {best_t:.2f} (F1={best_f1:.4f})")
    return best_th

def reliability_bins_and_ece(logits, labels, pad_mask, n_bins=15):
    probs = torch.sigmoid(logits.detach()).numpy()   # <— detach here
    y_true = labels.numpy().astype(int)        # [N,L,C]
    valid = (~pad_mask).numpy()                # [N,L]
    probs = probs.reshape(-1, probs.shape[-1])[valid.reshape(-1)]
    y_true = y_true.reshape(-1, y_true.shape[-1])[valid.reshape(-1)]

    confidences = probs.ravel()
    outcomes    = y_true.ravel()

    bins = np.linspace(0.0, 1.0, n_bins+1)
    bin_ids = np.digitize(confidences, bins) - 1
    bin_acc, bin_conf, bin_count = [], [], []
    ece = 0.0
    for b in range(n_bins):
        idx = (bin_ids == b)
        if idx.sum() == 0:
            bin_acc.append(np.nan); bin_conf.append(np.nan); bin_count.append(0)
            continue
        acc  = outcomes[idx].mean()
        conf = confidences[idx].mean()
        n    = idx.sum()
        ece += (n / len(confidences)) * abs(acc - conf)
        bin_acc.append(acc); bin_conf.append(conf); bin_count.append(int(n))
    return {
        "bins": bins.tolist(),
        "bin_accuracy": bin_acc,
        "bin_confidence": bin_conf,
        "bin_count": bin_count,
        "ECE": float(ece),
    }

class TemperatureScaler(nn.Module):
    def __init__(self, init_temp=1.0):
        super().__init__()
        self.log_temp = nn.Parameter(torch.tensor(np.log(init_temp), dtype=torch.float32))
    def forward(self, logits):
        T = torch.exp(self.log_temp)
        return logits / T

def fit_temperature(model, val_loader, device, max_iters=200, lr=0.01):
    model.eval()
    logits, labels, pad = collect_logits_labels(model, val_loader, device)
    valid = (~pad).unsqueeze(-1).float()    # [N,L,1]

    scaler = TemperatureScaler().to(device)
    opt = torch.optim.LBFGS(scaler.parameters(), lr=lr, max_iter=max_iters)

    logits = logits.to(device)
    labels = labels.to(device).float()
    valid  = valid.to(device)

    def closure():
        opt.zero_grad(set_to_none=True)
        scaled = scaler(logits)
        # BCE loss per element, then mask and sum
        loss = nn.functional.binary_cross_entropy_with_logits(scaled, labels, reduction='none')
        loss = (loss * valid).sum()
        loss.backward()
        return loss

    opt.step(closure)
    with torch.no_grad():
        T = torch.exp(scaler.log_temp).item()
    print(f"🌡️ Fitted temperature T={T:.3f} (val NLL minimized)")
    return scaler

def apply_temperature_scaler(logits, scaler, device):
    return scaler(logits.to(device)).cpu()


# -----------------------
# Training Functions
# -----------------------
def train_one_epoch(model, data_loader, optimizer, device, description="Training"):
    """
    Train the model for one epoch.
    
    Args:
        model: The model to train
        data_loader: DataLoader for training data
        optimizer: Optimizer for updating model parameters
        device: Device to run training on
        description: Description for progress bar
        
    Returns:
        average_loss: Average loss for the epoch
        average_f1: Average F1 score for the epoch
    """
    model.train()  # Set model to training mode
    
    total_loss = 0.0
    total_f1 = 0.0
    total_valid_positions = 0
    
    # Create progress bar
    progress_bar = tqdm(data_loader, desc=description, leave=False)
    
    for batch_features, batch_labels, attention_mask, padding_mask in progress_bar:
        # Move data to device
        batch_features = batch_features.to(device)
        batch_labels = batch_labels.to(device)
        padding_mask = padding_mask.to(device)
        
        # Forward pass
        predictions = model(batch_features, attention_mask=attention_mask)
        
        # Calculate loss
        loss = calculate_masked_loss(predictions, batch_labels, padding_mask)
        
        # Backward pass
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        # Calculate metrics
        with torch.no_grad():
            f1_score = calculate_micro_f1_score(predictions, batch_labels, padding_mask)
        
        # Accumulate metrics (weighted by number of valid positions)
        valid_positions = ((~padding_mask).sum().item()) * batch_labels.size(-1)
        total_loss += loss.item() * max(valid_positions, 1)
        total_f1 += f1_score * max(valid_positions, 1)
        total_valid_positions += max(valid_positions, 1)
        
        # Update progress bar
        progress_bar.set_postfix(
            loss=f"{loss.item():.4f}", 
            f1=f"{f1_score:.4f}"
        )
    
    # Calculate averages
    average_loss = total_loss / max(total_valid_positions, 1)
    average_f1 = total_f1 / max(total_valid_positions, 1)
    
    return average_loss, average_f1

@torch.no_grad()
def evaluate_model(model, data_loader, device, description="Evaluation"):
    """
    Evaluate the model on a dataset.
    
    Args:
        model: The model to evaluate
        data_loader: DataLoader for evaluation data
        device: Device to run evaluation on
        description: Description for progress bar
        
    Returns:
        average_loss: Average loss for the evaluation
        average_f1: Average F1 score for the evaluation
    """
    model.eval()  # Set model to evaluation mode
    
    total_loss = 0.0
    total_f1 = 0.0
    total_valid_positions = 0
    
    # Create progress bar
    progress_bar = tqdm(data_loader, desc=description, leave=False)
    
    for batch_features, batch_labels, attention_mask, padding_mask in progress_bar:
        # Move data to device
        batch_features = batch_features.to(device)
        batch_labels = batch_labels.to(device)
        padding_mask = padding_mask.to(device)
        
        # Forward pass (no gradients needed)
        predictions = model(batch_features, attention_mask=attention_mask)
        
        # Calculate loss and metrics
        loss = calculate_masked_loss(predictions, batch_labels, padding_mask)
        f1_score = calculate_micro_f1_score(predictions, batch_labels, padding_mask)
        
        # Accumulate metrics (weighted by number of valid positions)
        valid_positions = ((~padding_mask).sum().item()) * batch_labels.size(-1)
        total_loss += loss.item() * max(valid_positions, 1)
        total_f1 += f1_score * max(valid_positions, 1)
        total_valid_positions += max(valid_positions, 1)
        
        # Update progress bar
        progress_bar.set_postfix(
            loss=f"{loss.item():.4f}", 
            f1=f"{f1_score:.4f}"
        )
    
    # Calculate averages
    average_loss = total_loss / max(total_valid_positions, 1)
    average_f1 = total_f1 / max(total_valid_positions, 1)
    
    return average_loss, average_f1

# -----------------------
# Main Training Loop
# -----------------------
from copy import deepcopy
import matplotlib.pyplot as plt
from tqdm.auto import trange

def train_model_with_validation(
    model, 
    train_loader, 
    val_loader, 
    test_loader, 
    optimizer, 
    device,
    num_epochs=None,
    use_learning_rate_scheduler=True,
    early_stopping_patience=8,
    checkpoint_path="best_model.ckpt"
):
    """
    Train the model with validation and early stopping.
    
    Args:
        model: The model to train
        train_loader: DataLoader for training data
        val_loader: DataLoader for validation data
        test_loader: DataLoader for test data
        optimizer: Optimizer for training
        device: Device to run training on
        num_epochs: Number of epochs to train (uses config if None)
        use_learning_rate_scheduler: Whether to use learning rate scheduling
        early_stopping_patience: Number of epochs to wait before early stopping
        
    Returns:
        best_epoch: Epoch with best validation F1
        best_val_f1: Best validation F1 score
        best_model: Model with best validation performance
        test_f1: Final test F1 score
    """
    if num_epochs is None:
        num_epochs = config.NUM_EPOCHS
    
    # Initialize tracking variables
    best_val_f1 = -1.0
    best_epoch = 0
    best_model_state = deepcopy(model.state_dict())
    train_losses = []
    val_losses = []
    early_stopping_counter = 0
    lr_drop_count = 0
    
    # Set up learning rate scheduler
    if use_learning_rate_scheduler:
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="max",
            factor=0.5,
            patience=3,
            threshold_mode="rel",
            threshold=0.002,
            cooldown=1,
            min_lr=3e-5
        )
    
    print(f"Starting training for {num_epochs} epochs...")
    
    # Training loop
    for epoch in trange(num_epochs, desc="Training Progress"):
        # Train for one epoch
        train_loss, train_f1 = train_one_epoch(
            model, train_loader, optimizer, device, 
            description=f"Epoch {epoch+1}/{num_epochs} - Training"
        )
        
        # Validate
        val_loss, val_f1 = evaluate_model(
            model, val_loader, device, 
            description=f"Epoch {epoch+1}/{num_epochs} - Validation"
        )
        
        # Store losses for plotting
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        # Update learning rate and track LR drops
        if use_learning_rate_scheduler:
            prev_lr = optimizer.param_groups[0]["lr"]
            scheduler.step(val_f1)
            current_lr = optimizer.param_groups[0]["lr"]
            if current_lr < prev_lr:
                lr_drop_count += 1
        
        # Check for best model
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            best_model_state = deepcopy(model.state_dict())
            early_stopping_counter = 0
            # === SAVE CHECKPOINT ===
            torch.save({
                "epoch": epoch + 1,
                "model_state_dict": best_model_state,
                "optimizer_state_dict": optimizer.state_dict(),
                "val_f1": best_val_f1,
                "config": {
                    "num_classes": config.num_bias_classes,
                    "input_dim": getattr(model, "input_dim", None),
                }
            }, checkpoint_path)
            print(f"💾 Saved new best checkpoint to {checkpoint_path}")
            print(f"🎉 New best validation F1: {best_val_f1:.4f} at epoch {epoch+1}")
        else:
            early_stopping_counter += 1
            if early_stopping_patience and early_stopping_counter >= early_stopping_patience:
                print(f"📉 Early stopping at epoch {epoch+1} (no improvement for {early_stopping_patience} epochs)")
                break

        # Print epoch summary
        print(f"Epoch {epoch+1}: Train Loss={train_loss:.4f}, Train F1={train_f1:.4f}, "
              f"Val Loss={val_loss:.4f}, Val F1={val_f1:.4f}")
    
    # Restore best model
    model.load_state_dict(best_model_state)
    best_model = deepcopy(model)
    # Save final checkpoint
    torch.save({
        "epoch": best_epoch + 1,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "val_f1": best_val_f1,
    }, "final_model.ckpt")
    print("💾 Saved final checkpoint to final_model.ckpt")
    
    # Final test evaluation
    print("🧪 Running final test evaluation...")
    # Reuse a single forward pass for test logits, then compute metrics from those logits
    test_logits, test_labels, test_pad = collect_logits_labels(model, test_loader, device)
    test_loss = calculate_masked_loss(test_logits.to(device), test_labels.to(device), test_pad.to(device)).item()
    test_f1 = calculate_micro_f1_score(test_logits.to(device), test_labels.to(device), test_pad.to(device))
    
    # Plot training curves
    plot_training_curves(train_losses, val_losses)
    
    print(f"✅ Training completed!")
    print(f"   Best validation F1: {best_val_f1:.4f} at epoch {best_epoch+1}")
    print(f"   Final test F1: {test_f1:.4f}")
    print(f"📉 Total LR drops during training: {lr_drop_count}")
    
    return best_epoch, best_val_f1, best_model, test_f1, test_logits, test_labels, test_pad

def plot_training_curves(train_losses, val_losses):
    """Plot training and validation loss curves."""
    epochs = range(1, len(train_losses) + 1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, train_losses, label="Training Loss", marker="o", linewidth=2)
    plt.plot(epochs, val_losses, label="Validation Loss", marker="s", linewidth=2)
    
    plt.xlabel("Epoch", fontsize=12)
    plt.ylabel("Loss", fontsize=12)
    plt.title("Training and Validation Loss", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

print(f"Dataset sizes - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")

# -----------------------
# Start Training
# -----------------------
print("🚀 Starting model training...")
print(f"Model configuration:")
print(f"  - Input features: {len(get_all_feature_columns())}")
print(f"  - Bias classes: {config.num_bias_classes}")
print(f"  - Embedding dimension: {config.EMBEDDING_DIM}")
print(f"  - Number of layers: {config.NUM_ENCODER_LAYERS}")
print(f"  - Attention heads: {config.NUM_ATTENTION_HEADS}")
print(f"  - Batch size: {config.BATCH_SIZE}")
print(f"  - Learning rate: {config.LEARNING_RATE}")
print(f"  - Max epochs: {config.NUM_EPOCHS}")

# Start training
best_epoch, best_val_f1, best_model, test_f1, test_logits, test_labels, test_pad = train_model_with_validation(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    test_loader=test_loader,
    optimizer=optimizer,
    device=device,
    num_epochs=config.NUM_EPOCHS,
    use_learning_rate_scheduler=True,
    early_stopping_patience=config.EARLY_STOPPING_PATIENCE,
    checkpoint_path="best_model.ckpt"
)

# Final results summary

print("\n" + "="*60)
print("🎯 FINAL RESULTS SUMMARY")
print("="*60)
print(f"Best validation F1: {best_val_f1:.4f} (at epoch {best_epoch+1})")
print(f"Final test F1: {test_f1:.4f}")
print(f"Model parameters: {sum(p.numel() for p in best_model.parameters()):,}")
print("="*60)


# -----------------------
# Pretty printing helpers
# -----------------------
BIAS_EMOJI = {
    "bias_overconfidence": "🚀",
    "bias_confirmation": "🔁",
    "bias_recency": "🕑",
    "bias_disposition": "📉",
    "bias_loss_aversion": "😬",
    "bias_anchoring": "⚓️",
    "bias_sunk_cost": "🕳️",
    "bias_gamblers_fallacy": "🎲",
    "bias_hot_hand": "🔥",
    "bias_house_money": "🏠💵",
    "bias_endowment": "🎁",
}

def _fmt(x, n=4):
    return f"{x:.{n}f}"

def print_per_class_table(report, title_prefix="VAL", threshold_note=None):
    print(f"\n📊 Per-class metrics — {title_prefix}{f' (threshold={threshold_note})' if threshold_note is not None else ''}")
    print("-" * 72)
    print(f"{'Class':28}  P     R     F1    N")
    print("-" * 72)
    for row in report["per_class"]:
        name = row["class"]
        icon = BIAS_EMOJI.get(name, "•")
        p = _fmt(row["precision"], 3)
        r = _fmt(row["recall"], 3)
        f = _fmt(row["f1"], 3)
        n = str(row["support"]).rjust(5)
        print(f"{icon} {name:26}  {p:>5} {r:>5} {f:>6} {n}")
    print("-" * 72)
    print(f"Macro F1: {_fmt(report['macro']['f1'])}   •   Weighted F1: {_fmt(report['weighted']['f1'])}")


def print_best_thresholds(best_thresholds, class_names):
    print("\n🎯 Tuned per-class thresholds (max F1 on VAL):")
    for t, name in zip(best_thresholds, class_names):
        print(f"{BIAS_EMOJI.get(name, '•')} {name}: {_fmt(float(t), 2)}")


def print_ece(label, ece_value):
    print(f"\n📏 ECE {label}: {_fmt(ece_value, 4)}")

# =======================
# Detailed Evaluation
# =======================
print("\n🔎 Running detailed evaluation (per-class metrics, tuned thresholds, calibration)...")

# 1) Collect logits/labels on VAL and TEST
val_logits, val_labels, val_pad = collect_logits_labels(best_model, val_loader, device)
# test_logits, test_labels, test_pad are already collected above and reused here

# 2) Per-class metrics with default threshold 0.45
val_report_default = per_class_metrics(val_logits, val_labels, val_pad, thresholds=None, class_names=config.BIAS_LABEL_COLUMNS)
print_per_class_table(val_report_default, title_prefix="VAL", threshold_note=0.45)

# 3) Tune per-class thresholds on VAL
best_thresholds = tune_thresholds_on_validation(val_logits, val_labels, val_pad, class_names=config.BIAS_LABEL_COLUMNS)
print_best_thresholds(best_thresholds, config.BIAS_LABEL_COLUMNS)

# 4) Evaluate with tuned thresholds on VAL and TEST
val_report_tuned = per_class_metrics(val_logits, val_labels, val_pad, thresholds=best_thresholds, class_names=config.BIAS_LABEL_COLUMNS)
print_per_class_table(val_report_tuned, title_prefix="VAL (tuned)")

test_report_tuned = per_class_metrics(test_logits, test_labels, test_pad, thresholds=best_thresholds, class_names=config.BIAS_LABEL_COLUMNS)
print_per_class_table(test_report_tuned, title_prefix="TEST (tuned)")

# 5) Calibration: ECE before temperature scaling on VAL
cal_val_before = reliability_bins_and_ece(val_logits, val_labels, val_pad, n_bins=15)
print_ece("(VAL before temperature scaling)", cal_val_before["ECE"])

# 6) Fit temperature on VAL and apply to TEST, then compute ECE
temp_scaler = fit_temperature(best_model, val_loader, device)
test_logits_scaled = apply_temperature_scaler(test_logits, temp_scaler, device)
cal_test_after = reliability_bins_and_ece(test_logits_scaled, test_labels, test_pad, n_bins=15)
print_ece("(TEST after temperature scaling)", cal_test_after["ECE"])

