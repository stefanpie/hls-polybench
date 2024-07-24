import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from argparse import ArgumentParser, Namespace
from itertools import product
from pathlib import Path
from pprint import pp

import numpy as np
from joblib import Parallel, delayed

from process import main


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


def compile_and_run_benchmark(
    benchmark_directory: Path,
    temp_dir_overide: Path | None = None,
    copy_tb_data: bool = True,
    copy_tb_error: bool = True,
):
    benchmark_name = benchmark_directory.stem

    # if temp_dir_overide is None:
    #     temp_dir = tempfile.TemporaryDirectory()
    #     temp_dir_path = Path(temp_dir.name)
    # else:
    #     temp_dir_path = temp_dir_overide / benchmark_name
    #     temp_dir_path.mkdir(exist_ok=True, parents=True)

    if temp_dir_overide is not None:
        raise NotImplementedError(
            "temp_dir_overide is not supported for custom path yet"
        )

    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    print(f"temp_dir_path: {temp_dir_path}")

    all_files = list(benchmark_directory.glob("*"))
    for file in all_files:
        shutil.copy(file, temp_dir_path)

    vitis_hls_include_dir = get_vitis_hls_include_dir()
    clang_bin_path = get_vitis_hls_clang_pp_path()
    # vitis_hls_install_dir = get_vitis_hls_install_dir()

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

    print(f"COMPILE : {benchmark_name}: {p_compile.returncode}")

    if p_compile.returncode != 0:
        raise RuntimeError("Compiling the benchmark failed")
        # return p_compile.returncode, None, None

    # run the compiled binary
    p_run = subprocess.run(
        [f"./{benchmark_name}"],
        cwd=Path(temp_dir_path),
        text=True,
        capture_output=True,
    )

    print(f"RUN : {benchmark_name}: {p_run.returncode}")

    if p_run.returncode != 0:
        raise RuntimeError("Runing the compiled benchmark failed")

    output_tb_data = temp_dir_path / "tb_data_hls.txt"
    output_tb_data.write_text(p_run.stderr)

    data_golden = extract_array_dump_data(benchmark_directory / "tb_data.txt")
    data_hls = extract_array_dump_data(temp_dir_path / "tb_data_hls.txt")

    data_golden_keys = sorted(data_golden.keys())
    data_hls_keys = sorted(data_hls.keys())
    if data_golden_keys != data_hls_keys:
        print(f"ERROR: {benchmark_name}: Array data keys do not match")
        print(f"Golden: {data_golden_keys}")
        print(f"HLS: {data_hls_keys}")
        raise RuntimeError("Array data keys do not match")
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

    if copy_tb_data:
        shutil.copy(
            temp_dir_path / "tb_data_hls.txt", benchmark_directory / "tb_data_hls.txt"
        )

    if copy_tb_error:
        error_fp = benchmark_directory / "tb_data_hls_error.json"
        error_fp.write_text(json.dumps(data_error, indent=4))

    # return p_compile.returncode, p_run.returncode, data_error


