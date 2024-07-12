#include "floyd-warshall.h"


void kernel_floyd_warshall(
			   int path[ 500 + 0][500 + 0])
{
  #pragma HLS top name=kernel_floyd_warshall

    const int n = 500;

  int i, j, k;

  for (k = 0; k < n; k++)
    {
      for(i = 0; i < n; i++)
	for (j = 0; j < n; j++)
	  path[i][j] = path[i][j] < path[i][k] + path[k][j] ?
	    path[i][j] : path[i][k] + path[k][j];
    }

}