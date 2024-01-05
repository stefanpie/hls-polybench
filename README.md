# HLS-Polybench

This project aims to provide automation tools to have a reproducible way to generate "HLS compatible" versions of all the polybench kernels with their respective testbenches from the original official polybench distribution.

The generated kernels should be compatible with the Xilinx Vitis HLS tool. All `float` and `double` types are converted to fixed-point types using `ap_fixed` type from the Vitis HLS. All `int` or `uint`.

The automation is done using source code text processing and manipulation using custom Python functions and a Python-based C preprocessor.
