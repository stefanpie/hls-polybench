#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<48,16> t_ap_fixed;

extern "C" {
void kernel_mvt(int n,
		t_ap_fixed x1[ 400 + 0],
		t_ap_fixed x2[ 400 + 0],
		t_ap_fixed y_1[ 400 + 0],
		t_ap_fixed y_2[ 400 + 0],
		t_ap_fixed A[ 400 + 0][400 + 0]);
}