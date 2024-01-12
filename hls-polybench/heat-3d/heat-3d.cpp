#include "heat-3d.h"


void kernel_heat_3d(int tsteps,
		      int n,
		      t_ap_fixed A[ 20 + 0][20 + 0][20 + 0],
		      t_ap_fixed B[ 20 + 0][20 + 0][20 + 0])
{
  #pragma HLS top name=kernel_heat_3d

  int t, i, j, k;

    for (t = 1; t <= 40; t++) {
        for (i = 1; i < n-1; i++) {
            for (j = 1; j < n-1; j++) {
                for (k = 1; k < n-1; k++) {
                    B[i][j][k] =   (t_ap_fixed(0.125)) * (A[i+1][j][k] - (t_ap_fixed(2.0)) * A[i][j][k] + A[i-1][j][k])
                                 + (t_ap_fixed(0.125)) * (A[i][j+1][k] - (t_ap_fixed(2.0)) * A[i][j][k] + A[i][j-1][k])
                                 + (t_ap_fixed(0.125)) * (A[i][j][k+1] - (t_ap_fixed(2.0)) * A[i][j][k] + A[i][j][k-1])
                                 + A[i][j][k];
                }
            }
        }
        for (i = 1; i < n-1; i++) {
           for (j = 1; j < n-1; j++) {
               for (k = 1; k < n-1; k++) {
                   A[i][j][k] =   (t_ap_fixed(0.125)) * (B[i+1][j][k] - (t_ap_fixed(2.0)) * B[i][j][k] + B[i-1][j][k])
                                + (t_ap_fixed(0.125)) * (B[i][j+1][k] - (t_ap_fixed(2.0)) * B[i][j][k] + B[i][j-1][k])
                                + (t_ap_fixed(0.125)) * (B[i][j][k+1] - (t_ap_fixed(2.0)) * B[i][j][k] + B[i][j][k-1])
                                + B[i][j][k];
               }
           }
       }
    }

}