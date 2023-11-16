#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_atax(int m, int n,
		 t_ap_fixed A[ 1900 + 0][2100 + 0],
		 t_ap_fixed x[ 2100 + 0],
		 t_ap_fixed y[ 2100 + 0],
		 t_ap_fixed tmp[ 1900 + 0])
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