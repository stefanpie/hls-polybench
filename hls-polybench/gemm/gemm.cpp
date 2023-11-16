#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_gemm(int ni, int nj, int nk,
		 t_ap_fixed alpha,
		 t_ap_fixed beta,
		 t_ap_fixed C[ 1000 + 0][1100 + 0],
		 t_ap_fixed A[ 1000 + 0][1200 + 0],
		 t_ap_fixed B[ 1200 + 0][1100 + 0])
{
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