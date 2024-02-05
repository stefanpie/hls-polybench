## deriche

`deriche` implements the Deriche recursive filter, which is a generic filter that can be used for both edge detection and smoothing [2, 3]. The 2D version takes advantage of the separability and is implemented as horizontal passes followed by vertical passes over an image.
It takes the following as input,

- $x$: $W \times H$ image.
- $\alpha$: A parameter of the filter that is related to the size of the convolution.
- $a_1, \ldots, a_8, b_1, b_2, c_1, c_2$: Coefficients of the filter that determine the behavior of the filter.

and gives the following as output:

- $y$: The processed image. How the image is processed depends on the coefficients used.

The generic 2D implementation reproduced from the original article is as follows:

**Horizontal Pass**

$$
y_1(i, j) = a_1x(i, j) + a_2x(i, j - 1) + b_1y_1(i, j - 1) + b_2y_1(i, j - 2)
$$

$$
y_2(i, j) = a_3x(i, j + 1) + a_4x(i, j + 2) + b_1y_2(i, j + 1) + b_2y_2(i, j + 2)
$$

$$
r(i, j) = c_1(y_1(i, j) + y_2(i, j))
$$

**Vertical Pass**

$$
z_1(i, j) = a_5r(i, j) + a_6r(i - 1, j) + b_1z_1(i - 1, j) + b_2z_1(i - 2, j)
$$

$$
z_2(i, j) = a_7r(i + 1, j) + a_8r(i + 2, j) + b_1z_2(i + 1, j) + b_2z_2(i + 2, j)
$$

$$
y(i, j) = c_2(z_1(i, j) + z_2(i, j))
$$

The C implementation in PolyBench use the following parameters for the filter:

- $\alpha = 0.25$
- $a_1 = a_5 = k$
- $a_2 = a_6 = ke^{-\alpha(\alpha - 1)}$
- $a_3 = a_7 = ke^{-\alpha(\alpha + 1)}$
- $a_4 = a_8 = -ke^{-2\alpha}$
- $b_1 = 2e^{-\alpha}$
- $b_2 = -e^{-2\alpha}$
- $c_1 = c_2 = 1$

where $k$ is computed as

$$
k = \frac{(1 - e^{-\alpha})^2}{1 + 2\alpha e^{-\alpha} - e^{-2\alpha}}
$$

which implements the smoothing filter.