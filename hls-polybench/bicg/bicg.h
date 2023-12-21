#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_bicg(int m, int n,
		 t_ap_fixed A[ 410 + 0][390 + 0],
		 t_ap_fixed s[ 390 + 0],
		 t_ap_fixed q[ 410 + 0],
		 t_ap_fixed p[ 390 + 0],
		 t_ap_fixed r[ 410 + 0]);
}