#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "adi.h"


void init_array (int n,
		 double u[ 200 + 0][200 + 0])
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      {
	u[i][j] =  (double)(i + n-j) / n;
      }
}


void print_array(int n,
		 double u[ 200 + 0][200 + 0])

{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "u");
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
      if ((i * n + j) % 20 == 0) fprintf(stderr, "\n");
      fprintf (stderr, "%0.6lf ", u[i][j]);
    }
  fprintf(stderr, "\nend   dump: %s\n", "u");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int n = 200;
  int tsteps = 100;


   double u[ 200 + 0][200 + 0];
   double v[ 200 + 0][200 + 0];
   double p[ 200 + 0][200 + 0];
   double q[ 200 + 0][200 + 0];


  init_array (n, u);


  kernel_adi ( u, v, p, q);


  print_array(n, u);


  return 0;
}