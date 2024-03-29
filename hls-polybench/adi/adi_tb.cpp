#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "adi.h"


t_ap_fixed u[ 60 + 0][60 + 0];
t_ap_fixed v[ 60 + 0][60 + 0];
t_ap_fixed p[ 60 + 0][60 + 0];
t_ap_fixed q[ 60 + 0][60 + 0];


void init_array (int n,
		 t_ap_fixed u[ 60 + 0][60 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      {
	u[i][j] =  (t_ap_fixed)(i + n-j) / n;
      }
}


void print_array(int n,
		 t_ap_fixed u[ 60 + 0][60 + 0])

{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "u");
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
      if ((i * n + j) % 20 == 0) fprintf(stderr, "\n");
      fprintf (stderr, "%0.6lf ", (float)u[i][j]);
    }
  fprintf(stderr, "\nend   dump: %s\n", "u");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int n = 60;
  int tsteps = 40;


  init_array (n, u);


  kernel_adi ( u, v, p, q);


  print_array(n, u);


  return 0;
}