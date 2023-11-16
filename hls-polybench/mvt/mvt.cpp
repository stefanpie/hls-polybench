#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_mvt(int n,
		t_ap_fixed x1[ 2000 + 0],
		t_ap_fixed x2[ 2000 + 0],
		t_ap_fixed y_1[ 2000 + 0],
		t_ap_fixed y_2[ 2000 + 0],
		t_ap_fixed A[ 2000 + 0][2000 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      x1[i] = x1[i] + A[i][j] * y_1[j];
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      x2[i] = x2[i] + A[j][i] * y_2[j];

}