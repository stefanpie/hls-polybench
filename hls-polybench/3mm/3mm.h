#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_3mm(int ni, int nj, int nk, int nl, int nm,
		t_ap_fixed E[ 180 + 0][190 + 0],
		t_ap_fixed A[ 180 + 0][200 + 0],
		t_ap_fixed B[ 200 + 0][190 + 0],
		t_ap_fixed F[ 190 + 0][210 + 0],
		t_ap_fixed C[ 190 + 0][220 + 0],
		t_ap_fixed D[ 220 + 0][210 + 0],
		t_ap_fixed G[ 180 + 0][210 + 0]);
}