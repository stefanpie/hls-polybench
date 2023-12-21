#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_heat_3d(int tsteps,
		      int n,
		      t_ap_fixed A[ 40 + 0][40 + 0][40 + 0],
		      t_ap_fixed B[ 40 + 0][40 + 0][40 + 0]);
}