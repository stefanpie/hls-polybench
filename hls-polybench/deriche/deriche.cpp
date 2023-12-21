#include "deriche.h"


void kernel_deriche(int w, int h, t_ap_fixed alpha,
       t_ap_fixed imgIn[ 720 + 0][480 + 0],
       t_ap_fixed imgOut[ 720 + 0][480 + 0],
       t_ap_fixed y1[ 720 + 0][480 + 0],
       t_ap_fixed y2[ 720 + 0][480 + 0]) {
    int i,j;
    t_ap_fixed xm1, tm1, ym1, ym2;
    t_ap_fixed xp1, xp2;
    t_ap_fixed tp1, tp2;
    t_ap_fixed yp1, yp2;

    t_ap_fixed k;
    t_ap_fixed a1, a2, a3, a4, a5, a6, a7, a8;
    t_ap_fixed b1, b2, c1, c2;

   k = ((t_ap_fixed)1.0-hls::exp(-alpha))*((t_ap_fixed)1.0-hls::exp(-alpha))/((t_ap_fixed)1.0+(t_ap_fixed)2.0*alpha*hls::exp(-alpha)-hls::exp((t_ap_fixed)2.0*alpha));
   a1 = a5 = k;
   a2 = a6 = k*hls::exp(-alpha)*(alpha-(t_ap_fixed)1.0);
   a3 = a7 = k*hls::exp(-alpha)*(alpha+(t_ap_fixed)1.0);
   a4 = a8 = -k*hls::exp(-(t_ap_fixed)2.0*alpha);
   b1 =  hls::pow((t_ap_fixed)((t_ap_fixed)2.0),(t_ap_fixed)(-alpha));
   b2 = -hls::exp(-(t_ap_fixed)2.0*alpha);
   c1 = c2 = 1;

   for (i=0; i<w; i++) {
        ym1 = (t_ap_fixed)0.0;
        ym2 = (t_ap_fixed)0.0;
        xm1 = (t_ap_fixed)0.0;
        for (j=0; j<h; j++) {
            y1[i][j] = a1*imgIn[i][j] + a2*xm1 + b1*ym1 + b2*ym2;
            xm1 = imgIn[i][j];
            ym2 = ym1;
            ym1 = y1[i][j];
        }
    }

    for (i=0; i<w; i++) {
        yp1 = (t_ap_fixed)0.0;
        yp2 = (t_ap_fixed)0.0;
        xp1 = (t_ap_fixed)0.0;
        xp2 = (t_ap_fixed)0.0;
        for (j=h-1; j>=0; j--) {
            y2[i][j] = a3*xp1 + a4*xp2 + b1*yp1 + b2*yp2;
            xp2 = xp1;
            xp1 = imgIn[i][j];
            yp2 = yp1;
            yp1 = y2[i][j];
        }
    }

    for (i=0; i<w; i++)
        for (j=0; j<h; j++) {
            imgOut[i][j] = c1 * (y1[i][j] + y2[i][j]);
        }

    for (j=0; j<h; j++) {
        tm1 = (t_ap_fixed)0.0;
        ym1 = (t_ap_fixed)0.0;
        ym2 = (t_ap_fixed)0.0;
        for (i=0; i<w; i++) {
            y1[i][j] = a5*imgOut[i][j] + a6*tm1 + b1*ym1 + b2*ym2;
            tm1 = imgOut[i][j];
            ym2 = ym1;
            ym1 = y1 [i][j];
        }
    }


    for (j=0; j<h; j++) {
        tp1 = (t_ap_fixed)0.0;
        tp2 = (t_ap_fixed)0.0;
        yp1 = (t_ap_fixed)0.0;
        yp2 = (t_ap_fixed)0.0;
        for (i=w-1; i>=0; i--) {
            y2[i][j] = a7*tp1 + a8*tp2 + b1*yp1 + b2*yp2;
            tp2 = tp1;
            tp1 = imgOut[i][j];
            yp2 = yp1;
            yp1 = y2[i][j];
        }
    }

    for (i=0; i<w; i++)
        for (j=0; j<h; j++)
            imgOut[i][j] = c2*(y1[i][j] + y2[i][j]);

}