#include "covariance.h"


void kernel_covariance( 
		       double float_n,
		       double data[ 32 + 0][28 + 0],
		       double cov[ 28 + 0][28 + 0],
		       double mean[ 28 + 0])
{
  #pragma HLS top name=kernel_covariance

    const int n = 32;
    const int m = 28;

  int i, j, k;

  for (j = 0; j < m; j++)
    {
      mean[j] = 0.0;
      for (i = 0; i < n; i++)
        mean[j] += data[i][j];
      mean[j] /= float_n;
    }

  for (i = 0; i < n; i++)
    for (j = 0; j < m; j++)
      data[i][j] -= mean[j];

  for (i = 0; i < m; i++)
    for (j = i; j < m; j++)
      {
        cov[i][j] = 0.0;
        for (k = 0; k < n; k++)
	  cov[i][j] += data[k][i] * data[k][j];
        cov[i][j] /= (float_n - 1.0);
        cov[j][i] = cov[i][j];
      }

}