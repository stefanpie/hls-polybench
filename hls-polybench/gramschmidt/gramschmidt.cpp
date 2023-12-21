#include "gramschmidt.h"


void kernel_gramschmidt(int m, int n,
			t_ap_fixed A[ 200 + 0][240 + 0],
			t_ap_fixed R[ 240 + 0][240 + 0],
			t_ap_fixed Q[ 200 + 0][240 + 0])
{
  int i, j, k;

  t_ap_fixed nrm;


  const t_ap_fixed eps = hls::nextafter(t_ap_fixed(0.0), t_ap_fixed(1.0));

  for (k = 0; k < n; k++)
    {
      nrm = (t_ap_fixed(0.0));
      for (i = 0; i < m; i++)
        nrm += A[i][k] * A[i][k];
      R[k][k] = hls::sqrt(nrm);
      if (R[k][k] == t_ap_fixed(0.0)) R[k][k] += eps;
      for (i = 0; i < m; i++)
        Q[i][k] = A[i][k] / R[k][k];
      for (j = k + 1; j < n; j++)
	{
	  R[k][j] = (t_ap_fixed(0.0));
	  for (i = 0; i < m; i++)
	    R[k][j] += Q[i][k] * A[i][j];
	  for (i = 0; i < m; i++)
	    A[i][j] = A[i][j] - Q[i][k] * R[k][j];
	}
    }

}