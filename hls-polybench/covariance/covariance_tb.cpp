#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "covariance.h"


t_ap_fixed data[ 100 + 0][80 + 0];
t_ap_fixed cov[ 80 + 0][80 + 0];
t_ap_fixed mean[ 80 + 0];


void init_array (int m, int n,
		 t_ap_fixed *float_n,
		 t_ap_fixed data[ 100 + 0][80 + 0])
{
  int i, j;

  *float_n = (t_ap_fixed)n;

  for (i = 0; i < 100; i++)
    for (j = 0; j < 80; j++)
      data[i][j] = t_ap_fixed(i*j) / t_ap_fixed(80.0);
}


void print_array(int m,
		 t_ap_fixed cov[ 80 + 0][80 + 0])

{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "cov");
  for (i = 0; i < m; i++)
    for (j = 0; j < m; j++) {
      if ((i * m + j) % 20 == 0) fprintf (stderr, "\n");
      fprintf (stderr, "%0.6lf ", (float)cov[i][j]);
    }
  fprintf(stderr, "\nend   dump: %s\n", "cov");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int n = 100;
  int m = 80;


  t_ap_fixed float_n;
  
  
  init_array (m, n, &float_n, data);


  kernel_covariance (m, n, float_n,
		     data,
		     cov,
		     mean);


  print_array(m, cov);


  return 0;
}