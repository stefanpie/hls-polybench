import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import joblib
import numpy as np


def hls_synth_benchmark(
    benchmark_directory: Path, temp_dir_overide: Path | None = None
) -> int:
    benchmark_name = benchmark_directory.stem

    if temp_dir_overide is None:
        temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = Path(temp_dir.name)
    else:
        temp_dir_path = temp_dir_overide / benchmark_name
        temp_dir_path.mkdir(exist_ok=True, parents=True)

    benchmark_name = benchmark_directory.stem
    benchmark_name_c = benchmark_name.replace("-", "_")

    all_files = list(benchmark_directory.glob("*"))
    for file in all_files:
        shutil.copy(file, temp_dir_path)

    print(f"Running HLS Synthesis : {benchmark_name} : {temp_dir_path}")

    tcl_script = temp_dir_path / "build.tcl"
    tcl_script_txt = ""
    tcl_script_txt += f"open_project -reset test_proj_{benchmark_name}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '.cpp')}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '.h')}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '_tb.cpp')} -tb\n"
    tcl_script_txt += "open_solution solution1\n"
    tcl_script_txt += f"set_top kernel_{benchmark_name_c}\n"
    tcl_script_txt += "set_part {xc7z020clg484-1}\n"
    tcl_script_txt += "create_clock -period 10 -name default\n"
    tcl_script_txt += "csynth_design\n"
    tcl_script_txt += "exit\n"
    tcl_script.write_text(tcl_script_txt)

    p = subprocess.run(
        ["vitis_hls", "-f", tcl_script.resolve()],
        cwd=temp_dir_path,
        text=True,
        capture_output=True,
    )
    print(f"{benchmark_name}: {p.returncode}")

    if p.returncode == 0:
        csynth_rpt_fp = (
            temp_dir_path
            / f"test_proj_{benchmark_name}"
            / "solution1"
            / "syn"
            / "report"
            / "csynth.rpt"
        )
        shutil.copy(csynth_rpt_fp, temp_dir_path / "csynth.rpt")

    return p.returncode


def get_vitis_hls_include_dir() -> Path:
    vitis_hls_bin_path_str = shutil.which("vitis_hls")
    if vitis_hls_bin_path_str is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path_str)
    vitis_hls_include_dir = vitis_hls_bin_path.parent.parent / "include"
    return vitis_hls_include_dir


def get_vitis_hls_clang_pp_path() -> Path:
    vitis_hls_bin_path_str = shutil.which("vitis_hls")
    if vitis_hls_bin_path_str is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path_str)
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
    vitis_hls_bin_path_str = shutil.which("vitis_hls")
    if vitis_hls_bin_path_str is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path_str)
    vitis_hls_install_dir = vitis_hls_bin_path.parent.parent
    return vitis_hls_install_dir


RE_SINGLE_ARRAY = re.compile(r"begin dump: ([A-Za-z]+)((?:.|\s)*?)end   dump: \w+")


def extract_array_dump_data(data_fp: Path):
    raw_txt = data_fp.read_text()

    data: dict[str, dict] = {}

    array_matches = RE_SINGLE_ARRAY.finditer(raw_txt)
    for match in array_matches:
        array_data = {}
        array_name = match.group(1)
        array_str = match.group(2)
        array_str_flat = array_str.replace("\n", " ").strip()
        array = np.fromstring(array_str_flat, sep=" ")
        array_data["name"] = array_name
        array_data["shape"] = array.shape
        array_data["data"] = array
        data[array_name] = array_data

    return data


