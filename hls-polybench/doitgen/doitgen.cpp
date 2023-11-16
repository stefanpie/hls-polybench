#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_doitgen(int nr, int nq, int np,
		    t_ap_fixed A[ 150 + 0][140 + 0][160 + 0],
		    t_ap_fixed C4[ 160 + 0][160 + 0],
		    t_ap_fixed sum[ 160 + 0])
{
  int r, q, p, s;

  for (r = 0; r < nr; r++)
    for (q = 0; q < nq; q++)  {
      for (p = 0; p < np; p++)  {
	sum[p] = (t_ap_fixed)0.0;
	for (s = 0; s < np; s++)
	  sum[p] += A[r][q][s] * C4[s][p];
      }
      for (p = 0; p < np; p++)
	A[r][q][p] = sum[p];
    }

}