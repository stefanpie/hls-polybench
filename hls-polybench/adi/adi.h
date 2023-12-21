#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<48,16> t_ap_fixed;

extern "C" {
void kernel_adi(int tsteps, int n,
		t_ap_fixed u[ 200 + 0][200 + 0],
		t_ap_fixed v[ 200 + 0][200 + 0],
		t_ap_fixed p[ 200 + 0][200 + 0],
		t_ap_fixed q[ 200 + 0][200 + 0]);
}