#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_gemver(int n,
		   t_ap_fixed alpha,
		   t_ap_fixed beta,
		   t_ap_fixed A[ 2000 + 0][2000 + 0],
		   t_ap_fixed u1[ 2000 + 0],
		   t_ap_fixed v1[ 2000 + 0],
		   t_ap_fixed u2[ 2000 + 0],
		   t_ap_fixed v2[ 2000 + 0],
		   t_ap_fixed w[ 2000 + 0],
		   t_ap_fixed x[ 2000 + 0],
		   t_ap_fixed y[ 2000 + 0],
		   t_ap_fixed z[ 2000 + 0])
{
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