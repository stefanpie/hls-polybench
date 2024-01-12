#include "doitgen.h"


void kernel_doitgen(int nr, int nq, int np,
		    t_ap_fixed A[ 25 + 0][20 + 0][30 + 0],
		    t_ap_fixed C4[ 30 + 0][30 + 0],
		    t_ap_fixed sum[ 30 + 0])
{
  #pragma HLS top name=kernel_doitgen

  int r, q, p, s;

  for (r = 0; r < nr; r++)
    for (q = 0; q < nq; q++)  {
      for (p = 0; p < np; p++)  {
	sum[p] = (t_ap_fixed(0.0));
	for (s = 0; s < np; s++)
	  sum[p] += A[r][q][s] * C4[s][p];
      }
      for (p = 0; p < np; p++)
	A[r][q][p] = sum[p];
    }

}