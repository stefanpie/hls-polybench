#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;

extern "C" {
void kernel_deriche(int w, int h, t_ap_fixed alpha,
       t_ap_fixed imgIn[ 192 + 0][128 + 0],
       t_ap_fixed imgOut[ 192 + 0][128 + 0],
       t_ap_fixed y1[ 192 + 0][128 + 0],
       t_ap_fixed y2[ 192 + 0][128 + 0]);
}