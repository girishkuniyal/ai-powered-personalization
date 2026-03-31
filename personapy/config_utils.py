"""
Configuration utilities for PersonaLity.

Provides:
- Loading/saving configs from YAML/JSON
- Config merging and validation
- Pretty printing
- Getting predefined SPLADE variants
"""

from dataclasses import asdict, is_dataclass, fields
from pathlib import Path
from typing import Any, Type, TypeVar, Dict
import json

# Use relative imports
from .config import (
    ESCIDataConfig,
    BM25Config,
    SPLADEConfig,
    DenseConfig,
    HybridConfig,
    EvalConfig,
    SPLADE_MODELS,
)

T = TypeVar("T")


def load_yaml_config(config_path: Path, config_class: Type[T]) -> T:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    return config_class(**config_dict)


def load_json_config(config_path: Path, config_class: Type[T]) -> T:
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    return config_class(**config_dict)


def save_config_yaml(config: Any, output_path: Path) -> None:
    """Save configuration to YAML file."""
    config_dict = asdict(config) if hasattr(config, '__dataclass_fields__') else config
    with open(output_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False)


def save_config_json(config: Any, output_path: Path) -> None:
    """Save configuration to JSON file."""
    config_dict = asdict(config) if hasattr(config, '__dataclass_fields__') else config
    with open(output_path, 'w') as f:
        json.dump(config_dict, f, indent=2)


def get_splade_config(variant: str = "prithivi") -> SPLADEConfig:
    """Get SPLADE configuration by variant name."""
    if variant not in SPLADE_MODELS:
        raise ValueError(
            f"Unknown SPLADE variant: {variant}. "
            f"Available: {list(SPLADE_MODELS.keys())}"
        )
    return SPLADE_MODELS[variant]


def print_config(cfg: Any, name: str = None) -> None:
    """Pretty-print a configuration object."""
    if name is None:
        name = cfg.__class__.__name__

    print(f"\n{'='*60}")
    print(f"Configuration: {name}")
    print(f"{'='*60}")

    for field_obj in fields(cfg):
        value = getattr(cfg, field_obj.name)
        if isinstance(value, Path):
            value = str(value)
        elif isinstance(value, dict):
            value = json.dumps(value, indent=2)

        print(f"  {field_obj.name:20s} = {value}")

    print(f"{'='*60}\n")


def merge_configs(base_cfg: T, overrides: Dict[str, Any]) -> T:
    """
    Merge override values into a config dataclass.

    Args:
        base_cfg: Base configuration object
        overrides: Dictionary of field names to values

    Returns:
        New config instance with merged values

    Example:
        cfg = BM25Config()
        cfg = merge_configs(cfg, {"k1": 2.0, "b": 0.5})
    """
    if not is_dataclass(base_cfg):
        raise ValueError(f"{base_cfg} is not a dataclass")

    cfg_dict = asdict(base_cfg)
    cfg_dict.update(overrides)
    return base_cfg.__class__(**cfg_dict)


def config_to_dict(cfg: Any) -> Dict[str, Any]:
    """Convert dataclass config to dictionary."""
    if not is_dataclass(cfg):
        raise ValueError(f"{cfg} is not a dataclass")
    return asdict(cfg)


def config_to_json(cfg: Any, indent: int = 2) -> str:
    """Convert dataclass config to JSON string."""

    def _serialize(obj):
        if isinstance(obj, Path):
            return str(obj)
        return obj

    data = asdict(cfg)
    return json.dumps(
        data,
        default=_serialize,
        indent=indent,
    )
