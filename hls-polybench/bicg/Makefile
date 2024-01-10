CC=/tools/software/xilinx/Vitis_HLS/2023.1/lnx64/tools/clang-3.9/bin/clang++
CFLAGS=-std=c++14 -O3 -g -fPIC -fPIE -lm -Wl,--sysroot=/ -I/tools/software/xilinx/Vitis_HLS/2023.1/include -I/tools/software/xilinx/Vitis_HLS/2023.1/include/etc -I/tools/software/xilinx/Vitis_HLS/2023.1/include/utils
all: bicg
bicg: bicg_tb.cpp bicg.cpp
	$(CC) $^ -o $@ $(CFLAGS)
run: bicg
	./bicg
