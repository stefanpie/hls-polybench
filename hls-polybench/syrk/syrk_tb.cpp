#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "syrk.h"


t_ap_fixed C[ 240 + 0][240 + 0];
t_ap_fixed A[ 240 + 0][200 + 0];


void init_array(int n, int m,
		t_ap_fixed *alpha,
		t_ap_fixed *beta,
		t_ap_fixed C[ 240 + 0][240 + 0],
		t_ap_fixed A[ 240 + 0][200 + 0])
{
  int i, j;

  *alpha = (t_ap_fixed(1.5));
  *beta = (t_ap_fixed(1.2));
  for (i = 0; i < n; i++)
    for (j = 0; j < m; j++)
      A[i][j] = (t_ap_fixed) ((i*j+1)%n) / n;
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      C[i][j] = (t_ap_fixed) ((i*j+2)%m) / m;
}


void print_array(int n,
		 t_ap_fixed C[ 240 + 0][240 + 0])
{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "C");
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
	if ((i * n + j) % 20 == 0) fprintf (stderr, "\n");
	fprintf (stderr, "%0.6lf ", (float)C[i][j]);
    }
  fprintf(stderr, "\nend   dump: %s\n", "C");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int n = 240;
  int m = 200;


  t_ap_fixed alpha;
  t_ap_fixed beta;
  
  
  init_array (n, m, &alpha, &beta, C, A);


  kernel_syrk (n, m, alpha, beta, C, A);


  print_array(n, C);


  return 0;
}