def hls_synth_benchmark(
    benchmark_directory: Path,
    temp_dir_overide: Path | None = None,
    copy_ip: bool = True,
    copy_reports: bool = True,
):
    benchmark_name = benchmark_directory.stem

    # if temp_dir_overide is None:
    #     temp_dir = tempfile.TemporaryDirectory()
    #     temp_dir_path = Path(temp_dir.name)
    # else:
    #     temp_dir_path = temp_dir_overide / benchmark_name
    #     temp_dir_path.mkdir(exist_ok=True, parents=True)

    if temp_dir_overide is not None:
        raise NotImplementedError(
            "temp_dir_overide is not supported for custom path yet"
        )

    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    print(f"temp_dir_path: {temp_dir_path}")

    benchmark_name = benchmark_directory.stem
    benchmark_name_c = benchmark_name.replace("-", "_")

    all_files = list(benchmark_directory.glob("*"))
    for file in all_files:
        shutil.copy(file, temp_dir_path)

    print(f"HLS SYNTH : {benchmark_name} : {temp_dir_path}")

    tcl_script = temp_dir_path / "build.tcl"
    tcl_script_txt = ""
    tcl_script_txt += f"open_project -reset test_proj_{benchmark_name}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '.cpp')}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '.h')}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '_tb.cpp')} -tb\n"
    tcl_script_txt += "open_solution solution\n"
    tcl_script_txt += f"set_top kernel_{benchmark_name_c}\n"
    tcl_script_txt += "set_part {xc7z020clg484-1}\n"
    tcl_script_txt += "create_clock -period 10 -name default\n"
    tcl_script_txt += "csynth_design\n"
    tcl_script_txt += "export_design -format ip_catalog -rtl verilog\n"

    tcl_script_txt += "exit\n"
    tcl_script.write_text(tcl_script_txt)

    p = subprocess.run(
        ["vitis_hls", "-f", tcl_script.resolve()],
        cwd=temp_dir_path,
        text=True,
        capture_output=True,
    )
    print(f"{benchmark_name}: {p.returncode}")

    if p.returncode != 0:
        raise RuntimeError("HLS Synthesis failed")

    csynth_rpt_dir_fp = (
        temp_dir_path / f"test_proj_{benchmark_name}" / "solution" / "syn" / "report"
    )

    report_archive_fp = temp_dir_path / "synth_report.zip"
    with zipfile.ZipFile(report_archive_fp, "w", zipfile.ZIP_DEFLATED) as f:
        f.write(csynth_rpt_dir_fp, arcname=csynth_rpt_dir_fp.name)

    ip_dir_fp = (
        temp_dir_path / f"test_proj_{benchmark_name}" / "solution" / "impl" / "ip"
    )
    ip_fp = list(ip_dir_fp.glob("*.zip"))[0]
    shutil.copy(ip_fp, temp_dir_path / f"ip_{benchmark_name}.zip")

    if copy_ip:
        shutil.copy(ip_fp, benchmark_directory / f"ip_{benchmark_name}.zip")

    if copy_reports:
        shutil.copy(report_archive_fp, benchmark_directory / "synth_report.zip")


DIR_SCRIPT = Path(__file__).parent
DIR_DIST = DIR_SCRIPT / "dist"
if DIR_DIST.exists():
    shutil.rmtree(DIR_DIST)
DIR_DIST.mkdir(parents=True)

FP_BENCHMARK_DIST = DIR_SCRIPT / "polybench-c-4.2.1-beta.tar.gz"

SIZES = (
    "MINI",
    "SMALL",
    "MEDIUM",
    # "DEFAULT",
    # "LARGE",
    # "EXTRALARGE",
)

DATA_TYPES = [
    "FLOAT",
    "FIXED",
]

COMBOS = list(product(SIZES, DATA_TYPES))

OUTPUT_NAME = "hls_polybench"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=1)

    args = parser.parse_args()
    n_jobs = args.jobs

    # for suffix in SIZES:
    for size, data_type in COMBOS:
        suffix = f"__{data_type}__{size}".lower()

        args_for_processor = Namespace()
        args_for_processor.jobs = n_jobs
        args_for_processor.dataset_size = size
        args_for_processor.float_or_fixed = data_type
        args_for_processor.output_suffix = suffix
        args_for_processor.benchmark_distribution = FP_BENCHMARK_DIST
        args_for_processor.output_directory = DIR_DIST / OUTPUT_NAME
        args_for_processor.output_file = DIR_DIST / OUTPUT_NAME

        main(args_for_processor)

        full_output_dir = Path(
            (DIR_DIST / f"{OUTPUT_NAME}{args_for_processor.output_suffix}")
        )

        # add gitignore in the output directories
        (full_output_dir / ".gitignore").write_text("*")

        kernel_dirs = sorted([fp for fp in full_output_dir.iterdir() if fp.is_dir()])

        Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(compile_and_run_benchmark)(kernel_dir) for kernel_dir in kernel_dirs
        )

        # gather errors and rank form highest to lowest
        # error_files = list(full_output_dir.glob("**/tb_data_hls_error.json"))
        # errors = {}
        # for error_file in error_files:
        #     error_data = json.loads(error_file.read_text())
        #     for array_name, error in error_data.items():
        #         errors[(error_file.parent.stem, array_name)] = error["rmse"]
        # errors_sorted = sorted(errors.items(), key=lambda x: x[1], reverse=True)
        # pp(errors_sorted)

        Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(hls_synth_benchmark)(kernel_dir) for kernel_dir in kernel_dirs
        )

        build_archive_name = (
            full_output_dir.name.removesuffix(".tar.gz") + "__build.tar.gz"
        )
        with tarfile.open(build_archive_name, "w:gz") as f:
            for kernel_dir in kernel_dirs:
                f.add(kernel_dir, arcname=kernel_dir.name)
        shutil.move(build_archive_name, DIR_DIST / build_archive_name)
