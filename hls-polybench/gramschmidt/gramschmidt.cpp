#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;












void kernel_gramschmidt(int m, int n,
			t_ap_fixed A[ 1000 + 0][1200 + 0],
			t_ap_fixed R[ 1200 + 0][1200 + 0],
			t_ap_fixed Q[ 1000 + 0][1200 + 0])
{
  int i, j, k;

  t_ap_fixed nrm;

  for (k = 0; k < n; k++)
    {
      nrm = (t_ap_fixed)0.0;
      for (i = 0; i < m; i++)
        nrm += A[i][k] * A[i][k];
      R[k][k] = hls::sqrt(nrm);
      for (i = 0; i < m; i++)
        Q[i][k] = A[i][k] / R[k][k];
      for (j = k + 1; j < n; j++)
	{
	  R[k][j] = (t_ap_fixed)0.0;
	  for (i = 0; i < m; i++)
	    R[k][j] += Q[i][k] * A[i][j];
	  for (i = 0; i < m; i++)
	    A[i][j] = A[i][j] - Q[i][k] * R[k][j];
	}
    }

}