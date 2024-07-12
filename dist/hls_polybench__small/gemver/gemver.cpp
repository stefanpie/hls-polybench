#include "gemver.h"


void kernel_gemver(
		   double alpha,
		   double beta,
		   double A[ 120 + 0][120 + 0],
		   double u1[ 120 + 0],
		   double v1[ 120 + 0],
		   double u2[ 120 + 0],
		   double v2[ 120 + 0],
		   double w[ 120 + 0],
		   double x[ 120 + 0],
		   double y[ 120 + 0],
		   double z[ 120 + 0])
{
  #pragma HLS top name=kernel_gemver

    const int n = 120;

  int i, j;


  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      A[i][j] = A[i][j] + u1[i] * v1[j] + u2[i] * v2[j];

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      x[i] = x[i] + beta * A[j][i] * y[j];

  for (i = 0; i < n; i++)
    x[i] = x[i] + z[i];

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      w[i] = w[i] +  alpha * A[i][j] * x[j];

}