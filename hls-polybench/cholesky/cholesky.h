#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;

extern "C" {
void kernel_cholesky(int n,
		     t_ap_fixed A[ 120 + 0][120 + 0]);
}