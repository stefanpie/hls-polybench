#include "trisolv.h"


void kernel_trisolv(int n,
		    t_ap_fixed L[ 120 + 0][120 + 0],
		    t_ap_fixed x[ 120 + 0],
		    t_ap_fixed b[ 120 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    {
      x[i] = b[i];
      for (j = 0; j <i; j++)
        x[i] -= L[i][j] * x[j];
      x[i] = x[i] / L[i][i];
    }

}