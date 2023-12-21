#include "seidel-2d.h"


void kernel_seidel_2d(int tsteps,
		      int n,
		      t_ap_fixed A[ 400 + 0][400 + 0])
{
  int t, i, j;

  for (t = 0; t <= tsteps - 1; t++)
    for (i = 1; i<= n - 2; i++)
      for (j = 1; j <= n - 2; j++)
	A[i][j] = (A[i-1][j-1] + A[i-1][j] + A[i-1][j+1]
		   + A[i][j-1] + A[i][j] + A[i][j+1]
		   + A[i+1][j-1] + A[i+1][j] + A[i+1][j+1])/(t_ap_fixed(9.0));

}