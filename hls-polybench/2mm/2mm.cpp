#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_2mm(int ni, int nj, int nk, int nl,
		t_ap_fixed alpha,
		t_ap_fixed beta,
		t_ap_fixed tmp[ 800 + 0][900 + 0],
		t_ap_fixed A[ 800 + 0][1100 + 0],
		t_ap_fixed B[ 1100 + 0][900 + 0],
		t_ap_fixed C[ 900 + 0][1200 + 0],
		t_ap_fixed D[ 800 + 0][1200 + 0])
{
  int i, j, k;


  for (i = 0; i < ni; i++)
    for (j = 0; j < nj; j++)
      {
	tmp[i][j] = (t_ap_fixed)0.0;
	for (k = 0; k < nk; ++k)
	  tmp[i][j] += alpha * A[i][k] * B[k][j];
      }
  for (i = 0; i < ni; i++)
    for (j = 0; j < nl; j++)
      {
	D[i][j] *= beta;
	for (k = 0; k < nj; ++k)
	  D[i][j] += tmp[i][k] * C[k][j];
      }

}