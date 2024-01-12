#include "adi.h"


void kernel_adi(int tsteps, int n,
		t_ap_fixed u[ 60 + 0][60 + 0],
		t_ap_fixed v[ 60 + 0][60 + 0],
		t_ap_fixed p[ 60 + 0][60 + 0],
		t_ap_fixed q[ 60 + 0][60 + 0])
{
  #pragma HLS top name=kernel_adi

  int t, i, j;
  t_ap_fixed DX, DY, DT;
  t_ap_fixed B1, B2;
  t_ap_fixed mul1, mul2;
  t_ap_fixed a, b, c, d, e, f;


  DX = (t_ap_fixed(1.0))/(t_ap_fixed)n;
  DY = (t_ap_fixed(1.0))/(t_ap_fixed)n;
  DT = (t_ap_fixed(1.0))/(t_ap_fixed)tsteps;
  B1 = (t_ap_fixed(2.0));
  B2 = (t_ap_fixed(1.0));
  mul1 = B1 * DT / (DX * DX);
  mul2 = B2 * DT / (DY * DY);

  a = -mul1 /  (t_ap_fixed(2.0));
  b = (t_ap_fixed(1.0))+mul1;
  c = a;
  d = -mul2 / (t_ap_fixed(2.0));
  e = (t_ap_fixed(1.0))+mul2;
  f = d;

 for (t=1; t<=tsteps; t++) {

    for (i=1; i<n-1; i++) {
      v[0][i] = (t_ap_fixed(1.0));
      p[i][0] = (t_ap_fixed(0.0));
      q[i][0] = v[0][i];
      for (j=1; j<n-1; j++) {
        p[i][j] = -c / (a*p[i][j-1]+b);
        q[i][j] = (-d*u[j][i-1]+((t_ap_fixed(1.0))+(t_ap_fixed(2.0))*d)*u[j][i] - f*u[j][i+1]-a*q[i][j-1])/(a*p[i][j-1]+b);
      }

      v[n-1][i] = (t_ap_fixed(1.0));
      for (j=n-2; j>=1; j--) {
        v[j][i] = p[i][j] * v[j+1][i] + q[i][j];
      }
    }

    for (i=1; i<n-1; i++) {
      u[i][0] = (t_ap_fixed(1.0));
      p[i][0] = (t_ap_fixed(0.0));
      q[i][0] = u[i][0];
      for (j=1; j<n-1; j++) {
        p[i][j] = -f / (d*p[i][j-1]+e);
        q[i][j] = (-a*v[i-1][j]+((t_ap_fixed(1.0))+(t_ap_fixed(2.0))*a)*v[i][j] - c*v[i+1][j]-d*q[i][j-1])/(d*p[i][j-1]+e);
      }
      u[i][n-1] = (t_ap_fixed(1.0));
      for (j=n-2; j>=1; j--) {
        u[i][j] = p[i][j] * u[i][j+1] + q[i][j];
      }
    }
  }
}