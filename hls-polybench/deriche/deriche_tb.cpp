#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "deriche.h"


t_ap_fixed imgIn[ 192 + 0][128 + 0];
t_ap_fixed imgOut[ 192 + 0][128 + 0];
t_ap_fixed y1[ 192 + 0][128 + 0];
t_ap_fixed y2[ 192 + 0][128 + 0];


void init_array (int w, int h, t_ap_fixed* alpha,
		 t_ap_fixed imgIn[ 192 + 0][128 + 0],
		 t_ap_fixed imgOut[ 192 + 0][128 + 0])
{
  int i, j;

  *alpha=(t_ap_fixed(0.25));


  for (i = 0; i < w; i++)
     for (j = 0; j < h; j++)
	imgIn[i][j] = (t_ap_fixed) ((313*i+991*j)%65536) / (t_ap_fixed(65535.0f));
}


void print_array(int w, int h,
		 t_ap_fixed imgOut[ 192 + 0][128 + 0])

{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "imgOut");
  for (i = 0; i < w; i++)
    for (j = 0; j < h; j++) {
      if ((i * h + j) % 20 == 0) fprintf(stderr, "\n");
      fprintf(stderr, "%0.6f ", (float)imgOut[i][j]);
    }
  fprintf(stderr, "\nend   dump: %s\n", "imgOut");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int w = 192;
  int h = 128;


  t_ap_fixed alpha;
   
   
  init_array (w, h, &alpha, imgIn, imgOut);


  kernel_deriche (alpha, imgIn, imgOut, y1, y2);


  print_array(w, h, imgOut);


  return 0;
}