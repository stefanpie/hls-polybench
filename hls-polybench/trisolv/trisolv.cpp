#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_trisolv(int n,
		    t_ap_fixed L[ 2000 + 0][2000 + 0],
		    t_ap_fixed x[ 2000 + 0],
		    t_ap_fixed b[ 2000 + 0])
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