def compile_benchmark(
    benchmark_directory: Path,
    error_dir: Path,
    output_dir: Path,
    temp_dir_overide: Path | None = None,
) -> tuple[int, int | None, dict | None]:
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

    makefile_text = ""
    makefile_text += f"CC={clang_bin_path}\n"
    makefile_text += f"CFLAGS=-std=c++14 -O3 -g -fPIC -fPIE -lm -Wl,--sysroot=/ -I{vitis_hls_include_dir} -I{vitis_hls_include_dir / 'etc'} -I{vitis_hls_include_dir / 'utils'}\n"
    makefile_text += f"all: {benchmark_name}\n"
    makefile_text += f"{benchmark_name}: {benchmark_name}_tb.cpp {benchmark_name}.cpp\n"
    makefile_text += "\t$(CC) $^ -o $@ $(CFLAGS)\n"
    makefile_text += f"run: {benchmark_name}\n"
    makefile_text += f"\t./{benchmark_name}\n"

    (temp_dir_path / "Makefile").write_text(makefile_text)

    if p_compile.returncode != 0:
        error_dir.mkdir(exist_ok=True)
        error_log_fp = error_dir / f"{benchmark_name}_compile_error.log"
        error_log_fp.write_text(p_compile.stdout + "\n" + p_compile.stderr)

    print(f"COMPILE : {benchmark_name}: {p_compile.returncode}")

    if p_compile.returncode != 0:
        return p_compile.returncode, None, None

    # run the compiled binary
    p_run = subprocess.run(
        [f"./{benchmark_name}"],
        cwd=Path(temp_dir_path),
        text=True,
        capture_output=True,
    )

    if p_run.returncode == 0:
        temp_dir_path.mkdir(exist_ok=True)
        output_tb_data = temp_dir_path / "tb_data_hls.txt"
        output_tb_data.write_text(p_run.stderr)
    else:
        error_dir.mkdir(exist_ok=True)
        error_log_fp = error_dir / f"{benchmark_name}_run_error.log"
        error_log_fp.write_text(p_run.stdout + "\n" + p_run.stderr)

    print(f"RUN : {benchmark_name}: {p_run.returncode}")

    if p_run.returncode != 0:
        return p_compile.returncode, p_run.returncode, None

    # compute the MSE of each output array

    data_golden = extract_array_dump_data(benchmark_directory / "tb_data.txt")
    data_hls = extract_array_dump_data(temp_dir_path / "tb_data_hls.txt")

    # assert that all the array keys are the same
    data_golden_keys = sorted(data_golden.keys())
    data_hls_keys = sorted(data_hls.keys())
    if data_golden_keys != data_hls_keys:
        print(f"ERROR: {benchmark_name}: Array data keys do not match")
        print(f"Golden: {data_golden_keys}")
        print(f"HLS: {data_hls_keys}")
        raise RuntimeError("Array data keys do not match")

    # assert that all the array shapes are the same
    for key in data_golden_keys:
        if data_golden[key]["shape"] != data_hls[key]["shape"]:
            print(f"ERROR: {benchmark_name}: Array shape mismatch")
            print(f"Golden: {data_golden[key]['shape']}")
            print(f"HLS: {data_hls[key]['shape']}")
            raise RuntimeError("Array shape mismatch")

    data_error = {}
    for key in data_golden_keys:
        golden_data = data_golden[key]["data"]
        hls_data = data_hls[key]["data"]
        mae = np.abs(golden_data - hls_data).mean()
        mse = np.square(golden_data - hls_data).mean()
        rmse = np.sqrt(mse)

        data_error[key] = {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
        }

    return p_compile.returncode, p_run.returncode, data_error


def main(args):
    n_jobs = args.jobs

    report_flag = args.report
    report_file = args.report_file

    error_dir = Path("./errors")
    if error_dir.exists():
        shutil.rmtree(error_dir)

    output_dir = Path("./output")
    if output_dir.exists():
        shutil.rmtree(output_dir)

    temp_dir_compile = Path("./test_temp_compile")
    if temp_dir_compile.exists():
        shutil.rmtree(temp_dir_compile)

    temp_dir_synth = Path("./test_temp_synth")
    if temp_dir_synth.exists():
        shutil.rmtree(temp_dir_synth)

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

    ### HLS Synthesis ###
    return_data_hls = joblib.Parallel(n_jobs=n_jobs, backend="multiprocessing")(
        joblib.delayed(hls_synth_benchmark)(benchmark, temp_dir_overide=temp_dir_synth)
        for benchmark in benchmarks_to_test
    )
    return_codes_hls_synthesis = return_data_hls
    for return_code, benchmark in zip(return_codes_hls_synthesis, benchmarks_to_test):
        if return_code != 0:
            print(f"Failed to synthesize benchmark {benchmark.name}")

    ### HLS Compile and Run ###
    return_data = joblib.Parallel(n_jobs=n_jobs, backend="multiprocessing")(
        joblib.delayed(compile_benchmark)(
            benchmark, error_dir, output_dir, temp_dir_overide=temp_dir_compile
        )
        for benchmark in benchmarks_to_test
    )

    return_codes_compile, return_codes_run, data_error = zip(*return_data)

    if report_flag:
        report_text = ""
        report_text += "Polybench HLS Processed Test Report\n"
        report_text += "----------------------------------\n"
        report_text += "\n"
        for benchmark, return_code_compile, return_code_run, error in zip(
            benchmarks_to_test, return_codes_compile, return_codes_run, data_error
        ):
            report_text += f"BENCHMARK : {benchmark.stem}\n"
            report_text += f"COMPILE   : {return_code_compile}\n"
            report_text += f"RUN       : {return_code_run}\n"
            if return_code_compile == 0 and return_code_run == 0:
                report_text += "ERROR     :\n"
                report_text += json.dumps(error, indent=4)
            report_text += "\n\n"

        report_file.write_text(report_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "benchmarks_directory", type=Path, nargs="?", default=Path("./hls-polybench/")
    )
    parser.add_argument("-j", "--jobs", type=int, default=16)
    parser.add_argument("-r", "--report", action="store_true", default=False)
    parser.add_argument("-rf", "--report-file", type=Path, default=Path("./report.txt"))
    args = parser.parse_args()
    main(args)
