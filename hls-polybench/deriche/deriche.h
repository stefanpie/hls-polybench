#pragma once
#include <cmath>


extern "C" {
void kernel_deriche(  float alpha,
       float imgIn[ 720 + 0][480 + 0],
       float imgOut[ 720 + 0][480 + 0],
       float y1[ 720 + 0][480 + 0],
       float y2[ 720 + 0][480 + 0]);
}