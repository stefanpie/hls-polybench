#include "jacobi-2d.h"


void kernel_jacobi_2d(int tsteps,
			    int n,
			    t_ap_fixed A[ 250 + 0][250 + 0],
			    t_ap_fixed B[ 250 + 0][250 + 0])
{
  int t, i, j;

  for (t = 0; t < tsteps; t++)
    {
      for (i = 1; i < n - 1; i++)
	for (j = 1; j < n - 1; j++)
	  B[i][j] = (t_ap_fixed)0.2 * (A[i][j] + A[i][j-1] + A[i][1+j] + A[1+i][j] + A[i-1][j]);
      for (i = 1; i < n - 1; i++)
	for (j = 1; j < n - 1; j++)
	  A[i][j] = (t_ap_fixed)0.2 * (B[i][j] + B[i][j-1] + B[i][1+j] + B[1+i][j] + B[i-1][j]);
    }

}