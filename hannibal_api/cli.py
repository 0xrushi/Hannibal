from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from .io import load_plan_file, write_plan_file


def normalize_plan_file(in_path: Path, out_path: Optional[Path] = None) -> Path:
    """Validate and rewrite a plan file deterministically.

    If out_path is None, rewrites in place.
    Returns the written path.
    """

    plan = load_plan_file(in_path)
    out_path = out_path or in_path
    write_plan_file(out_path, plan)
    return out_path


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hannibal-plan", add_help=True)
    p.add_argument("in_path", help="Input plan JSON path")
    p.add_argument(
        "--out",
        dest="out_path",
        default=None,
        help="Output plan JSON path (default: rewrite in place)",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_argparser().parse_args(argv)
    in_path = Path(args.in_path)
    out_path = Path(args.out_path) if args.out_path else None
    normalize_plan_file(in_path, out_path)
    return 0
