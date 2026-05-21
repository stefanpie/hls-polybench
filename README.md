# HLS-Polybench

This project aims to provide automation tools to have a reproducible way to generate "High-Level Synthesis (HLS) compatible" versions of all the polybench kernels with their respective testbenches from the original official polybench distribution. Simply provide the main Python script with the path to the latest `polybench.tar.gz` source release (along with some options) and it will generate a `hls-polybench.tar.gz` archive with the HLS-compatible kernels and testbenches each in their own directory.

The generated kernels should be compatible with the Xilinx Vitis HLS tool. All `float` and `double` types are converted to fixed-point types using `ap_fixed` type from the Vitis HLS. All `int` or `uint` types are left unchanged since they are "natively" supported by the Vitis HLS tool.

The automation is done using source code text processing and manipulation using custom Python functions and a Python-based C preprocessor.

## Usage

```text
usage: process.py [-h] [-j [JOBS]] [-s [{MINI,SMALL,MEDIUM,LARGE,EXTRALARGE,DEFAULT}]] [polybench_distribution] [output_directory] [output_file]

positional arguments:
  polybench_distribution
                        Path to the input polybench distribution tar.gz file
  output_directory      Generated output directory with processed benchmarks
  output_file           Generated output tar.gz file with processed benchmarks

options:
  -h, --help            show this help message and exit
  -j [JOBS], --jobs [JOBS]
                        Number of jobs to run in parallel
  -s [{MINI,SMALL,MEDIUM,LARGE,EXTRALARGE,DEFAULT}], --dataset-size [{MINI,SMALL,MEDIUM,LARGE,EXTRALARGE,DEFAULT}]
                        Dataset size to use based on the sizes defined by polybench, ['MINI', 'SMALL', 'MEDIUM', 'LARGE', 'EXTRALARGE', 'DEFAULT'], or the DEFAULT size for each
                        individual benchmark
```
## Generating the full distribution (`gen_all.py`)

While `process.py` generates a single configuration, `gen_all.py` is the top-level
orchestrator that builds, **verifies**, and **synthesizes** the entire benchmark
distribution across every combination of dataset size and data type.

```bash
python gen_all.py -j <N>
```

The only option is `-j/--jobs` (number of parallel jobs, default `1`). The source
release is read from `polybench-c-4.2.1-beta.tar.gz` in the repository root.

For each `(size, data type)` combination it will:

1. **Generate** the HLS-compatible sources by calling `process.py` directly.
2. **Compile and run** each kernel's testbench with the Vitis HLS `clang++`, then
   compare the output against the golden reference, recording per-array error
   metrics (MAE / MSE / RMSE).
3. **Synthesize** each kernel with `vitis_hls` (target part `xc7z020clg484-1`, 10 ns
   clock) and export the synthesis report and an IP catalog.
4. **Package** the results into a `*__build.tar.gz` archive.

By default the build matrix is the cross product of:

* **Sizes:** `MINI`, `SMALL`, `MEDIUM`
* **Data types:** `FLOAT`, `FIXED`

To change which configurations are built, edit the `SIZES` and `DATA_TYPES` lists
near the top of `gen_all.py` (e.g. uncomment `LARGE` / `EXTRALARGE`).

> **Note:** Every run **wipes and recreates the `dist/` directory**. All output is
> written there; back up anything you want to keep first.

### Output

For each configuration, `dist/` will contain (where `<cfg>` is e.g.
`hls_polybench__float__mini`):

| Artifact | Description |
| --- | --- |
| `<cfg>/` | Directory of processed kernels, including verification (`tb_data_hls.txt`, `tb_data_hls_error.json`) and synthesis (`synth_report.zip`, `ip_<kernel>.zip`) artifacts copied into each kernel folder |
| `<cfg>.tar.gz` | Archive of the generated source benchmarks |
| `<cfg>__build.tar.gz` | Archive of the full per-kernel build, including verification and synthesis artifacts |

> **Note:** Any failure (compile, run, output mismatch, or synthesis) raises an
> exception and aborts the run.

## Requirements
Python Packages
* joblib
* pcpp
* numpy

For `gen_all.py` (compilation, verification, and synthesis), a working
[Xilinx Vitis HLS](https://www.xilinx.com/products/design-tools/vitis/vitis-hls.html)
installation must be on your `PATH` (the `vitis_hls` executable and its bundled
`clang++` are located via `which vitis_hls`).