#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_gemm(int ni, int nj, int nk,
		 t_ap_fixed alpha,
		 t_ap_fixed beta,
		 t_ap_fixed C[ 200 + 0][220 + 0],
		 t_ap_fixed A[ 200 + 0][240 + 0],
		 t_ap_fixed B[ 240 + 0][220 + 0]);
}