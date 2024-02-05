#pragma once
#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;

extern "C" {
void kernel_adi( 
		t_ap_fixed u[ 60 + 0][60 + 0],
		t_ap_fixed v[ 60 + 0][60 + 0],
		t_ap_fixed p[ 60 + 0][60 + 0],
		t_ap_fixed q[ 60 + 0][60 + 0]);
}