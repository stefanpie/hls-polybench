#include "doitgen.h"


void kernel_doitgen(  
		    double A[ 10 + 0][8 + 0][12 + 0],
		    double C4[ 12 + 0][12 + 0],
		    double sum[ 12 + 0])
{
  #pragma HLS top name=kernel_doitgen

    const int nr = 10;
    const int nq = 8;
    const int np = 12;

  int r, q, p, s;

  for (r = 0; r < nr; r++)
    for (q = 0; q < nq; q++)  {
      for (p = 0; p < np; p++)  {
	sum[p] = 0.0;
	for (s = 0; s < np; s++)
	  sum[p] += A[r][q][s] * C4[s][p];
      }
      for (p = 0; p < np; p++)
	A[r][q][p] = sum[p];
    }

}