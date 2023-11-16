#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_3mm(int ni, int nj, int nk, int nl, int nm,
		t_ap_fixed E[ 800 + 0][900 + 0],
		t_ap_fixed A[ 800 + 0][1000 + 0],
		t_ap_fixed B[ 1000 + 0][900 + 0],
		t_ap_fixed F[ 900 + 0][1100 + 0],
		t_ap_fixed C[ 900 + 0][1200 + 0],
		t_ap_fixed D[ 1200 + 0][1100 + 0],
		t_ap_fixed G[ 800 + 0][1100 + 0])
{
  int i, j, k;


  for (i = 0; i < ni; i++)
    for (j = 0; j < nj; j++)
      {
	E[i][j] = (t_ap_fixed)0.0;
	for (k = 0; k < nk; ++k)
	  E[i][j] += A[i][k] * B[k][j];
      }

  for (i = 0; i < nj; i++)
    for (j = 0; j < nl; j++)
      {
	F[i][j] = (t_ap_fixed)0.0;
	for (k = 0; k < nm; ++k)
	  F[i][j] += C[i][k] * D[k][j];
      }

  for (i = 0; i < ni; i++)
    for (j = 0; j < nl; j++)
      {
	G[i][j] = (t_ap_fixed)0.0;
	for (k = 0; k < nj; ++k)
	  G[i][j] += E[i][k] * F[k][j];
      }

}