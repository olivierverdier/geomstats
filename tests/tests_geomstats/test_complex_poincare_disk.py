"""Unit tests for the complex Poincare disk manifold."""

import geomstats.backend as gs
from tests.conftest import Parametrizer
from tests.data.complex_poincare_disk_data import (
    ComplexPoincareDiskMetricTestData,
    ComplexPoincareDiskTestData,
)
from tests.geometry_test_cases import ComplexRiemannianMetricTestCase, OpenSetTestCase

CDTYPE = gs.get_default_cdtype()


class TestComplexPoincareDisk(OpenSetTestCase, metaclass=Parametrizer):
    """Test of the complex Poincare disk methods."""

    testing_data = ComplexPoincareDiskTestData()

    def test_belongs(self, point, expected):
        self.assertAllClose(
            self.Space().belongs(gs.cast(gs.array(point), dtype=CDTYPE)), expected
        )

    def test_projection(self, point, expected):
        self.assertAllClose(
            self.Space().projection(gs.cast(gs.array(point), dtype=CDTYPE)),
            gs.cast(gs.array(expected), dtype=CDTYPE),
        )


class TestComplexPoincareDiskMetric(
    ComplexRiemannianMetricTestCase, metaclass=Parametrizer
):
    skip_test_parallel_transport_ivp_is_isometry = True
    skip_test_parallel_transport_bvp_is_isometry = True
    skip_test_exp_geodesic_ivp = True
    skip_test_exp_ladder_parallel_transport = True
    skip_test_geodesic_bvp_belongs = True
    skip_test_geodesic_ivp_belongs = True
    skip_test_covariant_riemann_tensor_is_skew_symmetric_1 = True
    skip_test_covariant_riemann_tensor_is_skew_symmetric_2 = True
    skip_test_covariant_riemann_tensor_bianchi_identity = True
    skip_test_covariant_riemann_tensor_is_interchange_symmetric = True
    skip_test_inner_product_is_symmetric = True
    skip_test_riemann_tensor_shape = True
    skip_test_scalar_curvature_shape = True
    skip_test_ricci_tensor_shape = True
    skip_test_sectional_curvature_shape = True

    testing_data = ComplexPoincareDiskMetricTestData()

    def test_inner_product(
        self, scale, tangent_vec_a, tangent_vec_b, base_point, expected
    ):
        metric = self.Metric(scale)
        result = metric.inner_product(
            gs.cast(gs.array(tangent_vec_a), dtype=CDTYPE),
            gs.cast(gs.array(tangent_vec_b), dtype=CDTYPE),
            gs.cast(gs.array(base_point), dtype=CDTYPE),
        )
        self.assertAllClose(result, expected)

    def test_exp(self, scale, tangent_vec, base_point, expected):
        metric = self.Metric(scale)
        self.assertAllClose(
            metric.exp(
                gs.cast(gs.array(tangent_vec), dtype=CDTYPE),
                gs.cast(gs.array(base_point), dtype=CDTYPE),
            ),
            gs.cast(gs.array(expected), dtype=CDTYPE),
        )

    def test_log(self, scale, point, base_point, expected):
        metric = self.Metric(scale)
        self.assertAllClose(
            metric.log(
                gs.cast(gs.array(point), dtype=CDTYPE),
                gs.cast(gs.array(base_point), dtype=CDTYPE),
            ),
            gs.cast(gs.array(expected), dtype=CDTYPE),
        )
