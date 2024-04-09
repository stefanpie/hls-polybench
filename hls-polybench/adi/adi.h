#pragma once
#include <cmath>


extern "C" {
void kernel_adi( 
		double u[ 200 + 0][200 + 0],
		double v[ 200 + 0][200 + 0],
		double p[ 200 + 0][200 + 0],
		double q[ 200 + 0][200 + 0]);
}