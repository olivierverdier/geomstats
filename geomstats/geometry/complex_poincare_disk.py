"""The complex Poincaré disk manifold.

The Poincaré complex disk is a representation of the Hyperbolic space of dimension 2.

Lead author: Yann Cabanes.

References
----------
.. [Cabanes2022] Yann Cabanes. Multidimensional complex stationary
    centered Gaussian autoregressive time series machine learning
    in Poincaré and Siegel disks: application for audio and radar
    clutter classification, PhD thesis, 2022
.. [JV2016] B. Jeuris and R. Vandebril. The Kahler mean of Block-Toeplitz
    matrices with Toeplitz structured blocks, 2016.
    https://epubs.siam.org/doi/pdf/10.1137/15M102112X
.. [Yang2013] Marc Arnaudon, Frédéric Barbaresco and Le Yang.
    Riemannian medians and means with applications to radar signal processing,
    IEEE Journal of Selected Topics in Signal Processing, vol. 7, no. 4, pp. 595-604,
    Aug. 2013, doi: 10.1109/JSTSP.2013.2261798.
    https://ieeexplore.ieee.org/document/6514112
"""

import geomstats.backend as gs
from geomstats.geometry.base import ComplexOpenSet
from geomstats.geometry.complex_riemannian_metric import ComplexRiemannianMetric
from geomstats.geometry.hermitian import Hermitian


class ComplexPoincareDisk(ComplexOpenSet):
    """Class for the complex Poincaré disk.

    The Poincaré disk is a representation of the Hyperbolic
    space of dimension 2. Its complex dimension is 1.

    Parameters
    ----------
    scale : int or float
        Scale of the complex Poincaré metric.
        Optional, default: 1.
    """

    def __init__(self, scale=1, **kwargs):
        super().__init__(
            dim=1,
            embedding_space=Hermitian(dim=1),
            metric=ComplexPoincareDiskMetric(scale=scale),
            **kwargs
        )
        self.scale = scale

    @staticmethod
    def belongs(point, atol=gs.atol):
        """Check if a point belongs to the complex unit disk.

        Check if a point belongs to the Poincaré complex disk,
        i.e. Check if its norm is lower than one.

        Parameters
        ----------
        point : array-like, shape=[..., 1]
            Point to be checked.
        atol : float
            Tolerance.
            Optional, default: backend atol.

        Returns
        -------
        belongs : array-like, shape=[...,]
            Boolean denoting if point belongs to the
            complex Poincaré disk.
        """
        point_shape = point.shape
        is_scalar = len(point_shape) == 1
        is_scalar = is_scalar or (len(point_shape) == 2 and point_shape[1] == 1)
        has_modulus_lower_than_one = gs.array(
            [[gs.all(gs.abs(point[i_point]) < 1)] for i_point in range(point_shape[0])]
        )
        belongs = gs.logical_and(is_scalar, has_modulus_lower_than_one)
        belongs = gs.reshape(belongs, (-1,))
        return belongs

    @staticmethod
    def projection(point):
        """Project a point on the complex unit disk.

        Parameters
        ----------
        point : array-like, shape=[..., 1]
            Point to project.
        atol : float
            Tolerance.
            Optional, default: backend atol.

        Returns
        -------
        projected : array-like, shape=[..., 1]
            Projected point.
        """
        return gs.where(
            gs.abs(point) >= 1 - gs.atol,
            gs.cast((1 - gs.atol) / gs.abs(point), dtype=point.dtype) * point,
            point,
        )

    def random_point(self, n_samples=1, bound=1.0):
        """Generate random points in the complex unit disk.

        Parameters
        ----------
        n_samples : int
            Number of samples.
            Optional, default: 1.
        bound : float
            Bound of the interval in which to sample in the tangent space.
            Optional, default: 1.

        Returns
        -------
        samples : array-like, shape=[..., 1]
            Points sampled in the unit disk.
        """
        size = (n_samples, 1) if n_samples != 1 else (1,)

        samples = gs.cast(gs.random.rand(*size), dtype=gs.get_default_cdtype())
        samples += 1j * gs.cast(gs.random.rand(*size), dtype=gs.get_default_cdtype())
        samples -= 0.5 + 0.5j
        samples /= 2
        samples *= 1 - gs.atol
        samples *= bound
        samples = self.projection(samples)
        return samples


