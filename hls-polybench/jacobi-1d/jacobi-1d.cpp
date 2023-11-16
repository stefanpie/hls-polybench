#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_jacobi_1d(int tsteps,
			    int n,
			    t_ap_fixed A[ 2000 + 0],
			    t_ap_fixed B[ 2000 + 0])
{
  int t, i;

  for (t = 0; t < tsteps; t++)
    {
      for (i = 1; i < n - 1; i++)
	B[i] = (t_ap_fixed)0.33333 * (A[i-1] + A[i] + A[i + 1]);
      for (i = 1; i < n - 1; i++)
	A[i] = (t_ap_fixed)0.33333 * (B[i-1] + B[i] + B[i + 1]);
    }

}