import argparse
import os
import re
import shutil
import sys
import tarfile
from pathlib import Path

from pcpp.pcmd import CmdPreprocessor


class SuppressOutput:
    def __enter__(self):
        # Save the current stdout and stderr
        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr

        # Redirect stdout and stderr to devnull
        self.devnull = open(os.devnull, "w")
        sys.stdout = self.devnull
        sys.stderr = self.devnull

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore stdout and stderr
        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr

        # Close the devnull file
        self.devnull.close()

        # Handle any exception that occurred in the block
        if exc_type is not None:
            print(f"Exception occurred: {exc_type}, {exc_val}")


def remove_c_function(c_fp: Path, function_start_str: str):
    c_text = c_fp.read_text()
    function_start = c_text.find(function_start_str)
    if function_start == -1:
        raise ValueError(f"Could not find {function_start_str} function")

    # find the first {
    block_start = c_text.find("{", function_start)
    if block_start == -1:
        raise ValueError(
            f"Could not find opening brace of {function_start_str} function"
        )

    # keep track of {} nesting
    nesting = 1
    for i in range(block_start + 1, len(c_text)):
        if c_text[i] == "{":
            nesting += 1
        elif c_text[i] == "}":
            nesting -= 1
        if nesting == 0:
            function_end = i
            break
    else:
        raise ValueError(
            f"Could not find closing brace of {function_start_str} function"
        )

    c_text = c_text[:function_start] + c_text[function_end + 1 :]
    c_fp.write_text(c_text)


def remove_line(c_fp: Path, contains_str: str):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    new_lines = []
    for line in lines:
        if contains_str not in line:
            new_lines.append(line)
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def remove_line_exact(c_fp: Path, exact_str: str):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    new_lines = []
    for line in lines:
        if exact_str != line:
            new_lines.append(line)
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def trim_top_empty_lines(c_fp: Path):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    new_lines = []
    idx = 0
    for line in lines:
        if line.strip() != "":
            break
        idx += 1
    new_lines = lines[idx:]
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def add_to_top(c_fp: Path, text: str):
    c_text = c_fp.read_text()
    c_text = text + "\n" + c_text
    c_fp.write_text(c_text)


RE_DECIMAL = re.compile(r"(?:[0-9]*?)\.(?:[0-9]+)")


def cast_decimal_to_ap_fixed(c_fp: Path):
    c_text = c_fp.read_text()
    offset = 0
    for match in RE_DECIMAL.finditer(c_text):
        start, end = match.span()
        start += offset
        end += offset
        new_text = "(t_ap_fixed)" + c_text[start:end]
        c_text = c_text[:start] + new_text + c_text[end:]
        offset += len(new_text) - (end - start)
    c_fp.write_text(c_text)


def process_benchmark_header(h_fp: Path):
    h_text = h_fp.read_text()
    lines = h_text.splitlines()
    new_lines = []
    for line in lines:
        if "DATA_PRINTF_MODIFIER" in line:
            continue
        elif "define SCALAR_VAL(x) x##f" in line:
            new_lines.append(line.replace("x##f", "x"))
        elif "SQRT_FUN" in line:
            if "define SQRT_FUN(x) sqrt(x)" in line:
                new_line = line.replace("sqrt(x)", "hls::sqrt(x)")
                new_lines.append(new_line)
                continue
            if "define SQRT_FUN(x) sqrtf(x)" in line:
                new_line = line.replace("sqrtf(x)", "hls::sqrt(x)")
                new_lines.append(new_line)
                continue
        elif "EXP_FUN" in line:
            if "define EXP_FUN(x) hls::exp(x)" in line:
                new_line = line.replace("exp(x)", "hls::exp(x)")
                new_lines.append(new_line)
                continue
            if "define EXP_FUN(x) expf(x)" in line:
                new_line = line.replace("expf(x)", "hls::exp(x)")
                new_lines.append(new_line)
                continue
        elif "POW_FUN" in line:
            if "define POW_FUN(x,y) pow(x,y)" in line:
                new_line = line.replace("pow(x,y)", "hls::pow(x,y)")
                new_lines.append(new_line)
                continue
            if "define POW_FUN(x,y) powf(x,y)" in line:
                new_line = line.replace(
                    "powf(x,y)", "hls::pow((t_ap_fixed)(x),(t_ap_fixed)(y))"
                )
                new_lines.append(new_line)
                continue
        elif "DATA_TYPE float" in line:
            new_lines.append("typedef ap_fixed<32,16> t_ap_fixed;")
            new_lines.append(line.replace("float", "t_ap_fixed"))
        elif "DATA_TYPE double" in line:
            new_lines.append("typedef ap_fixed<32,16> t_ap_fixed;")
            new_lines.append(line.replace("double", "t_ap_fixed"))
        else:
            new_lines.append(line)

    h_text = "\n".join(new_lines)
    h_fp.write_text(h_text)


