#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_seidel_2d(int tsteps,
		      int n,
		      t_ap_fixed A[ 400 + 0][400 + 0]);
}