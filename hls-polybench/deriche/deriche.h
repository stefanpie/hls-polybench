#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<48,16> t_ap_fixed;

extern "C" {
void kernel_deriche(int w, int h, t_ap_fixed alpha,
       t_ap_fixed imgIn[ 720 + 0][480 + 0],
       t_ap_fixed imgOut[ 720 + 0][480 + 0],
       t_ap_fixed y1[ 720 + 0][480 + 0],
       t_ap_fixed y2[ 720 + 0][480 + 0]);
}