import unittest
import numpy as np

from slotted_aloha import (
    build_transition_matrix,
    enumerate_states,
    low_probability_count,
    per_state_metrics,
    stationary_distribution,
    theoretical_results,
)


class SlottedAlohaTests(unittest.TestCase):
    def test_state_space_has_six_aggregated_states(self):
        states = enumerate_states()
        self.assertEqual(states, [0, 1, 2, 3, 4, 5])
        self.assertEqual(len(states), 6)
        self.assertEqual([low_probability_count(state) for state in states],
                         [0, 0, 2, 3, 4, 5])

    def test_idle_and_success_states_have_identical_transition_rows(self):
        _, matrix = build_transition_matrix(a=0.30, b=0.10)
        self.assertTrue(np.allclose(matrix[0], matrix[1], atol=1e-14))

    def test_transition_matrix_rows_sum_to_one(self):
        _, matrix = build_transition_matrix(a=0.30, b=0.10)
        self.assertEqual(matrix.shape, (6, 6))
        self.assertTrue(np.allclose(matrix.sum(axis=1), 1.0, atol=1e-12))
        self.assertTrue(np.all(matrix >= 0.0))

    def test_stationary_distribution_is_normalized_and_stationary(self):
        _, matrix = build_transition_matrix(a=0.30, b=0.10)
        pi = stationary_distribution(matrix)
        self.assertAlmostEqual(float(pi.sum()), 1.0, places=12)
        self.assertTrue(np.allclose(pi @ matrix, pi, atol=1e-10))

    def test_performance_probabilities_sum_to_one(self):
        _, _, _, metrics = theoretical_results(a=0.30, b=0.10)
        total = (
            metrics["throughput_packets_per_slot"]
            + metrics["idle_slot_fraction"]
            + metrics["collision_slot_fraction"]
        )
        self.assertAlmostEqual(total, 1.0, places=12)

    def test_metrics_match_original_27_state_model_reference(self):
        _, _, pi, metrics = theoretical_results(a=0.30, b=0.10)
        # Reference values from the original exact 27-state formulation.
        self.assertAlmostEqual(metrics["throughput_packets_per_slot"],
                               0.383422640409664, places=11)
        self.assertAlmostEqual(metrics["idle_slot_fraction"],
                               0.223211418374557, places=11)
        self.assertAlmostEqual(metrics["collision_slot_fraction"],
                               0.393365941215779, places=11)
        # In the six-state chain, each stationary event fraction is explicit.
        self.assertAlmostEqual(float(pi[0]), metrics["idle_slot_fraction"], places=12)
        self.assertAlmostEqual(float(pi[1]), metrics["throughput_packets_per_slot"], places=12)
        self.assertAlmostEqual(float(pi[2:].sum()), metrics["collision_slot_fraction"], places=12)

    def test_conditional_performance_probabilities_are_valid(self):
        for state in enumerate_states():
            idle, success, collision = per_state_metrics(state, 0.30, 0.10)
            self.assertAlmostEqual(idle + success + collision, 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