def process_benchmark_c(c_fp: Path):
    remove_c_function(c_fp, "static\nvoid init_array")
    remove_c_function(c_fp, "static\nvoid print_array")
    remove_c_function(c_fp, "int main(int argc, char** argv)")
    remove_line_exact(c_fp, "static")
    remove_line(c_fp, "#line ")
    remove_line(c_fp, "#pragma scop")
    remove_line(c_fp, "#pragma endscop")
    remove_line(c_fp, "polybench_alloc_data")
    remove_line(c_fp, "polybench_free_data")
    remove_line(c_fp, "polybench_flush_cache")
    remove_line(c_fp, "polybench_prepare_instruments")
    remove_line(c_fp, "# include")
    remove_line(c_fp, "#include")
    trim_top_empty_lines(c_fp)
    add_to_top(c_fp, '#include "ap_fixed.h"\n#include "hls_math.h"\n')
    cast_decimal_to_ap_fixed(c_fp)


def main(args):
    polybench_distribution_fp = args.polybench_distribution
    output_dir = args.output_directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_file

    if not polybench_distribution_fp.exists():
        raise FileNotFoundError(
            "Polybench distribution not found at {}".format(polybench_distribution_fp)
        )

    if not tarfile.is_tarfile(polybench_distribution_fp):
        raise ValueError(
            "Polybench distribution is not a tar.gz file: {}".format(
                polybench_distribution_fp
            )
        )

    tmp_dir = output_dir / "tmp"
    new_benchmarks_dir = output_dir / "benchmarks"

    with tarfile.open(polybench_distribution_fp, "r:gz") as tar:
        tar.extractall(path=tmp_dir)
    for file in tmp_dir.glob("polybench-c-4.2.1-beta/*"):
        os.rename(file, tmp_dir / file.name)
    os.rmdir(tmp_dir / "polybench-c-4.2.1-beta")

    fp_utils = tmp_dir / "utilities"
    fp_polybench_h = fp_utils / "polybench.h"
    fp_polybench_c = fp_utils / "polybench.c"

    benchmark_list_fp = fp_utils / "benchmark_list"
    benchmark_list = [
        Path(line.strip()) for line in benchmark_list_fp.read_text().splitlines()
    ]

    for benchmark in benchmark_list:
        fp_benchmark = tmp_dir / benchmark
        benchmark_name = benchmark.stem
        print(f"Processing {benchmark_name}")
        new_benchmark_dir = new_benchmarks_dir / benchmark_name
        if new_benchmark_dir.exists():
            shutil.rmtree(new_benchmark_dir)
        new_benchmark_dir.mkdir(parents=True, exist_ok=True)

        # copy benchmark files
        benchmark_files = fp_benchmark.parent.glob(benchmark_name + ".*")
        for file in benchmark_files:
            shutil.copy(file, new_benchmark_dir)
        shutil.copy(fp_polybench_h, new_benchmark_dir)
        shutil.copy(fp_polybench_c, new_benchmark_dir)

        h_file = new_benchmark_dir / (benchmark_name + ".h")
        process_benchmark_header(h_file)

        input_c_file = new_benchmark_dir / (benchmark_name + ".c")
        output_c_file = new_benchmark_dir / (benchmark_name + ".preprocessed.c")

        fake_argv = [
            sys.argv[0],
            "-o",
            str(output_c_file),
            "-I",
            str(new_benchmark_dir),
            str(input_c_file),
        ]
        with SuppressOutput():
            CmdPreprocessor(fake_argv)

        process_benchmark_c(output_c_file)

        os.remove(input_c_file)
        os.remove(h_file)
        os.remove(new_benchmark_dir / "polybench.c")
        os.remove(new_benchmark_dir / "polybench.h")
        os.rename(output_c_file, input_c_file)
        os.rename(input_c_file, new_benchmark_dir / (benchmark_name + ".cpp"))

    shutil.rmtree(tmp_dir)
    for dir in new_benchmarks_dir.glob("*"):
        shutil.move(dir, output_dir)
    shutil.rmtree(new_benchmarks_dir)

    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(output_dir, arcname=output_dir.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "polybench_distribution",
        type=Path,
        nargs="?",
        default=Path("polybench-c-4.2.1-beta.tar.gz"),
    )
    parser.add_argument(
        "output_directory", type=Path, nargs="?", default=Path("./hls-polybench/")
    )
    parser.add_argument(
        "output_file", type=Path, nargs="?", default=Path("./hls-polybench.tar.gz")
    )

    args = parser.parse_args()
    main(args)
