#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_fdtd_2d(int tmax,
		    int nx,
		    int ny,
		    t_ap_fixed ex[ 200 + 0][240 + 0],
		    t_ap_fixed ey[ 200 + 0][240 + 0],
		    t_ap_fixed hz[ 200 + 0][240 + 0],
		    t_ap_fixed _fict_[ 100 + 0]);
}