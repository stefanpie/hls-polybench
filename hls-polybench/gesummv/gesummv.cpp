#include "gesummv.h"


void kernel_gesummv(int n,
		    t_ap_fixed alpha,
		    t_ap_fixed beta,
		    t_ap_fixed A[ 250 + 0][250 + 0],
		    t_ap_fixed B[ 250 + 0][250 + 0],
		    t_ap_fixed tmp[ 250 + 0],
		    t_ap_fixed x[ 250 + 0],
		    t_ap_fixed y[ 250 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    {
      tmp[i] = (t_ap_fixed(0.0));
      y[i] = (t_ap_fixed(0.0));
      for (j = 0; j < n; j++)
	{
	  tmp[i] = A[i][j] * x[j] + tmp[i];
	  y[i] = B[i][j] * x[j] + y[i];
	}
      y[i] = alpha * tmp[i] + beta * y[i];
    }

}