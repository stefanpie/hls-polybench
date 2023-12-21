#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,20> t_ap_fixed;

extern "C" {
void kernel_gramschmidt(int m, int n,
			t_ap_fixed A[ 200 + 0][240 + 0],
			t_ap_fixed R[ 240 + 0][240 + 0],
			t_ap_fixed Q[ 200 + 0][240 + 0]);
}