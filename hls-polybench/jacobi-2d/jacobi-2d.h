#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<48,16> t_ap_fixed;

extern "C" {
void kernel_jacobi_2d(int tsteps,
			    int n,
			    t_ap_fixed A[ 250 + 0][250 + 0],
			    t_ap_fixed B[ 250 + 0][250 + 0]);
}