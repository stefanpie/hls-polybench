#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_syr2k(int n, int m,
		  t_ap_fixed alpha,
		  t_ap_fixed beta,
		  t_ap_fixed C[ 1200 + 0][1200 + 0],
		  t_ap_fixed A[ 1200 + 0][1000 + 0],
		  t_ap_fixed B[ 1200 + 0][1000 + 0])
{
  int i, j, k;
  for (i = 0; i < n; i++) {
    for (j = 0; j <= i; j++)
      C[i][j] *= beta;
    for (k = 0; k < m; k++)
      for (j = 0; j <= i; j++)
	{
	  C[i][j] += A[j][k]*alpha*B[i][k] + B[j][k]*alpha*A[i][k];
	}
  }

}