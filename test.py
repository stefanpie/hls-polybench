import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

import joblib


def build_benchmark(benchmark_directory: Path) -> int:
    temp_dir = tempfile.TemporaryDirectory()
    benchmark_name = benchmark_directory.stem
    benchmark_name_c = benchmark_name.replace("-", "_")
    shutil.copy(benchmark_directory / (benchmark_name + ".cpp"), temp_dir.name)

    print(f"Building {benchmark_name}: {temp_dir}")

    tcl_script = temp_dir.name + "/build.tcl"
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
        cwd=temp_dir.name,
        text=True,
        capture_output=True,
    )
    print(f"{benchmark_name}: {p.returncode}")
    return p.returncode


def get_vitis_hls_include_dir() -> Path:
    vitis_hls_bin_path = shutil.which("vitis_hls")
    if vitis_hls_bin_path is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path)
    vitis_hls_include_dir = vitis_hls_bin_path.parent.parent / "include"
    return vitis_hls_include_dir


def get_vitis_hls_clang_pp_path() -> Path:
    vitis_hls_bin_path = shutil.which("vitis_hls")
    if vitis_hls_bin_path is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path)
    vitis_hls_clang_pp_path = (
        vitis_hls_bin_path.parent.parent
        / "lnx64"
        / "tools"
        / "clang-3.9"
        / "bin"
        / "clang++"
    )
    return vitis_hls_clang_pp_path


def get_vitis_hls_install_dir() -> Path:
    vitis_hls_bin_path = shutil.which("vitis_hls")
    if vitis_hls_bin_path is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path)
    vitis_hls_install_dir = vitis_hls_bin_path.parent.parent
    return vitis_hls_install_dir


def compile_benchmark(
    benchmark_directory: Path,
    error_dir: Path,
    output_dir: Path,
    temp_dir_overide: Path | None = None,
) -> tuple[int, int]:
    benchmark_name = benchmark_directory.stem

    if temp_dir_overide is None:
        temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = Path(temp_dir.name)
    else:
        temp_dir_path = temp_dir_overide / benchmark_name
        temp_dir_path.mkdir(exist_ok=True, parents=True)

    all_files = list(benchmark_directory.glob("*"))
    for file in all_files:
        shutil.copy(file, temp_dir_path)

    # print(f"Compiling {benchmark_name}: {temp_dir_path}")

    vitis_hls_include_dir = get_vitis_hls_include_dir()
    # print(f"Using vitis_hls include dir {vitis_hls_include_dir}")
    clang_bin_path = get_vitis_hls_clang_pp_path()
    # print(f"Using vitis_hls clang++ from {clang_bin_path}")
    vitis_hls_install_dir = get_vitis_hls_install_dir()
    # print(f"Using vitis_hls install dir {vitis_hls_install_dir}")

    p_compile = subprocess.run(
        [
            str(clang_bin_path),
            f"./{benchmark_name}_tb.cpp",
            f"./{benchmark_name}.cpp",
            "-o",
            benchmark_name,
            "-std=c++14",
            "-O3",
            "-g",
            "-fPIC",
            "-fPIE",
            "-lm",
            "-Wl,--sysroot=/",
            # f'-L"{vitis_hls_install_dir}/lnx64/lib/csim" -lhlsmc++-CLANG39 -Wl,-rpath,"{vitis_hls_install_dir}/lnx64/lib/csim" -Wl,-rpath,"{vitis_hls_install_dir}/lnx64/tools/fpo_v7_1"',
            f"-I{vitis_hls_include_dir}",
            f"-I{vitis_hls_include_dir / 'etc'}",
            f"-I{vitis_hls_include_dir / 'utils'}",
        ],
        cwd=Path(temp_dir_path),
        text=True,
        capture_output=True,
    )

    command_compile = " ".join(p_compile.args)
    (temp_dir_path / "compile_command.txt").write_text(command_compile)

    if p_compile.returncode != 0:
        error_dir.mkdir(exist_ok=True)
        error_log_fp = error_dir / f"{benchmark_name}_compile_error.log"
        error_log_fp.write_text(p_compile.stdout + "\n" + p_compile.stderr)

    print(f"COMPILE : {benchmark_name}: {p_compile.returncode}")

    # run the compiled binary
    p_run = subprocess.run(
        [f"./{benchmark_name}"],
        cwd=Path(temp_dir_path),
        text=True,
        capture_output=True,
    )

    if p_run.returncode == 0:
        output_dir.mkdir(exist_ok=True)
        output_tb_data = output_dir / f"{benchmark_name}_tb_data_test.txt"
        output_tb_data.write_text(p_run.stderr)
    else:
        error_dir.mkdir(exist_ok=True)
        error_log_fp = error_dir / f"{benchmark_name}_run_error.log"
        error_log_fp.write_text(p_run.stdout + "\n" + p_run.stderr)

    print(f"RUN : {benchmark_name}: {p_run.returncode}")

    return p_compile.returncode, p_run.returncode


def main(args):
    n_jobs = args.jobs

    error_dir = Path("./errors")
    if error_dir.exists():
        shutil.rmtree(error_dir)

    output_dir = Path("./output")
    if output_dir.exists():
        shutil.rmtree(output_dir)

    temp_dir_overide = Path("./test_temp")
    if temp_dir_overide.exists():
        shutil.rmtree(temp_dir_overide)

    benchmarks_to_skip = [
        "deriche",
    ]

    benchmarks_directory = args.benchmarks_directory
    benchmarks = sorted(list(benchmarks_directory.glob("*")))

    benchmarks_to_test = [
        benchmark
        for benchmark in benchmarks
        if benchmark.stem not in benchmarks_to_skip
    ]

    # return_codes = joblib.Parallel(n_jobs=32, backend="multiprocessing")(
    #     joblib.delayed(build_benchmark)(benchmark) for benchmark in benchmarks
    # )
    # for return_code, benchmark in zip(return_codes, benchmarks):
    #     if return_code != 0:
    #         print(f"Failed to build benchmark {benchmark.name}")

    return_codes = joblib.Parallel(n_jobs=n_jobs, backend="multiprocessing")(
        joblib.delayed(compile_benchmark)(
            benchmark, error_dir, output_dir, temp_dir_overide=temp_dir_overide
        )
        for benchmark in benchmarks_to_test
    )

    return_codes_compile, return_codes_run = zip(*return_codes)
    print(f"Compile return codes: {return_codes_compile}")
    print(f"Run return codes: {return_codes_run}")

    # for return_code, benchmark in zip(return_codes_compile, benchmarks_to_test):
    #     if return_code != 0:
    #         print(f"Failed to compile benchmark {benchmark.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "benchmarks_directory", type=Path, nargs="?", default=Path("./hls-polybench/")
    )
    parser.add_argument("-j", "--jobs", type=int, default=16)
    args = parser.parse_args()
    main(args)
