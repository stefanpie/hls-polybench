import argparse
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from joblib import Parallel, delayed
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


def get_c_function_signature(c_fp: Path, function_start_str: str):
    c_text = c_fp.read_text()
    function_start = c_text.find(function_start_str)

    if function_start == -1:
        raise ValueError(f"Could not find {function_start_str} function")

    block_start = c_text.find("{", function_start)
    if block_start == -1:
        raise ValueError(
            f"Could not find opening brace of {function_start_str} function"
        )

    signature = c_text[function_start:block_start].strip() + ";"
    return signature


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


RE_DECIMAL = re.compile(r"(?:[0-9]*?)\.(?:[0-9]+)f?")


def cast_decimal_to_ap_fixed(c_fp: Path):
    c_text = c_fp.read_text()
    offset = 0
    for match in RE_DECIMAL.finditer(c_text):
        start, end = match.span()
        start += offset
        end += offset
        # new_text = "(t_ap_fixed)" + c_text[start:end]
        new_text = "(" + "t_ap_fixed" + "(" + c_text[start:end] + ")" + ")"
        c_text = c_text[:start] + new_text + c_text[end:]
        offset += len(new_text) - (end - start)
    c_fp.write_text(c_text)


RE_DECIMAL_NOT_IN_QUOTES = re.compile(
    r'((?:[0-9]*?)\.(?:[0-9]+)f?)(?=([^"]*"[^"]*")*[^"]*$)'
)


def cast_decimal_to_ap_fixed_not_in_quotes(c_fp: Path):
    c_text = c_fp.read_text()
    offset = 0
    for match in RE_DECIMAL_NOT_IN_QUOTES.finditer(c_text):
        start, end = match.span()
        start += offset
        end += offset
        # new_text = "(" + "(t_ap_fixed)" + c_text[start:end] + ")"
        new_text = "(" + "t_ap_fixed" + "(" + c_text[start:end] + ")" + ")"
        c_text = c_text[:start] + new_text + c_text[end:]
        offset += len(new_text) - (end - start)
    c_fp.write_text(c_text)


def process_benchmark_header(h_fp: Path):
    h_text = h_fp.read_text()
    lines = h_text.splitlines()
    new_lines = []
    for line in lines:
        if "DATA_PRINTF_MODIFIER" in line:
            new_lines.append(line)
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
            new_lines.append("typedef ap_fixed<48,16> t_ap_fixed;")
            new_lines.append(line.replace("float", "t_ap_fixed"))
            # dummy replace, keep as float
            # new_lines.append("typedef float t_ap_fixed;")
            # new_lines.append(line.replace("float", "t_ap_fixed"))
        elif "DATA_TYPE double" in line:
            new_lines.append("typedef ap_fixed<48,16> t_ap_fixed;")
            new_lines.append(line.replace("double", "t_ap_fixed"))
            # dummy replace, keep as double
            # new_lines.append("typedef double t_ap_fixed;")
            # new_lines.append(line.replace("double", "t_ap_fixed"))
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
    # add_to_top(c_fp, '#include "ap_fixed.h"\n#include "hls_math.h"\n')
    cast_decimal_to_ap_fixed(c_fp)


RE_ARRAY_DECL_MACRO = re.compile(r"POLYBENCH_\dD_ARRAY_DECL\((.*?)\)")


def replace_array_declarations(c_fp: Path):
    # convert POLYBENCH_2D_ARRAY_DECL(tmp,DATA_TYPE,NI,NJ,ni,nj) into DATA_TYPE POLYBENCH_2D(tmp,NI,NJ,ni,nj)
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    new_lines = []
    for line in lines:
        match = RE_ARRAY_DECL_MACRO.search(line)
        if match:
            arg_list = match.group(1).split(",")
            var = arg_list[0]
            d_type = arg_list[1]
            dims = arg_list[2:]
            new_line = f"  {d_type} POLYBENCH_{len(dims)//2}D({var},{','.join(dims)});"
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


