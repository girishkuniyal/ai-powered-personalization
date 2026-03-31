"""
Unified CLI for PersonaLity: BM25, Dense, and SPLADE search.

Entry point for all indexing and evaluation commands.

Commands:
  personapy bm25 index
  personapy bm25 evaluate [--max-queries 5000]
  personapy dense encode [--device cuda|cpu]
  personapy dense evaluate [--max-queries 5000]
  personapy splade encode [--device cuda|cpu] [--splade-model prithivi|qdrant_esci|naver|all]
  personapy splade evaluate [--max-queries 5000]
  personapy hybrid evaluate [--max-queries 5000]
"""

import click

# Import search modules - these modules handle the actual indexing/evaluation
from . import bm25_search
from . import dense_search
from . import splade_search
from . import hybrid_search


@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx):
    """
    PersonaLity: Hybrid Search with Vector Databases.
    
    Unified CLI for indexing and evaluating BM25, Dense, and SPLADE methods.
    """
    ctx.ensure_object(dict)


# =============================================================================
# BM25 COMMANDS - Sparse lexical search
# =============================================================================

@cli.group()
def bm25():
    """BM25 sparse search (~600MB cache)."""
    pass


@bm25.command()
def index():
    """Build BM25 sparse score matrix from products."""
    click.echo("Building BM25 index...")
    bm25_search.main(mode="index")


@bm25.command()
@click.option(
    "--max-queries",
    type=int,
    default=5000,
    help="Maximum number of queries to evaluate (0=all).",
    show_default=True,
)
def evaluate(max_queries):
    """Evaluate BM25 on ESCI dataset."""
    click.echo(f"Evaluating BM25 (max {max_queries} queries)...")
    bm25_search.main(mode="evaluate", max_queries=max_queries)


# =============================================================================
# DENSE COMMANDS - Semantic embeddings (SBERT)
# =============================================================================

@cli.group()
def dense():
    """Dense semantic search (SBERT + FAISS)."""
    pass


@dense.command()
@click.option(
    "--device",
    type=click.Choice(["cuda", "cpu"]),
    default="cuda",
    help="Device for encoding.",
    show_default=True,
)
def encode(device):
    """Encode all products to 384-dim embeddings using SBERT."""
    click.echo(f"Encoding dense embeddings (device: {device})...")
    dense_search.main(mode="encode", device=device)


@dense.command()
@click.option(
    "--max-queries",
    type=int,
    default=5000,
    help="Maximum number of queries to evaluate (0=all).",
    show_default=True,
)
def evaluate(max_queries):
    """Evaluate dense search on ESCI dataset."""
    click.echo(f"Evaluating dense search (max {max_queries} queries)...")
    dense_search.main(mode="evaluate", max_queries=max_queries)


# =============================================================================
# SPLADE COMMANDS - Learned sparse search
# =============================================================================

@cli.group()
def splade():
    """SPLADE learned sparse search (supports 3 variants)."""
    pass


@splade.command()
@click.option(
    "--device",
    type=click.Choice(["cuda", "cpu"]),
    default="cuda",
    help="Device for encoding.",
    show_default=True,
)
@click.option(
    "--splade-model",
    type=click.Choice(["prithivi", "qdrant_esci", "naver", "all"]),
    default="prithivi",
    help="SPLADE model variant",
    show_default=True,
)
def encode(device, splade_model):
    """Encode all products to sparse vectors using SPLADE.
    
    Variants:
    - prithivi: prithivida/Splade_PP_en_v2 (Apache 2.0)
    - qdrant_esci: thierrydamiba/splade-ecommerce-esci (tuned on ESCI)
    - naver: naver/splade-cocondenser-ensembledistil
    - all: Encode all 3 variants sequentially
    """
    click.echo(f"Encoding SPLADE embeddings ({splade_model}, device: {device})...")
    splade_search.main(mode="encode", device=device, splade_model=splade_model)


@splade.command()
@click.option(
    "--max-queries",
    type=int,
    default=5000,
    help="Maximum number of queries to evaluate (0=all).",
    show_default=True,
)
def evaluate(max_queries):
    """Evaluate SPLADE on ESCI dataset."""
    click.echo(f"Evaluating SPLADE (max {max_queries} queries)...")
    splade_search.main(mode="evaluate", max_queries=max_queries)


# =============================================================================
# HYBRID COMMANDS - Fusion methods (RRF, weighted)
# =============================================================================

@cli.group()
def hybrid():
    """Hybrid fusion methods (RRF, weighted fusion)."""
    pass


@hybrid.command()
@click.option(
    "--max-queries",
    type=int,
    default=5000,
    help="Maximum number of queries to evaluate (0=all).",
    show_default=True,
)
def evaluate(max_queries):
    """Evaluate hybrid fusion on ESCI dataset."""
    click.echo(f"Evaluating hybrid search (max {max_queries} queries)...")
    hybrid_search.main(mode="evaluate", max_queries=max_queries)


if __name__ == "__main__":
    cli()
