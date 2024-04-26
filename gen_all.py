import shutil
from argparse import Namespace
from pathlib import Path

from process import main

DIR_SCRIPT = Path(__file__).parent
DIR_DIST = DIR_SCRIPT / "dist"
if DIR_DIST.exists():
    shutil.rmtree(DIR_DIST)
DIR_DIST.mkdir(parents=True)

FP_BENCHMARK_DIST = DIR_SCRIPT / "polybench-c-4.2.1-beta.tar.gz"

SUFFIXES = (
    "MINI",
    "SMALL",
    "MEDIUM",
    # "DEFAULT",
    # "LARGE",
    # "EXTRALARGE",
)

OUTPUT_NAME = "hls_polybench"

for suffix in SUFFIXES:
    suffix_lowercase = suffix.lower()

    args = Namespace()
    args.jobs = 32
    args.dataset_size = suffix
    args.output_suffix = f"__{suffix_lowercase}"
    args.benchmark_distribution = FP_BENCHMARK_DIST
    args.output_directory = DIR_DIST / OUTPUT_NAME
    args.output_file = DIR_DIST / OUTPUT_NAME

    main(args)

    # add gitignore in the output directories
    Path((DIR_DIST / f"{OUTPUT_NAME}{args.output_suffix}") / ".gitignore").write_text(
        "*"
    )
