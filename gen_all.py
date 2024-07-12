import shutil
import subprocess
import tempfile
from argparse import ArgumentParser, Namespace
from pathlib import Path

from joblib import Parallel, delayed

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


def hls_synth_benchmark(
    benchmark_directory: Path, temp_dir_overide: Path | None = None
) -> int:
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

    temp_dir = tempfile.mkdtemp()
    temp_dir_path = Path(temp_dir)
    print(f"temp_dir_path: {temp_dir_path}")

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

    if p.returncode == 0:
        csynth_rpt_fp = (
            temp_dir_path
            / f"test_proj_{benchmark_name}"
            / "solution"
            / "syn"
            / "report"
            / "csynth.rpt"
        )
        shutil.copy(csynth_rpt_fp, temp_dir_path / "csynth.rpt")

    return p.returncode


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=1)

    args = parser.parse_args()
    n_jobs = args.jobs

    for suffix in SUFFIXES:
        suffix_lowercase = suffix.lower()

        args_for_processor = Namespace()
        args_for_processor.jobs = n_jobs
        args_for_processor.dataset_size = suffix
        args_for_processor.output_suffix = f"__{suffix_lowercase}"
        args_for_processor.benchmark_distribution = FP_BENCHMARK_DIST
        args_for_processor.output_directory = DIR_DIST / OUTPUT_NAME
        args_for_processor.output_file = DIR_DIST / OUTPUT_NAME

        main(args_for_processor)

        full_output_dir = Path(
            (DIR_DIST / f"{OUTPUT_NAME}{args_for_processor.output_suffix}")
        )

        # add gitignore in the output directories
        # (full_output_dir / ".gitignore").write_text("*")

        # get all folders in the output directory
        # kernel_dirs = [fp for fp in full_output_dir.iterdir() if fp.is_dir()]

        # for kernel_dir in kernel_dirs:
        #     hls_synth_benchmark(kernel_dir)

        # Parallel(n_jobs=n_jobs, backend="threading")(
        #     delayed(hls_synth_benchmark)(kernel_dir) for kernel_dir in kernel_dirs
        # )
