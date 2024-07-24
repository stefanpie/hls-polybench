#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "correlation.h"


void init_array (int m,
		 int n,
		 double *float_n,
		 double data[ 100 + 0][80 + 0])
{
  int i, j;

  *float_n = (double)100;

  for (i = 0; i < 100; i++)
    for (j = 0; j < 80; j++)
      data[i][j] = (double)(i*j)/80 + i;

}


void print_array(int m,
		 double corr[ 80 + 0][80 + 0])

{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "corr");
  for (i = 0; i < m; i++)
    for (j = 0; j < m; j++) {
      if ((i * m + j) % 20 == 0) fprintf (stderr, "\n");
      fprintf (stderr, "%0.6lf ", corr[i][j]);
    }
  fprintf(stderr, "\nend   dump: %s\n", "corr");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int n = 100;
  int m = 80;


  double float_n;
  double data[ 100 + 0][80 + 0];
  double corr[ 80 + 0][80 + 0];
  double mean[ 80 + 0];
  double stddev[ 80 + 0];


  init_array (m, n, &float_n, data);


  kernel_correlation ( float_n,
		      data,
		      corr,
		      mean,
		      stddev);


  print_array(m, corr);


  return 0;
}