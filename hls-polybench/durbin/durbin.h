#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;

extern "C" {
void kernel_durbin(int n,
		   t_ap_fixed r[ 120 + 0],
		   t_ap_fixed y[ 120 + 0]);
}