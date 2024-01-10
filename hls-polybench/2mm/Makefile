CC=/tools/software/xilinx/Vitis_HLS/2023.1/lnx64/tools/clang-3.9/bin/clang++
CFLAGS=-std=c++14 -O3 -g -fPIC -fPIE -lm -Wl,--sysroot=/ -I/tools/software/xilinx/Vitis_HLS/2023.1/include -I/tools/software/xilinx/Vitis_HLS/2023.1/include/etc -I/tools/software/xilinx/Vitis_HLS/2023.1/include/utils
all: 2mm
2mm: 2mm_tb.cpp 2mm.cpp
	$(CC) $^ -o $@ $(CFLAGS)
run: 2mm
	./2mm
