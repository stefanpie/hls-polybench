#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_bicg(int m, int n,
		 t_ap_fixed A[ 2100 + 0][1900 + 0],
		 t_ap_fixed s[ 1900 + 0],
		 t_ap_fixed q[ 2100 + 0],
		 t_ap_fixed p[ 1900 + 0],
		 t_ap_fixed r[ 2100 + 0])
{
  int i, j;

  for (i = 0; i < m; i++)
    s[i] = 0;
  for (i = 0; i < n; i++)
    {
      q[i] = (t_ap_fixed)0.0;
      for (j = 0; j < m; j++)
	{
	  s[j] = s[j] + r[i] * A[i][j];
	  q[i] = q[i] + A[i][j] * p[j];
	}
    }

}