RE_DCE_CALL = re.compile(r"polybench_prevent_dce\(((?:.|\s)*?)\);")


def remove_dce_call(c_fp: Path):
    c_fp = Path(c_fp)
    c_text = c_fp.read_text()
    c_text = RE_DCE_CALL.sub(r"\1;", c_text)
    c_fp.write_text(c_text)


def extract_apfixed_typedef(c_fp: Path) -> str | None:
    typedef_line = None
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    for line in lines:
        if line.startswith("typedef ap_fixed"):
            typedef_line = line
            break
    return typedef_line


def fix_includes(c_fp: Path):
    # include -> #include
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    new_lines = []
    for line in lines:
        if "# include" in line:
            new_lines.append(line.replace("# include", "#include"))
        else:
            new_lines.append(line)
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def fix_spacing(c_fp: Path):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    new_lines = []
    blank_line_count = 0
    for line in lines:
        if line.strip() == "":
            blank_line_count += 1
            if blank_line_count <= 2:
                new_lines.append(line)
        else:
            blank_line_count = 0
            new_lines.append(line)
    fixed_text = "\n".join(new_lines)
    c_fp.write_text(fixed_text)


def add_new_include_at_top(c_fp: Path, new_include: str):
    c_text = c_fp.read_text()
    c_text = new_include + "\n" + c_text
    c_fp.write_text(c_text)


def add_new_include_after_last_include(c_fp: Path, new_include: str):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    last_include_line_number = None
    for i, line in enumerate(lines):
        if line.startswith("#include"):
            last_include_line_number = i
    if last_include_line_number is None:
        raise ValueError("Could not find last include")

    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if i == last_include_line_number:
            new_lines.append(new_include)
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def add_new_lines_after_last_include(c_fp: Path, lines_to_add: list[str]):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    last_include_line_number = None
    for i, line in enumerate(lines):
        if line.startswith("#include"):
            last_include_line_number = i
    if last_include_line_number is None:
        raise ValueError("Could not find last include")

    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if i == last_include_line_number:
            new_lines += "\n"
            new_lines += lines_to_add
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def add_new_lines_after_matching_line(
    c_fp: Path, match_str: str, lines_to_add: list[str]
):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    match_line_number = None
    for i, line in enumerate(lines):
        if match_str in line:
            match_line_number = i
    if match_line_number is None:
        raise ValueError("Could not find match")

    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if i == match_line_number:
            new_lines += "\n"
            new_lines += lines_to_add
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def remove_pointers_and_refs_from_c_function_call(
    c_fp: Path, function_call_str: str, top_function: str
):
    c_text = c_fp.read_text()
    top_function_start = c_text.find(top_function)
    if top_function_start == -1:
        raise ValueError(f"Could not find {top_function} function")

    # find the first {
    block_start = c_text.find("{", top_function_start)
    if block_start == -1:
        raise ValueError(f"Could not find opening brace of {top_function} function")

    # keep track of {} nesting
    nesting = 1
    for i in range(block_start + 1, len(c_text)):
        if c_text[i] == "{":
            nesting += 1
        elif c_text[i] == "}":
            nesting -= 1
        if nesting == 0:
            top_function_end = i
            break
    else:
        raise ValueError(f"Could not find closing brace of {top_function} function")

    function_call_start = c_text.find(
        function_call_str, top_function_start, top_function_end
    )
    if function_call_start == -1:
        raise ValueError(f"Could not find {function_call_str} function call")
    function_call_end = c_text.find(";", function_call_start, top_function_end)
    if function_call_end == -1:
        raise ValueError(f"Could not find {function_call_str} function call")

    function_call = c_text[function_call_start : function_call_end + 1]
    function_call = function_call.replace("*", "")
    # function_call = function_call.replace("&", "")
    c_text = (
        c_text[:function_call_start] + function_call + c_text[function_call_end + 1 :]
    )
    c_fp.write_text(c_text)


