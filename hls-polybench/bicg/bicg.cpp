#include "bicg.h"


void kernel_bicg(int m, int n,
		 t_ap_fixed A[ 124 + 0][116 + 0],
		 t_ap_fixed s[ 116 + 0],
		 t_ap_fixed q[ 124 + 0],
		 t_ap_fixed p[ 116 + 0],
		 t_ap_fixed r[ 124 + 0])
{
  int i, j;

  for (i = 0; i < m; i++)
    s[i] = 0;
  for (i = 0; i < n; i++)
    {
      q[i] = (t_ap_fixed(0.0));
      for (j = 0; j < m; j++)
	{
	  s[j] = s[j] + r[i] * A[i][j];
	  q[i] = q[i] + A[i][j] * p[j];
	}
    }

}