## adi

Alternating Direction Implicit method for 2D heat diffusion. The main strength of ADI over other methods is that it decomposes a 2D problem to two 1D problems, allowing direct solutions to the sub-problems with lower cost. For 2D heat equations, each sub-problem becomes a tridiagonal system of equations.

From a “stencil” point of view, this can be seen as taking the heat equation of the form:

$$
u^{t+1} = f \left(
\begin{array}{ccc}
& u^{t}_{i,j+1} & \\
u^{t}_{i-1,j} & u^{t}_{i,j} & u^{t}_{i+1,j} \\
& u^{t}_{i,j-1} & \\
\end{array}
\right)
$$

and splitting it two steps:

$$
u^{t+\frac{1}{2}} = g(u^{t}_{i+1,j}, u^{t}_{i,j}, u^{t}_{i-1,j})
$$

$$
u^{t+1} = h \left( u^{t+\frac{1}{2}}_{i,j+1}, u^{t+\frac{1}{2}}_{i,j}, u^{t+\frac{1}{2}}_{i,j-1} \right)
$$

The C reference implementation is based on a Fortran code in a paper by Li and Kedem. In this implementation, the coefficients are also computed since the parameters configure the resolution and not the size of the space/time domain.