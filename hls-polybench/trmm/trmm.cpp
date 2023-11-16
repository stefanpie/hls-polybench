#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_trmm(int m, int n,
		 t_ap_fixed alpha,
		 t_ap_fixed A[ 1000 + 0][1000 + 0],
		 t_ap_fixed B[ 1000 + 0][1200 + 0])
{
  int i, j, k;
  for (i = 0; i < m; i++)
     for (j = 0; j < n; j++) {
        for (k = i+1; k < m; k++)
           B[i][j] += A[k][i] * B[k][j];
        B[i][j] = alpha * B[i][j];
     }

}