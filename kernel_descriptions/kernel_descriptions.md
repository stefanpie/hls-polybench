# Kernel Descriptions

## covariance

Computes the covariance, a measure from statistics that show how linearly related two variables are.
It takes the following as input,

- `data`: $N \times M$ matrix that represents $N$ data points, each with $M$ attributes,

and gives the following output:

- `cov`: $M \times M$ matrix where the $i,j$-th element is the covariance between $i$ and $j$. The matrix is symmetric.

Covariance is defined to be the mean of the product of deviations for $i$ and $j$:

$$
\text{cov}(i,j) = \frac{\sum_{k=0}^{N-1} ( \text{data}(k,i) - \text{mean}(i) )(\text{data}(k,j) - \text{mean}(j) )}{N - 1}
$$

where

$$
\text{mean}(x) = \frac{\sum_{k=0}^{N-1} \text{data}(k, x)}{N}
$$

Note that the above computes *sample covariance* where the denominator is $N - 1$.

## correlation

Correlation computes the correlation coefficients (Pearson's), which is normalized covariance.
It takes the following as input,

- `data`: $N \times M$ matrix that represents $N$ data points, each with $M$ attributes,

and gives the following as output:

- `corr`: $M \times M$ matrix where the $i,j$-th element is the correlation coefficient between $i$ and $j$. The matrix is symmetric.

Correlation is defined as the following,

$$
\text{corr}(i,j) = \frac{\text{cov}(i,j)}{\text{stddev}(i)\text{stddev}(j)}
$$

where

$$
\text{stddev}(x) = \sqrt{\frac{\sum_{k=0}^{N-1} (\text{data}(k, x) - \text{mean}(x))^2}{N}}
$$

`cov` and `mean` are defined in covariance (1).

(1): However, the denominator when computing covariance is $N$ for correlation.

## gemm

Generalized Matrix Multiply from BLAS.
It takes the following as inputs,

- $\alpha, \beta$: scalars
- $A$: $P \times Q$ matrix
- $B$: $Q \times R$ matrix
- $C$: $P \times R$ matrix

and gives the following as output:

- $C_{out}$: $P \times R$ array, where $C_{out} = \alpha AB + \beta C$

Note that the output $C_{out}$ is to be stored in place of the input array $C$. The BLAS parameters used are `TRANSA = TRANSB = ‘N’`, meaning both $A$ and $B$ are not transposed.

## gemver

Multiple matrix-vector multiplication from updated BLAS. However, it is not part of the current BLAS distribution.
It takes the following as inputs,

- $\alpha, \beta$: scalars
- $A$: $N \times N$ matrix
- $u1, v1, u2, v2, y, z$: vectors of length $N$

and gives the following as outputs:

- $A$: $N \times N$ matrix, where $A = A + u1 \cdot v1^T + u2 \cdot v2^T$
- $x$: vector of length $N$, where $x = \beta A^T y + z$
- $w$: vector of length $N$, where $w = \alpha A x$

## gesummv

Summed matrix-vector multiplications from updated BLAS. However, it is not part of the current BLAS distribution.
It takes the following as inputs,

- $\alpha, \beta$: scalars
- $A, B$: $N \times N$ matrix
- $x$: vector of length $N$

and gives the following as outputs:

- $y$: vector of length $N$, where $y = \alpha Ax + \beta Bx$

## symm

Symmetric matrix multiplication from BLAS.
It takes the following as inputs,

- $\alpha, \beta$: scalars
- $A$: $M \times M$ symmetric matrix
- $B, C$: $M \times N$ matrices

and gives the following as output:

- $C_{\text{out}}$: $M \times N$ matrix, where $C_{\text{out}} = \alpha AB + \beta BC$

Note that the output $C_{\text{out}}$ is to be stored in place of the input array $C$. The matrix $A$ is stored as a triangular matrix in BLAS. The configuration used are `SIDE = 'L'` and `UPLO = 'L'`, meaning the multiplication is from the left, and the symmetric matrix is stored as a lower triangular matrix.

## syrk

Symmetric rank k update from updated BLAS.
It takes the following as inputs,

- $\alpha, \beta$: scalars
- $A$: $N \times M$ matrix
- $C$: $N \times N$ symmetric matrix

and gives the following as output:

- $C_{out}$: $N \times N$ matrix, where $C_{out} = \alpha A A^T + \beta C$

Note that the output $C_{out}$ is to be stored in place of the input array $C$. The matrix $C$ is stored as a triangular matrix in BLAS, and the result is also triangular. The configurations used are `TRANS = 'N'` and `UPLO = 'L'` meaning the $A$ matrix is not transposed, and $C$ matrix stores the symmetric matrix as lower triangular matrix.

## syr2k

Symmetric rank 2k update from updated BLAS.
It takes the following as inputs,

- $\alpha, \beta$: scalars
- $A, B$: $N \times M$ matrices
- $C$: $N \times N$ symmetric matrix

and gives the following as output:

- $C_{out}$: $N \times N$ matrix, where $C_{out} = \alpha AB^T + \alpha BA^T + \beta C$

Note that the output $C_{out}$ is to be stored in place of the input array $C$. The matrix $C$ is stored as a triangular matrix in BLAS, and the result is also triangular. The configurations used are $TRANS = 'N'$ and $UPLO = 'L'$ meaning the $A$ matrix is not transposed, and $

## trmm

Triangular matrix multiplication.
It takes the following as inputs,

- $A$: $N \times N$ lower triangular matrix
- $B$: $N \times N$ matrix

and gives the following as output:

- $B_{out}$: $N \times N$ matrix, where $B_{out} = AB$

Note that the output $B_{out}$ is to be stored in place of the input array $B$. The configurations used are `SIDE = 'L'`, `UPLO = 'L'`, `TRANSA = 'T'`, and `DIAG = 'U'`, meaning the multiplication is from the left, the matrix is lower triangular, untransposed with unit diagonal.

## 2mm

Linear algebra kernel that consists of two matrix multiplications.
It takes the following as inputs,

- $\alpha, \beta$: scalars
- $A: P \times Q$ matrix
- $B: Q \times R$ matrix
- $C: R \times S$ matrix
- $D: P \times S$ matrix

and gives the following as output:

- $E: P \times S$ matrix, where $E = \alpha ABC + \beta D$

## 3mm

Linear algebra kernel that consists of three matrix multiplications.
It takes the following as inputs,

- $A: P \times Q$ matrix
- $B: Q \times R$ matrix
- $C: R \times S$ matrix
- $D: S \times T$ matrix

and gives the following as output:

- $G: P \times T$ matrix, where $G = (A.B).(C.D)$

## atax

Computes $A^T$ times $Ax$.
It takes the following as inputs,

- $A: M \times N$ matrix
- $x$: vector of length $N$

and gives the following as output:

- $y$: vector of length $N$, where $y = A^T(Ax)$

## bicg

Kernel of BiCGSTAB (BiConjugate Gradient STABilized method).
It takes the following as inputs,

- $A: N \times M$ matrix
- $p$: vector of length $M$
- $r$: vector of length $N$

and gives the following as output:

- $q$: vector of length $N$, where $q = Ap$
- $s$: vector of length $M$, where $s = A^Tr$

## doitgen

Kernel of Multiresolution ADaptive NumErical Scientific Simulation (MADNESS). The kernel is taken from the modified version used by You et al.
It takes the following as inputs,

- $A: R \times Q \times S$ array
- $x: P \times S$ array

and gives the following as output:

- $A_{out}: R \times Q \times P$ array

where $A_{out}(r, q, p) = \sum_{s=0}^{S-1} A(r, q, s) x(p, s)$

Note that the output $A_{out}$ is to be stored in place of the input array $A$ in the original code. Although it is not mentioned anywhere, the computation does not make sense if $P \neq S$.

## mvt

Matrix vector multiplication composed with another matrix vector multiplication but with transposed matrix.
It takes the following as inputs,

- $A: N \times N$ matrix
- $y1, y2$: vectors of length $N$

and gives the following as outputs:

- $x1$: vector of length $N$, where $x1 = x1 + Ay1$
- $x2$: vector of length $N$, where $x2 = x2 + A^Ty2$

## cholesky

Cholesky decomposition, which decomposes a matrix to triangular matrices. Only applicable when the input matrix is positive-definite.
It takes the following as input,

- $A: N \times N$ positive-definite matrix

and gives the following as output:

- $L: N \times N$ lower triangular matrix such that $A = LL^T$

The C reference implementation uses CholeskyBanachiewicz algorithm. The algorithm computes the following, where the computation starts from the upper-left corner of $L$ and proceeds row by row.

$$
L(i,j) =
\begin{cases}
\sqrt{A(i, i) - \sum_{k=0}^{i-1} L(i, k)^2} & \text{for } i = j \\
\frac{1}{L(j, j)} \left( A(i, j) - \sum_{k=0}^{j-1} L(i, k)L(j, k) \right) & \text{for } i > j
\end{cases}
$$

## durbin

Durbin is an algorithm for solving Yule-Walker equations, which is a special case of Toeplitz systems.
It takes the following as input,

- $r$: vector of length $N$.

and gives the following as output:

- $y$: vector of length $N$

such that $Ty = -r$ where $T$ is a symmetric, unit-diagonal, Toeplitz matrix defined by the vector $[1,r_0, \ldots ,r_{N-1}]$.
The C reference implementation is a direct implementation of the algorithm described in a book by Golub and Van Loan. The book mentions that a vector can be removed to use less space, but the implementation retains this vector.

## gramschmidt

QR Decomposition with Modified Gram Schmidt.
It takes the following as input,

- $A: M \times N$ rank $N$ matrix ($M \geq N$).

and gives the following as outputs:

- $Q: M \times N$ orthogonal matrix
- $R: N \times N$ upper triangular matrix

such that $A = QR$.
The algorithm is described in a techreport by Walter Gander: `http://www.inf.ethz.ch/personal/gander/`.

## lu

LU decomposition without pivoting.
It takes the following as input,

- $A: N \times N$ matrix

and gives the following as outputs:

- $L: N \times N$ lower triangular matrix
- $U: N \times N$ upper triangular matrix

such that $A = LU$.
L and U are computed as follows:

$$
U(i,j) = A(i,j) - \sum_{k=0}^{i-1} L(i,k)U(k,j)
$$

$$
L(i,j) = \frac{1}{U(j,j)} \left( A(i,j) - \sum_{k=0}^{j-1} L(i,k)U(k,j) \right)
$$

## ludcmp

This kernel solves a system of linear equations using LU decomposition followed by forward and backward substitutions.
It takes the following as inputs,

- $A: N \times N$ matrix
- $b$: vector of length $N$

and gives the following as output:

- $x$: vector of length $N$, where $Ax = b$

The matrix $A$ is first decomposed into $L$ and $U$ using the same algorithm as in `lu`. Then the two triangular systems are solved to find $x$ as follows:

$$
Ax = b \Rightarrow LUx = b \Rightarrow
\begin{cases}
Ly = b \\
Ux = y
\end{cases}
$$

The forward and backward substitutions are as follows:

$$
y(i) = \frac{b(i) - \sum_{j=0}^{i-1} L(i,j)y(j)}{L(i,i)}
$$

$$
x(i) = \frac{y(i) - \sum_{j=0}^{i-1} U(i,j)x(j)}{U(i,i)}
$$

## trisolv

Triangular matrix solver using forward substitution.
It takes the following as inputs,

- $L$: $N \times N$ lower triangular matrix
- $b$: vector of length $N$

and gives the following as output:

- $x$: vector of length $N$, where $Lx = b$

The forward substitution is as follows:

$$
x(i) = \frac{b(i) - \sum_{j=0}^{i-1} L(i, j) \cdot x(j)}{L(i, i)}
$$

## deriche

`deriche` implements the Deriche recursive filter, which is a generic filter that can be used for both edge detection and smoothing [2, 3]. The 2D version takes advantage of the separability and is implemented as horizontal passes followed by vertical passes over an image.
It takes the following as input,

- $x$: $W \times H$ image.
- $\alpha$: A parameter of the filter that is related to the size of the convolution.
- $a_1, \ldots, a_8, b_1, b_2, c_1, c_2$: Coefficients of the filter that determine the behavior of the filter.

and gives the following as output:

- $y$: The processed image. How the image is processed depends on the coefficients used.

The generic 2D implementation reproduced from the original article [3] is as follows:

## Horizontal Pass

$$
y_1(i, j) = a_1x(i, j) + a_2x(i, j - 1) + b_1y_1(i, j - 1) + b_2y_1(i, j - 2)
$$

$$
y_2(i, j) = a_3x(i, j + 1) + a_4x(i, j + 2) + b_1y_2(i, j + 1) + b_2y_2(i, j + 2)
$$

$$
r(i, j) = c_1(y_1(i, j) + y_2(i, j))
$$

## Vertical Pass

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

## floyd-warshall

Floyd-Warshall computes the shortest paths between each pair of nodes in a graph. The following only computes the shortest path lengths, which is a typical use of this method.
It takes the following as input,

- $w$: $N \times N$ matrix, where the $i, j$ entry represents the cost of taking an edge from $i$ to $j$. Set to infinity if there is no edge connecting $i$ to $j$.

and gives the following as output:

- $paths$: $N \times N$ matrix, where the $i, j$ entry represents the shortest path length from $i$ to $j$.

The shortest path lengths are computed recursively as follows:

$$
p(k, i, j) =
\begin{cases}
w(i, j) & \text{if } k = -1 \\
\min(p(k - 1, i, j), p(k - 1, i, k) + p(k - 1, k, j)) & \text{if } 0 \leq k < N
\end{cases}
$$

where the final output $paths(i, j) = p(N - 1, i, j)$.
