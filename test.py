import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

import joblib


def build_benchmark(benchmark_directory: Path) -> int:
    temnp_dir = tempfile.TemporaryDirectory()
    benchmark_name = benchmark_directory.stem
    benchmark_name_c = benchmark_name.replace("-", "_")
    shutil.copy(benchmark_directory / (benchmark_name + ".cpp"), temnp_dir.name)

    print(f"Building {benchmark_name}: {temnp_dir}")

    tcl_script = temnp_dir.name + "/build.tcl"
    with open(tcl_script, "w") as f:
        f.write(f"open_project -reset test_proj_{benchmark_name}\n")
        f.write(f"add_files {(benchmark_name + '.cpp')}\n")
        f.write("open_solution solution1\n")
        f.write(f"set_top kernel_{benchmark_name_c}\n")
        f.write("set_part {xc7z020clg484-1}\n")
        f.write("create_clock -period 10 -name default\n")
        f.write("csynth_design\n")
        f.write("exit\n")

    p = subprocess.run(
        ["vitis_hls", "-f", tcl_script],
        cwd=temnp_dir.name,
        text=True,
        capture_output=True,
    )
    print(f"{benchmark_name}: {p.returncode}")
    return p.returncode


def main(args):
    benchmarks_directory = args.benchmarks_directory
    benchmarks = list(benchmarks_directory.glob("*"))
    return_codes = joblib.Parallel(n_jobs=32, backend="multiprocessing")(
        joblib.delayed(build_benchmark)(benchmark) for benchmark in benchmarks
    )
    for return_code, benchmark in zip(return_codes, benchmarks):
        if return_code != 0:
            print(f"Failed to build benchmark {benchmark.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "benchmarks_directory", type=Path, nargs="?", default=Path("./hls-polybench/")
    )
    args = parser.parse_args()
    main(args)