def cast_printf_ap_fixed_to_float(c_fp: Path):
    c_text = c_fp.read_text()
    lines = c_text.splitlines()
    new_lines = []
    for line in lines:
        match = re.search(r"fprintf\s*\(\s*stderr\s*,\s*\"%0\.[0-9]+l?f\s*\", ?", line)
        if match:
            start, end = match.span()
            new_line = line[:start] + match.group(0) + "(float)" + line[end:]
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    c_text = "\n".join(new_lines)
    c_fp.write_text(c_text)


def add_more_decimals_to_printf(c_fp: Path, n_decimals: int):
    c_text = c_fp.read_text()
    c_text = c_text.replace("%0.2lf", f"%0.{n_decimals}lf")
    c_text = c_text.replace("%0.2f", f"%0.{n_decimals}f")
    c_fp.write_text(c_text)


def replace_text_exact(c_fp: Path, old_text: str, new_text: str):
    c_text = c_fp.read_text()
    c_text = c_text.replace(old_text, new_text)
    c_fp.write_text(c_text)


RE_ARRAY_DECLARATION = re.compile(r"t_ap_fixed \w+(?:\[.*?\])+;")


def move_array_declaration_to_outer_scope(c_fp: Path):
    c_text = c_fp.read_text()

    array_declarations = list(RE_ARRAY_DECLARATION.finditer(c_text))
    array_declarations_text = [match.group(0) for match in array_declarations]

    for t in array_declarations_text:
        c_text = c_text.replace(t, "")

    # c_text = c_text.replace(
    #     "int main", "\n".join(array_declarations_text) + "\n\n\nint main"
    # )

    c_fp.write_text(c_text)

    add_new_lines_after_last_include(c_fp, array_declarations_text)