class ComplexPoincareDiskMetric(ComplexRiemannianMetric):
    """Class for the complex Poincaré metric.

    Parameters
    ----------
    scale : int or float
        Scale of the complex Poincaré metric.
        Optional, default: 1.
    """

    def __init__(self, scale=1):
        super().__init__(
            dim=1,
            shape=(1,),
            signature=(1, 0),
        )
        self.scale = scale

    def inner_product_matrix(self, base_point):
        """Compute the inner product matrix at base point.

        Parameters
        ----------
        base_point : array-like, shape=[..., 1]
            Base point.

        Returns
        -------
        inner_prod_mat : array-like, shape=[..., 1]
            Inner product matrix.
        """
        inner_prod_mat = 1 / (1 - gs.abs(base_point) ** 2) ** 2
        inner_prod_mat = gs.cast(inner_prod_mat, dtype=gs.get_default_cdtype())
        inner_prod_mat *= self.scale**2
        return inner_prod_mat

    def inner_product(self, tangent_vec_a, tangent_vec_b, base_point):
        """Compute the complex Poincaré disk inner-product.

        Compute the inner-product of tangent_vec_a and tangent_vec_b
        at point base_point using the Siegel Riemannian metric:

        Parameters
        ----------
        tangent_vec_a : array-like, shape=[..., 1]
            Tangent vector at base point.
        tangent_vec_b : array-like, shape=[..., 1]
            Tangent vector at base point.
        base_point : array-like, shape=[..., 1]
            Base point.

        Returns
        -------
        inner_product : array-like, shape=[...,]
            Inner-product.
        """
        inner_product_matrix = self.inner_product_matrix(base_point=base_point)
        inner_prod = gs.conj(tangent_vec_a) * inner_product_matrix * tangent_vec_b
        inner_prod = gs.reshape(inner_prod, (-1,))
        return inner_prod

    def squared_norm(self, vector, base_point):
        """Compute the square of the norm of a vector.

        Squared norm of a vector associated to the inner product
        at the tangent space at a base point.

        Parameters
        ----------
        vector : array-like, shape=[..., 1]
            Vector.
        base_point : array-like, shape=[..., 1]
            Base point.
            Optional, default: None.

        Returns
        -------
        sq_norm : array-like, shape=[...,]
            Squared norm.
        """
        sq_norm = self.inner_product(vector, vector, base_point=base_point)
        sq_norm = gs.real(sq_norm)
        return sq_norm

    @staticmethod
    def exp(tangent_vec, base_point):
        """Compute the complex Poincaré disk exponential map.

        Parameters
        ----------
        tangent_vec : array-like, shape=[..., 1]
            Tangent vector at base point.
        base_point : array-like, shape=[..., 1]
            Base point.

        Returns
        -------
        exp : array-like, shape=[..., 1]
            Riemannian exponential.
        """
        ndim = max(len(gs.shape(tangent_vec)), len(gs.shape(base_point)))
        tangent_vec = gs.to_ndarray(tangent_vec, to_ndim=2)
        base_point = gs.to_ndarray(base_point, to_ndim=2)
        if base_point.shape[0] < tangent_vec.shape[0]:
            base_point = (
                gs.cast(gs.ones(tangent_vec.shape), dtype=base_point.dtype) @ base_point
            )
        elif base_point.shape[0] > tangent_vec.shape[0]:
            tangent_vec = (
                gs.cast(gs.ones(base_point.shape), dtype=tangent_vec.dtype)
                @ tangent_vec
            )
        theta = gs.cast(gs.angle(tangent_vec), dtype=gs.get_default_cdtype())
        s = 2 * gs.abs(tangent_vec) / (1 - gs.abs(base_point) ** 2)
        num = gs.array(base_point)
        exp_i_theta = gs.exp(1j * theta)
        exp_minus_s = gs.cast(gs.exp(-s), dtype=gs.get_default_cdtype())
        num += exp_i_theta
        num += (base_point - exp_i_theta) * exp_minus_s
        den = 1
        den += gs.conj(base_point) * exp_i_theta
        den += (1 - gs.conj(base_point) * exp_i_theta) * exp_minus_s
        exp = num / den
        if ndim == 1:
            exp = gs.reshape(exp, (-1,))
        return exp

    @staticmethod
    def _tau(point_a, point_b, atol=gs.atol):
        """Compute the coefficient tau.

        The coefficient tau is used to compute the distance
        between point_a and point_b; it is also used to
        compute the logarithm map between point_a and point_b.

        Parameters
        ----------
        point_a : array-like, shape=[..., 1]
            Point.
        point_b : array-like, shape=[..., 1]
            Point.
        atol : float
            Tolerance.
            Optional, default: backend atol.

        Returns
        -------
        tau : array-like, shape=[...,]
            Coefficient tau.
        """
        num = gs.abs(point_a - point_b)
        den = gs.abs(1 - point_a * gs.conj(point_b))
        den = gs.maximum(den, atol)
        delta = num / den
        delta = gs.minimum(delta, 1 - atol)
        tau = (1 / 2) * gs.log((1 + delta) / (1 - delta))
        return tau

    def log(self, point, base_point):
        """Compute the complex Poincaré disk logarithm map.

        Compute the Riemannian logarithm at point base_point,
        of point wrt the positive reals metric.
        This gives a tangent vector at point base_point.

        Parameters
        ----------
        point : array-like, shape=[..., 1]
            Point.
        base_point : array-like, shape=[..., 1]
            Base point.

        Returns
        -------
        log : array-like, shape=[..., 1]
            Riemannian logarithm.
        """
        log = self._tau(base_point, point)
        log = gs.cast(log, dtype=gs.get_default_cdtype())
        angle = gs.angle(point - base_point) - gs.angle(1 - gs.conj(base_point) * point)
        angle = gs.cast(angle, dtype=gs.get_default_cdtype())
        log *= gs.exp(1j * angle)
        log *= gs.cast(1 - gs.abs(base_point) ** 2, dtype=gs.get_default_cdtype())
        return log

    def squared_dist(self, point_a, point_b, atol=gs.atol):
        """Compute the complex Poincaré disk squared distance.

        Compute the Riemannian squared distance between point_a and point_b.

        Parameters
        ----------
        point_a : array-like, shape=[..., 1]
            Point.
        point_b : array-like, shape=[..., 1]
            Point.

        Returns
        -------
        squared_dist : array-like, shape=[...,]
            Riemannian squared distance.
        """
        sq_dist = self._tau(point_a, point_b, atol=atol)
        sq_dist = gs.real(sq_dist)
        sq_dist = gs.reshape(sq_dist, (-1,))
        sq_dist = gs.power(sq_dist, 2)
        sq_dist *= self.scale**2
        return sq_dist

    def dist(self, point_a, point_b, atol=gs.atol):
        """Compute the complex Poincaré disk distance.

        Compute the Riemannian distance between point_a and point_b.

        Parameters
        ----------
        point_a : array-like, shape=[..., 1]
            Point.
        point_b : array-like, shape=[..., 1]
            Point.

        Returns
        -------
        dist : array-like, shape=[...,]
            Riemannian distance.
        """
        dist = self._tau(point_a, point_b, atol=atol)
        dist = gs.reshape(dist, (-1,))
        dist *= self.scale
        return dist
