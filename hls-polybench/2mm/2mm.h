#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_2mm(int ni, int nj, int nk, int nl,
		t_ap_fixed alpha,
		t_ap_fixed beta,
		t_ap_fixed tmp[ 180 + 0][190 + 0],
		t_ap_fixed A[ 180 + 0][210 + 0],
		t_ap_fixed B[ 210 + 0][190 + 0],
		t_ap_fixed C[ 190 + 0][220 + 0],
		t_ap_fixed D[ 180 + 0][220 + 0]);
}