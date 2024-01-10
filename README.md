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
