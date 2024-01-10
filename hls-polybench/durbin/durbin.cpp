#include "durbin.h"


void kernel_durbin(int n,
		   t_ap_fixed r[ 120 + 0],
		   t_ap_fixed y[ 120 + 0])
{
 t_ap_fixed z[120];
 t_ap_fixed alpha;
 t_ap_fixed beta;
 t_ap_fixed sum;

 int i,k;

 y[0] = -r[0];
 beta = (t_ap_fixed(1.0));
 alpha = -r[0];

 for (k = 1; k < n; k++) {
   beta = (1-alpha*alpha)*beta;
   sum = (t_ap_fixed(0.0));
   for (i=0; i<k; i++) {
      sum += r[k-i-1]*y[i];
   }
   alpha = - (r[k] + sum)/beta;

   for (i=0; i<k; i++) {
      z[i] = y[i] + alpha*y[k-i-1];
   }
   for (i=0; i<k; i++) {
     y[i] = z[i];
   }
   y[k] = alpha;
 }

}