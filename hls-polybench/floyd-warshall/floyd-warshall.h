#pragma once
#include "ap_fixed.h"
#include "hls_math.h"


extern "C" {
void kernel_floyd_warshall(int n,
			   int path[ 180 + 0][180 + 0]);
}