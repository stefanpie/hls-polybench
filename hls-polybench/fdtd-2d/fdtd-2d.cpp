#include "ap_fixed.h"
#include "hls_math.h"

typedef ap_fixed<32,16> t_ap_fixed;










void kernel_fdtd_2d(int tmax,
		    int nx,
		    int ny,
		    t_ap_fixed ex[ 1000 + 0][1200 + 0],
		    t_ap_fixed ey[ 1000 + 0][1200 + 0],
		    t_ap_fixed hz[ 1000 + 0][1200 + 0],
		    t_ap_fixed _fict_[ 500 + 0])
{
  int t, i, j;


  for(t = 0; t < tmax; t++)
    {
      for (j = 0; j < ny; j++)
	ey[0][j] = _fict_[t];
      for (i = 1; i < nx; i++)
	for (j = 0; j < ny; j++)
	  ey[i][j] = ey[i][j] - (t_ap_fixed)0.5*(hz[i][j]-hz[i-1][j]);
      for (i = 0; i < nx; i++)
	for (j = 1; j < ny; j++)
	  ex[i][j] = ex[i][j] - (t_ap_fixed)0.5*(hz[i][j]-hz[i][j-1]);
      for (i = 0; i < nx - 1; i++)
	for (j = 0; j < ny - 1; j++)
	  hz[i][j] = hz[i][j] - (t_ap_fixed)0.7*  (ex[i][j+1] - ex[i][j] +
				       ey[i+1][j] - ey[i][j]);
    }

}