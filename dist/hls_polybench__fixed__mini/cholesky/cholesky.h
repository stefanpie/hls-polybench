#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;

extern "C" {
void kernel_cholesky(
		     t_ap_fixed A[ 40 + 0][40 + 0]);
}