def main(args):
    n_jobs = args.jobs

    polybench_dataset_size = args.dataset_size

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

    # build and run all benchmarks
    # capture std out

    p = subprocess.run(
        ["perl", "./utilities/makefile-gen.pl", ".", "-cfg"],
        cwd=tmp_dir,
        capture_output=True,
        text=True,
    )

    if p.returncode != 0:
        print(p.stderr)
        print(p.stdout)
        raise RuntimeError("Failed to run makefile-gen.pl")
    else:
        print(p.stdout)

    main_config_make_fp = tmp_dir / "config.mk"
    main_config_make_text = main_config_make_fp.read_text()
    main_config_make_text = main_config_make_text.replace("CFLAGS=-O2", "CFLAGS=-O3")
    main_config_make_text = main_config_make_text.replace(
        "-DPOLYBENCH_USE_C99_PROTO", ""
    )

    if polybench_dataset_size != "DEFAULT":
        for line in main_config_make_text.splitlines():
            if line.startswith("CFLAGS"):
                main_config_make_text = line + f" -D{polybench_dataset_size}_DATASET"
                break
        else:
            raise ValueError("Could not find CFLAGS line")

    main_config_make_fp.write_text(main_config_make_text)

    makefiles_fps = list(tmp_dir.rglob("Makefile"))

    def compile_design(makefile_fp: Path):
        design_dir = makefile_fp.parent
        design_name = design_dir.name

        h_fp = design_dir / f"{design_name}.h"
        print(h_fp)
        add_more_decimals_to_printf(h_fp, 6)

        print(f"Compiling {design_dir} : {design_name}")
        p = subprocess.run(
            ["make", "clean"],
            cwd=design_dir,
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            print(p.stderr)
            print(p.stdout)
            raise RuntimeError("Failed to run make")
        p = subprocess.run(
            ["make"],
            cwd=design_dir,
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            print(p.stderr)
            print(p.stdout)
            raise RuntimeError("Failed to run make")

    Parallel(n_jobs=n_jobs)(
        delayed(compile_design)(makefile_fp) for makefile_fp in makefiles_fps
    )

    def run_design(makefile_fp: Path):
        design_dir = makefile_fp.parent
        design_name = design_dir.name
        print(f"Running {design_dir} : {design_name}")
        p = subprocess.run(
            [f"./{design_name}"],
            cwd=design_dir,
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            print(p.stderr)
            print(p.stdout)
            raise RuntimeError("Failed to run design")

        tb_golden_output_fp = makefile_fp.parent / "tb_data.txt"
        tb_golden_output_fp.write_text(p.stderr)

    Parallel(n_jobs=n_jobs)(
        delayed(run_design)(makefile_fp) for makefile_fp in makefiles_fps
    )

    benchmark_list_fp = fp_utils / "benchmark_list"
    benchmark_list = [
        Path(line.strip()) for line in benchmark_list_fp.read_text().splitlines()
    ]

    def process_benchmark(benchmark: Path):
        fp_benchmark = tmp_dir / benchmark
        benchmark_name = benchmark.stem
        print(f"Processing {benchmark_name}")
        new_benchmark_dir = new_benchmarks_dir / benchmark_name
        if new_benchmark_dir.exists():
            shutil.rmtree(new_benchmark_dir)
        new_benchmark_dir.mkdir(parents=True, exist_ok=True)

        benchmark_files = fp_benchmark.parent.glob(benchmark_name + ".*")
        for file in benchmark_files:
            shutil.copy(file, new_benchmark_dir)
        shutil.copy(fp_polybench_h, new_benchmark_dir)
        shutil.copy(fp_polybench_c, new_benchmark_dir)

        tb_data_original_fp = fp_benchmark.parent / "tb_data.txt"
        shutil.copy(tb_data_original_fp, new_benchmark_dir)

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
        ]
        if polybench_dataset_size != "DEFAULT":
            fake_argv += ["-D", f"{polybench_dataset_size}_DATASET"]

        # str(input_c_file)
        fake_argv += [str(input_c_file)]

        with SuppressOutput():
            CmdPreprocessor(fake_argv)

        process_benchmark_c(output_c_file)

        input_tb_file = new_benchmark_dir / f"{benchmark_name}_tb.c"
        output_tb_file = new_benchmark_dir / f"{benchmark_name}_tb.preprocessed.c"

        shutil.copy(input_c_file, input_tb_file)

        replace_array_declarations(input_tb_file)
        remove_dce_call(input_tb_file)
        remove_line(input_tb_file, "/* Be clean. */")
        remove_line(input_tb_file, "POLYBENCH_FREE_ARRAY")
        remove_line(input_tb_file, "/* Start timer. */")
        remove_line(input_tb_file, "polybench_start_instruments;")
        remove_line(input_tb_file, "/* Stop and print timer. */")
        remove_line(input_tb_file, "polybench_stop_instruments;")
        remove_line(input_tb_file, "polybench_print_instruments;")

        fake_argv = [
            sys.argv[0],
            "-o",
            str(output_tb_file),
            "-I",
            str(new_benchmark_dir),
        ]
        if polybench_dataset_size != "DEFAULT":
            fake_argv += ["-D", f"{polybench_dataset_size}_DATASET"]

        fake_argv += [
            str(input_tb_file),
        ]

        with SuppressOutput():
            CmdPreprocessor(fake_argv)

        remove_line(output_tb_file, "#line")
        remove_line(output_tb_file, "extern void* polybench_alloc_data")
        remove_line(output_tb_file, "extern void polybench_free_data")
        remove_line(output_tb_file, "extern void polybench_flush_cache")
        remove_line(output_tb_file, "extern void polybench_prepare_instruments")
        remove_line(output_tb_file, "#include <unistd.h>")

        os.remove(input_c_file)
        os.remove(h_file)
        os.remove(new_benchmark_dir / "polybench.c")
        os.remove(new_benchmark_dir / "polybench.h")
        os.rename(output_c_file, input_c_file)
        os.rename(input_c_file, new_benchmark_dir / (benchmark_name + ".cpp"))
        os.rename(output_tb_file, input_tb_file)
        os.rename(input_tb_file, new_benchmark_dir / (benchmark_name + "_tb.cpp"))

        new_h_fp = new_benchmark_dir / (benchmark_name + ".h")
        h_text = ""
        h_text += "#pragma once\n"
        h_text += '#include "ap_fixed.h"\n'
        h_text += '#include "hls_math.h"\n'
        h_text += "\n"
        typedef_line = extract_apfixed_typedef(
            new_benchmark_dir / (benchmark_name + ".cpp")
        )
        if typedef_line:
            h_text += typedef_line + "\n"
        h_text += "\n"

        kernel_function_signature = get_c_function_signature(
            new_benchmark_dir / (benchmark_name + ".cpp"),
            f"void kernel_{benchmark_name.replace('-', '_')}",
        )
        # h_text += kernel_function_signature + "\n"
        h_text += 'extern "C" {\n'
        h_text += kernel_function_signature + "\n"
        h_text += "}\n"
        new_h_fp.write_text(h_text)

        remove_line(new_benchmark_dir / (benchmark_name + ".cpp"), "typedef ap_fixed")
        remove_line(
            new_benchmark_dir / (benchmark_name + "_tb.cpp"), "typedef ap_fixed"
        )

        remove_line_exact(new_benchmark_dir / (benchmark_name + ".cpp"), "static")
        remove_line_exact(new_benchmark_dir / (benchmark_name + "_tb.cpp"), "static")

        remove_c_function(
            new_benchmark_dir / (benchmark_name + "_tb.cpp"),
            f"void kernel_{benchmark_name.replace('-', '_')}",
        )

        fix_includes(new_benchmark_dir / (benchmark_name + "_tb.cpp"))

        fix_spacing(new_benchmark_dir / (benchmark_name + ".cpp"))
        fix_spacing(new_benchmark_dir / (benchmark_name + "_tb.cpp"))

        add_new_include_at_top(
            new_benchmark_dir / (benchmark_name + ".cpp"),
            f'#include "{benchmark_name}.h"',
        )
        add_new_include_after_last_include(
            new_benchmark_dir / (benchmark_name + "_tb.cpp"),
            f'\n#include "{benchmark_name}.h"',
        )

        remove_pointers_and_refs_from_c_function_call(
            new_benchmark_dir / (benchmark_name + "_tb.cpp"),
            "init_array",
            "int main",
        )

        remove_pointers_and_refs_from_c_function_call(
            new_benchmark_dir / (benchmark_name + "_tb.cpp"),
            f"kernel_{benchmark_name.replace('-', '_')}",
            "int main",
        )

        remove_pointers_and_refs_from_c_function_call(
            new_benchmark_dir / (benchmark_name + "_tb.cpp"),
            "print_array",
            "int main",
        )

        cast_printf_ap_fixed_to_float(new_benchmark_dir / (benchmark_name + "_tb.cpp"))

        cast_decimal_to_ap_fixed_not_in_quotes(
            new_benchmark_dir / (benchmark_name + "_tb.cpp")
        )

        move_array_declaration_to_outer_scope(
            new_benchmark_dir / (benchmark_name + "_tb.cpp")
        )

        # add_more_decimals_to_printf(new_benchmark_dir / (benchmark_name + "_tb.cpp"), 4)

        ### Special cases

        if benchmark_name == "nussinov":
            # special case to handle kernel which uese extra typedef for "char" named "base"

            # remove the line "typedef char base"
            # replace the word base with char

            remove_line(
                new_benchmark_dir / (benchmark_name + ".cpp"), "typedef char base"
            )
            replace_text_exact(
                new_benchmark_dir / (benchmark_name + ".cpp"), "base", "char"
            )

            remove_line(
                new_benchmark_dir / (benchmark_name + "_tb.cpp"), "typedef char base"
            )
            replace_text_exact(
                new_benchmark_dir / (benchmark_name + "_tb.cpp"), "base", "char"
            )

            remove_line(
                new_benchmark_dir / (benchmark_name + ".h"), "typedef char base"
            )
            replace_text_exact(
                new_benchmark_dir / (benchmark_name + ".h"), "base", "char"
            )

        spelcial_cases_pointer_in_tb = ["cholesky", "lu", "ludcmp"]

        if benchmark_name in spelcial_cases_pointer_in_tb:
            # special case to remove the * from the B pointer in the _tb.cpp file
            replace_text_exact(
                new_benchmark_dir / (benchmark_name + "_tb.cpp"), "(*B)", "B"
            )

        if benchmark_name == "gramschmidt":
            # special case to add support for eps in gramschmidt calculation
            # due to sqrt and fixed point quantizing to 0 sometimes
            kernel_fp = new_benchmark_dir / (benchmark_name + ".cpp")

            add_new_lines_after_matching_line(
                kernel_fp,
                "t_ap_fixed nrm;",
                [
                    "  const t_ap_fixed eps = hls::nextafter(t_ap_fixed(0.0), t_ap_fixed(1.0));"
                ],
            )
            replace_text_exact(
                new_benchmark_dir / (benchmark_name + ".cpp"),
                "R[k][k] = hls::sqrt(nrm);",
                "R[k][k] = hls::sqrt(nrm);\n      if (R[k][k] == t_ap_fixed(0.0)) R[k][k] += eps;",
            )

            # TODO: fix other issues with large fixed point percision rnage and norm sum overflows

        if benchmark_name == "atax":
            # special case in atax to fix weird casting rules between int and ap_fixed based on int loop index variables
            tb_fp = new_benchmark_dir / (benchmark_name + "_tb.cpp")
            replace_text_exact(
                tb_fp,
                "x[i] = 1 + (i / fn);",
                "x[i] = (t_ap_fixed(1.0)) + ( (t_ap_fixed(i)) / fn );",
            )
            replace_text_exact(
                tb_fp,
                "((i+j) % n) / (5*m)",
                "(t_ap_fixed(((i+j) % n))) / (t_ap_fixed(5.0)*t_ap_fixed(m))",
            )

        if benchmark_name == "gemver":
            # special case in gemver to fix weird casting rules between int and ap_fixed based on int loop index variables
            tb_fp = new_benchmark_dir / (benchmark_name + "_tb.cpp")
            replace_text_exact(
                tb_fp,
                "((i+1)/fn)",
                "(t_ap_fixed(i+1)) / (fn)",
            )
            replace_text_exact(
                tb_fp,
                "(i*j % n) / n",
                "((t_ap_fixed(i*j % n)) / (t_ap_fixed(n)))",
            )

        if benchmark_name == "gramschmidt":
            # special case in gramschmidt to fix weird casting rules between int and ap_fixed based on int loop index variables
            tb_fp = new_benchmark_dir / (benchmark_name + "_tb.cpp")
            # (((t_ap_fixed) ((i*j) % m) / m )*100) + 10
            replace_text_exact(
                tb_fp,
                "(((t_ap_fixed) ((i*j) % m) / m )*100) + 10",
                "(( (t_ap_fixed(i*j % m)) / (t_ap_fixed(m)) ) * (t_ap_fixed(100.0)) ) + (t_ap_fixed(10.0))",
            )

        if benchmark_name == "ludcmp":
            # special case in ludcmp to fix weird casting rules between int and ap_fixed based on int loop index variables
            tb_fp = new_benchmark_dir / (benchmark_name + "_tb.cpp")
            replace_text_exact(
                tb_fp,
                "x[i] = 0;",
                "x[i] = t_ap_fixed(0.0);",
            )
            replace_text_exact(
                tb_fp,
                "y[i] = 0;",
                "y[i] = t_ap_fixed(0.0);",
            )
            # b[i] = (i+1)/fn/(t_ap_fixed(2.0)) + 4;
            replace_text_exact(
                tb_fp,
                "b[i] = (i+1)/fn/(t_ap_fixed(2.0)) + 4;",
                "b[i] = ( (t_ap_fixed(i+1)) / (fn) ) / (t_ap_fixed(2.0)) + (t_ap_fixed(4.0));",
            )
            # A[i][j] = 0;
            replace_text_exact(
                tb_fp,
                "A[i][j] = 0;",
                "A[i][j] = t_ap_fixed(0.0);",
            )
            # A[i][i] = 1;
            replace_text_exact(
                tb_fp,
                "A[i][i] = 1;",
                "A[i][i] = t_ap_fixed(1.0);",
            )

        if benchmark_name == "correlation":
            # special case in ludcmp to fix weird casting rules between int and ap_fixed based on int loop index variables
            tb_fp = new_benchmark_dir / (benchmark_name + "_tb.cpp")

            RE_FLOAT_N = re.compile("\*float_n = \(t_ap_fixed\)(\d+);")
            match = RE_FLOAT_N.search(tb_fp.read_text())
            if match:
                float_n = match.group(1)
                replace_text_exact(
                    tb_fp,
                    f"*float_n = (t_ap_fixed){float_n};",
                    f"*float_n = t_ap_fixed({float_n}.0);",
                )

            RE_LINE_TO_CHANGE = re.compile("\(t_ap_fixed\)\(i\*j\)/(\d+) \+ i;")
            match = RE_LINE_TO_CHANGE.search(tb_fp.read_text())
            if match:
                n = match.group(1)
                replace_text_exact(
                    tb_fp,
                    f"(t_ap_fixed)(i*j)/{n} + i;",
                    f"(t_ap_fixed)(t_ap_fixed(i*j)/t_ap_fixed({n}.0)) + t_ap_fixed(i);",
                )

        if benchmark_name == "covariance":
            # special case in ludcmp to fix weird casting rules between int and ap_fixed based on int loop index variables

            tb_fp = new_benchmark_dir / (benchmark_name + "_tb.cpp")

            # data[i][j] = ((t_ap_fixed) i*j) / 80;
            RE_LINE_TO_CHANGE = re.compile(
                "data\[i\]\[j\] = \(\(t_ap_fixed\) i\*j\) / (\d+);"
            )

            match = RE_LINE_TO_CHANGE.search(tb_fp.read_text())
            if match:
                n = match.group(1)
                replace_text_exact(
                    tb_fp,
                    f"data[i][j] = ((t_ap_fixed) i*j) / {n};",
                    f"data[i][j] = t_ap_fixed(i*j) / t_ap_fixed({n}.0);",
                )

        fix_spacing(new_benchmark_dir / (benchmark_name + ".cpp"))
        fix_spacing(new_benchmark_dir / (benchmark_name + "_tb.cpp"))
        fix_spacing(new_benchmark_dir / (benchmark_name + ".h"))

    Parallel(n_jobs=n_jobs)(
        delayed(process_benchmark)(benchmark) for benchmark in benchmark_list
    )

    shutil.rmtree(tmp_dir)
    for folder in new_benchmarks_dir.glob("*"):
        shutil.move(folder, output_dir)
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
        help="Path to the input polybench distribution tar.gz file",
    )
    parser.add_argument(
        "output_directory",
        type=Path,
        nargs="?",
        default=Path("./hls-polybench/"),
        help="Generated output directory with processed benchmarks",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        default=Path("./hls-polybench.tar.gz"),
        help="Generated output tar.gz file with processed benchmarks",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        nargs="?",
        default=1,
        help="Number of jobs to run in parallel",
    )

    POLYBENCH_DATASET_SIZES = [
        "MINI",
        "SMALL",
        "MEDIUM",
        "LARGE",
        "EXTRALARGE",
        "DEFAULT",
    ]
    parser.add_argument(
        "-s",
        "--dataset-size",
        type=str,
        nargs="?",
        default="MEDIUM",
        choices=POLYBENCH_DATASET_SIZES,
        help=f"Dataset size to use based on the sizes defined by polybench, {POLYBENCH_DATASET_SIZES}, or the DEFAULT size for each individual benchmark",
    )

    args = parser.parse_args()
    main(args)
