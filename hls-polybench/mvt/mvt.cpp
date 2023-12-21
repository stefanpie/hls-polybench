#include "mvt.h"


void kernel_mvt(int n,
		t_ap_fixed x1[ 400 + 0],
		t_ap_fixed x2[ 400 + 0],
		t_ap_fixed y_1[ 400 + 0],
		t_ap_fixed y_2[ 400 + 0],
		t_ap_fixed A[ 400 + 0][400 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      x1[i] = x1[i] + A[i][j] * y_1[j];
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      x2[i] = x2[i] + A[j][i] * y_2[j];

}