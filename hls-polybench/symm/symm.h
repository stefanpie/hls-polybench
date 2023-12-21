#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<48,16> t_ap_fixed;

extern "C" {
void kernel_symm(int m, int n,
		 t_ap_fixed alpha,
		 t_ap_fixed beta,
		 t_ap_fixed C[ 200 + 0][240 + 0],
		 t_ap_fixed A[ 200 + 0][200 + 0],
		 t_ap_fixed B[ 200 + 0][240 + 0]);
}