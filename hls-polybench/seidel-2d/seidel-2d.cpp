#include "seidel-2d.h"


void kernel_seidel_2d(
		      
		      double A[ 400 + 0][400 + 0])
{
  #pragma HLS top name=kernel_seidel_2d

    const int n = 400;
    const int tsteps = 100;

  int t, i, j;

  for (t = 0; t <= tsteps - 1; t++)
    for (i = 1; i<= n - 2; i++)
      for (j = 1; j <= n - 2; j++)
	A[i][j] = (A[i-1][j-1] + A[i-1][j] + A[i-1][j+1]
		   + A[i][j-1] + A[i][j] + A[i][j+1]
		   + A[i+1][j-1] + A[i+1][j] + A[i+1][j+1])/9.0;

}