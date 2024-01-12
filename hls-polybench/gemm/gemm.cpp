#include "gemm.h"


void kernel_gemm(int ni, int nj, int nk,
		 t_ap_fixed alpha,
		 t_ap_fixed beta,
		 t_ap_fixed C[ 60 + 0][70 + 0],
		 t_ap_fixed A[ 60 + 0][80 + 0],
		 t_ap_fixed B[ 80 + 0][70 + 0])
{
  #pragma HLS top name=kernel_gemm

  int i, j, k;
  for (i = 0; i < ni; i++) {
    for (j = 0; j < nj; j++)
	C[i][j] *= beta;
    for (k = 0; k < nk; k++) {
       for (j = 0; j < nj; j++)
	  C[i][j] += alpha * A[i][k] * B[k][j];
    }
  }

}