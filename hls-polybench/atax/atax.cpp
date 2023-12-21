#include "atax.h"


void kernel_atax(int m, int n,
		 t_ap_fixed A[ 390 + 0][410 + 0],
		 t_ap_fixed x[ 410 + 0],
		 t_ap_fixed y[ 410 + 0],
		 t_ap_fixed tmp[ 390 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    y[i] = 0;
  for (i = 0; i < m; i++)
    {
      tmp[i] = (t_ap_fixed)0.0;
      for (j = 0; j < n; j++)
	tmp[i] = tmp[i] + A[i][j] * x[j];
      for (j = 0; j < n; j++)
	y[j] = y[j] + A[i][j] * tmp[i];
    }

}