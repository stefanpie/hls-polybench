#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "cholesky.h"


t_ap_fixed B[ 400 + 0][400 + 0];
t_ap_fixed A[ 400 + 0][400 + 0];


void init_array(int n,
		t_ap_fixed A[ 400 + 0][400 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    {
      for (j = 0; j <= i; j++)
	A[i][j] = (t_ap_fixed)(-j % n) / n + 1;
      for (j = i+1; j < n; j++) {
	A[i][j] = 0;
      }
      A[i][i] = 1;
    }


  int r,s,t;
   
  for (r = 0; r < n; ++r)
    for (s = 0; s < n; ++s)
      B[r][s] = 0;
  for (t = 0; t < n; ++t)
    for (r = 0; r < n; ++r)
      for (s = 0; s < n; ++s)
	B[r][s] += A[r][t] * A[s][t];
    for (r = 0; r < n; ++r)
      for (s = 0; s < n; ++s)
	A[r][s] = B[r][s];

}


void print_array(int n,
		 t_ap_fixed A[ 400 + 0][400 + 0])

{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "A");
  for (i = 0; i < n; i++)
    for (j = 0; j <= i; j++) {
    if ((i * n + j) % 20 == 0) fprintf (stderr, "\n");
    fprintf (stderr, "%0.6lf ", (float)A[i][j]);
  }
  fprintf(stderr, "\nend   dump: %s\n", "A");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int n = 400;


  init_array (n, A);


  kernel_cholesky (n, A);


  print_array(n, A);


  return 0;
}