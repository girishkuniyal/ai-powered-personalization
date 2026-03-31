#PersonaLity: Complete User Guide

A hybrid search package supporting BM25 (sparse lexical), Dense (semantic), SPLADE (learned sparse), and Hybrid (fusion) search methods for e-commerce datasets.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [CLI Commands & Parameters](#cli-commands--parameters)
5. [Usage Examples](#usage-examples)
6. [Configuration Reference](#configuration-reference)
7. [Programmatic API](#programmatic-api)

---

## Quick Start

```bash
# 1. Install package
pip install -e .

# 2. Copy default config (optional)
cp config.yaml.default config.yaml

# 3. Run commands
personapy bm25 index
personapy dense encode --device cuda
personapy splade encode --splade-model qdrant_esci
personapy hybrid evaluate --max-queries 1000
```

---

## Installation

### As CLI Package (Recommended for users)

```bash
# Install in development mode from project root
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"

# Verify installation
personapy --version
```

After installation, the `personapy` command is available globally.

### As Library (For developers)

```python
from personapy.config import BM25Config, DenseConfig
from personapy import bm25_search, dense_search
```

---

## Configuration

### Configuration File (config.yaml)

PersonaLity supports optional YAML configuration files for batch configuration without CLI arguments.

**Setup:**
```bash
# Copy default config to project root
cp config.yaml.default config.yaml

# Edit as needed
nano config.yaml
```

**If no config.yaml exists**: All defaults from `config.yaml.default` are used.

**Priority order** (highest to lowest):
1. CLI arguments (`--device cuda`)
2. config.yaml file (if exists in project root)
3. Hardcoded defaults in `config.py`

### Configuration Sections

#### ✅ Dataset Section
```yaml
dataset:
  data_dir: "Dataset"
  locale: "us"                    # us, uk, de, es, fr, it, jp
  max_queries: 5000               # 0 = all (~97K)
  max_products: 0                 # 0 = all (~1.2M)
```

#### ✅ BM25 Section
```yaml
bm25:
  enabled: true
  method: "lucene"                # lucene, robertson, atire, bm25l, bm25+
  k1: 1.5                          # 1.2-2.0 (higher = more term freq weight)
  b: 0.75                          # 0.5-0.75 (doc length normalization)
  cache_dir: "cache/bm25"
```

#### ✅ Dense Section
```yaml
dense:
  enabled: true
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 64                   # Reduce if OOM
  max_seq_length: 128
  embedding_dim: 384               # 384 for MiniLM, 768 for MPNET
  normalize_embeddings: true
  faiss_index_type: "IndexFlatIP"
  cache_dir: "cache/embeddings"
```

**Dense Model Options:**
- `all-MiniLM-L6-v2` (384-dim, fast) — recommended for speed
- `all-mpnet-base-v2` (768-dim, better quality)
- `all-distilroberta-v1` (384-dim, balanced)

#### ✅ SPLADE Section
```yaml
splade:
  enabled: true
  default_model: "prithivi"        # prithivi, qdrant_esci, naver
  models:
    prithivi:
      enabled: true
      model_name: "prithivida/Splade_PP_en_v2"
    qdrant_esci:
      enabled: true
      model_name: "thierrydamiba/splade-ecommerce-esci"
    naver:
      enabled: true
      model_name: "naver/splade-cocondenser-ensembledistil"
```

**SPLADE Variant Guide:**
- **Prithivi**: General purpose, Apache 2.0 license
- **Qdrant ESCI**: Tuned on Amazon ESCI (best for e-commerce) ⭐
- **Naver**: Ensemble distilled (balanced quality/speed)

#### ✅ Hybrid Section
```yaml
hybrid:
  rrf_k: 60                        # 40-100 (higher = smoother)
  fusion_method: "weighted"        # rrf, weighted
  weights:
    bm25: 0.3                      # Adjust per use case
    splade: 0.4
    dense: 0.3
  retrieval_top_k: 100
```

#### ✅ Evaluation Section
```yaml
evaluation:
  ndcg_k: [10, 20, 50]
  gains:
    E: 3                           # Exact match
    S: 2                           # Substitute
    C: 1                           # Complement
    I: 0                           # Irrelevant
```

#### ✅ Runtime Section
```yaml
runtime:
  device: "cuda"                   # cuda, cpu
  num_workers: 4
  seed: 42
  log_level: "INFO"                # DEBUG, INFO, WARNING, ERROR
```

---

## CLI Commands & Parameters

### Root Command

```bash
personapy --version               # Show version
personapy --help                  # Show all commands
```

---

### BM25 Commands

#### Build Index
```bash
personapy bm25 index

# Parameters:
#   (none - uses config.yaml or defaults)

# Example:
personapy bm25 index
```

**Output**: BM25 index cached in `cache/bm25/` (~600MB)

#### Evaluate
```bash
personapy bm25 evaluate [OPTIONS]

# Options:
#   --max-queries INTEGER    Max queries to evaluate (0=all ~97K)
#                           Default: 5000

# Examples:
personapy bm25 evaluate
personapy bm25 evaluate --max-queries 1000
personapy bm25 evaluate --max-queries 0     # All queries
```

**Output**: NDCG@10/20/50 metrics, saved to `results/`

---

### Dense Commands

#### Encode Products
```bash
personapy dense encode [OPTIONS]

# Options:
#   --device [cuda|cpu]      Device for encoding
#                           Default: cuda
#   --batch-size INTEGER     Batch size (reduce if OOM)
#                           Default: 64

# Examples:
personapy dense encode                      # GPU, batch=64
personapy dense encode --device cpu         # CPU
personapy dense encode --device cuda        # Explicit GPU
```

**Output**: Dense embeddings cached in `cache/embeddings/dense_product_embeddings.npz` (~4-6GB)

#### Evaluate
```bash
personapy dense evaluate [OPTIONS]

# Options:
#   --max-queries INTEGER    Max queries to evaluate
#                           Default: 5000

# Examples:
personapy dense evaluate
personapy dense evaluate --max-queries 2000
```

**Output**: NDCG@10/20/50 metrics

---

### SPLADE Commands

#### Encode Products
```bash
personapy splade encode [OPTIONS]

# Options:
#   --device [cuda|cpu]              Device for encoding
#                                   Default: cuda
#   --splade-model [prithivi|qdrant_esci|naver|all]
#                                   Model variant to use
#                                   Default: prithivi
#   --batch-size INTEGER             Batch size
#                                   Default: 32

# Examples:
personapy splade encode                                   # Default (Prithivi)
personapy splade encode --splade-model qdrant_esci       # E-commerce tuned ⭐
personapy splade encode --splade-model naver
personapy splade encode --splade-model all               # Encode all 3 variants
personapy splade encode --device cpu
personapy splade encode --splade-model qdrant_esci --device cuda
```

**Output**: Sparse vectors cached in `cache/splade/{variant}/` (~200-400MB each)

#### Evaluate
```bash
personapy splade evaluate [OPTIONS]

# Options:
#   --max-queries INTEGER    Max queries to evaluate
#                           Default: 5000

# Examples:
personapy splade evaluate
personapy splade evaluate --max-queries 3000
```

**Output**: NDCG@10/20/50 metrics per variant

---

### Hybrid Commands

#### Evaluate Fusion
```bash
personapy hybrid evaluate [OPTIONS]

# Options:
#   --max-queries INTEGER    Max queries to evaluate
#                           Default: 5000

# Examples:
personapy hybrid evaluate
personapy hybrid evaluate --max-queries 5000
```

**Output**: Compares all methods + fusion result (RRF + weighted)

**Requirements**:
- BM25 index must exist (`personapy bm25 index`)
- Dense embeddings must exist (`personapy dense encode`)
- SPLADE embeddings must exist (`personapy splade encode`)

---

## Usage Examples

### Example 1: Full E-commerce Search Pipeline

```bash
# Setup default config
cp config.yaml.default config.yaml

# Build all indexes
personapy bm25 index                           # Build BM25
personapy dense encode --device cuda           # Encode dense
personapy splade encode --splade-model qdrant_esci --device cuda  # SPLADE (ESCI-tuned)

# Evaluate each method
personapy bm25 evaluate
personapy dense evaluate
personapy splade evaluate

# Evaluate hybrid fusion
personapy hybrid evaluate
```

### Example 2: Quick Testing with Limited Queries

```bash
# Use only 100 queries for fast testing
personapy bm25 evaluate --max-queries 100
personapy dense evaluate --max-queries 100
personapy splade evaluate --max-queries 100
personapy hybrid evaluate --max-queries 100
```

### Example 3: CPU-Only Setup (No GPU)

```bash
# All encoding on CPU
personapy dense encode --device cpu
personapy splade encode --device cpu --splade-model prithivi

# Evaluate
personapy hybrid evaluate
```

### Example 4: Compare All SPLADE Variants

```bash
# Encode all 3 variants sequentially
personapy splade encode --splade-model all --device cuda

# Evaluate (all 3 will be compared)
personapy splade evaluate --max-queries 5000
```

### Example 5: Custom Configuration

Create `config.yaml`:
```yaml
dataset:
  max_queries: 2000
  max_products: 500000

dense:
  batch_size: 128
  model_name: "sentence-transformers/all-mpnet-base-v2"

splade:
  default_model: "qdrant_esci"

hybrid:
  weights:
    bm25: 0.2
    splade: 0.5
    dense: 0.3

runtime:
  device: "cuda"
```

Then run:
```bash
personapy bm25 index          # Uses config.yaml
personapy dense encode
personapy splade encode
personapy hybrid evaluate
```

---

## Configuration Reference

### Dataset

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| data_dir | str | "Dataset" | Any path | Path to dataset root |
| locale | str | "us" | us, uk, de, es, fr, it, jp | Dataset locale |
| max_queries | int | 5000 | 0-97000 | 0 = all queries |
| max_products | int | 0 | 0-1200000 | 0 = all products |
| random_seed | int | 42 | Any int | Reproducibility |

### BM25

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| enabled | bool | true | true/false | Enable BM25 |
| method | str | "lucene" | lucene, robertson, atire, bm25l, bm25+ | BM25 variant |
| k1 | float | 1.5 | 1.0-3.0 | Term frequency weight |
| b | float | 0.75 | 0.0-1.0 | Doc length normalization |
| cache_dir | str | "cache/bm25" | Any path | Cache location |

### Dense (SBERT)

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| enabled | bool | true | true/false | Enable dense search |
| model_name | str | all-MiniLM-L6-v2 | HF model ID | Sentence-transformers model |
| batch_size | int | 64 | 1-1024 | Batch size (reduce if OOM) |
| max_seq_length | int | 128 | 64-512 | Max input length |
| embedding_dim | int | 384 | 192-768 | Output dimension |
| normalize_embeddings | bool | true | true/false | L2 normalization |
| faiss_index_type | str | IndexFlatIP | IndexFlatIP, IndexIVFFlat | FAISS index type |

### SPLADE

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| enabled | bool | true | true/false | Enable SPLADE |
| default_model | str | "prithivi" | prithivi, qdrant_esci, naver | Default variant |
| batch_size | int | 32 | 1-256 | Batch size |
| vocab_size | int | 30522 | 30522 | BERT vocab size |
| models.*.enabled | bool | true | true/false | Enable variant |

### Hybrid

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| rrf_k | int | 60 | 40-100 | RRF smoothing |
| fusion_method | str | "weighted" | rrf, weighted | Fusion algorithm |
| weights.bm25 | float | 0.3 | 0.0-1.0 | BM25 weight |
| weights.splade | float | 0.4 | 0.0-1.0 | SPLADE weight |
| weights.dense | float | 0.3 | 0.0-1.0 | Dense weight |

### Evaluation

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| ndcg_k | list | [10,20,50] | Any ints | NDCG evaluation points |
| gains.E | int | 3 | 0-3 | Exact match gain |
| gains.S | int | 2 | 0-3 | Substitute gain |
| gains.C | int | 1 | 0-3 | Complement gain |
| gains.I | int | 0 | 0 | Irrelevant gain |

### Runtime

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| device | str | "cuda" | cuda, cpu | Compute device |
| num_workers | int | 4 | 0-16 | Data loading workers |
| seed | int | 42 | Any int | Random seed |
| log_level | str | "INFO" | DEBUG, INFO, WARNING, ERROR | Log verbosity |

---

## Programmatic API

### Using Configs

```python
from personapy.config import BM25Config, DenseConfig, SPLADEConfig
from personapy.config_utils import print_config, merge_configs, get_splade_config

# Load default configs
bm25_cfg = BM25Config()
dense_cfg = DenseConfig()
splade_cfg = SPLADEConfig()

# Print configuration
print_config(dense_cfg, "Dense Settings")

# Override specific fields
custom_cfg = merge_configs(dense_cfg, {"batch_size": 128})

# Get SPLADE variant
qdrant_cfg = get_splade_config("qdrant_esci")
```

### Direct Module Usage

```python
from personapy import bm25_search, dense_search, splade_search

# Build BM25 index
bm25_search.main(mode="index")

# Encode dense embeddings
dense_search.main(mode="encode", device="cuda")

# Encode SPLADE with specific variant
splade_search.main(mode="encode", device="cuda", splade_model="qdrant_esci")

# Evaluate
bm25_search.main(mode="evaluate", max_queries=5000)
```

---

## Troubleshooting

### Out of Memory (OOM) Errors

**Dense encoding**: Reduce batch size
```bash
personapy dense encode --device cuda --batch-size 32
```

**SPLADE encoding**: Use CPU
```bash
personapy splade encode --device cpu --splade-model prithivi
```

### Missing Cache Files

If you see "index not found" errors, rebuild:
```bash
personapy bm25 index
personapy dense encode --device cuda
personapy splade encode --splade-model qdrant_esci
```

### Slow Evaluation

Use `--max-queries` to subset:
```bash
personapy hybrid evaluate --max-queries 100
```

### Choose Right SPLADE Model for E-commerce

Use Qdrant ESCI variant (tuned on Amazon ESCI dataset):
```bash
personapy splade encode --splade-model qdrant_esci --device cuda
```

---

## Performance Notes

| Method | Speed | Accuracy | Memory | Cache Size |
|--------|-------|----------|--------|------------|
| BM25 | ⚡⚡⚡ Fast | 📊 Medium | 💾 Low | ~600MB |
| Dense | ⚡ Medium | 📊📊 Good | 💾💾 Medium | ~4-6GB |
| SPLADE | ⚡ Medium | 📊📊📊 Best | 💾 Medium | ~200-400MB |
| Hybrid | ⚡ Medium | 📊📊📊 Best | 💾💾 Medium | ~5-7GB |

---

## File Structure

```
personapy/
├── cli.py                       # CLI entry point
├── config.py                    # Configuration dataclasses
├── config_utils.py              # Config helpers
├── bm25_search.py              # BM25 implementation
├── dense_search.py             # Dense search implementation
├── splade_search.py            # SPLADE implementation
├── hybrid_search.py            # Hybrid fusion implementation
├── data_loader.py              # Dataset loading
└── evaluate.py                 # Evaluation metrics

cache/
├── bm25/                       # BM25 index
├── embeddings/                 # Dense embeddings
└── splade/                     # SPLADE vectors
   ├── prithivi/
   ├── qdrant_esci/
   └── naver/

results/
├── hybrid_search_results.json  # Results
└── method_comparison.csv       # Comparison

config.yaml.default             # Default configuration template
config.yaml                     # (Optional) Your configuration
```

---

**For more details, see individual module docstrings or raise an issue!**
