#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

#include "deriche.h"


void init_array (int w, int h, float* alpha,
		 float imgIn[ 720 + 0][480 + 0],
		 float imgOut[ 720 + 0][480 + 0])
{
  int i, j;

  *alpha=0.25;


  for (i = 0; i < w; i++)
     for (j = 0; j < h; j++)
	imgIn[i][j] = (float) ((313*i+991*j)%65536) / 65535.0f;
}


void print_array(int w, int h,
		 float imgOut[ 720 + 0][480 + 0])

{
  int i, j;

  fprintf(stderr, "==BEGIN DUMP_ARRAYS==\n");
  fprintf(stderr, "begin dump: %s", "imgOut");
  for (i = 0; i < w; i++)
    for (j = 0; j < h; j++) {
      if ((i * h + j) % 20 == 0) fprintf(stderr, "\n");
      fprintf(stderr, "%0.6f ", imgOut[i][j]);
    }
  fprintf(stderr, "\nend   dump: %s\n", "imgOut");
  fprintf(stderr, "==END   DUMP_ARRAYS==\n");
}


int main(int argc, char** argv)
{

  int w = 720;
  int h = 480;


  float alpha;
   float imgIn[ 720 + 0][480 + 0];
   float imgOut[ 720 + 0][480 + 0];
   float y1[ 720 + 0][480 + 0];
   float y2[ 720 + 0][480 + 0];


  init_array (w, h, &alpha, imgIn, imgOut);


  kernel_deriche (alpha, imgIn, imgOut, y1, y2);


  print_array(w, h, imgOut);


  return 0;
}