#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<48,16> t_ap_fixed;

extern "C" {
void kernel_jacobi_1d(int tsteps,
			    int n,
			    t_ap_fixed A[ 400 + 0],
			    t_ap_fixed B[ 400 + 0]);
}