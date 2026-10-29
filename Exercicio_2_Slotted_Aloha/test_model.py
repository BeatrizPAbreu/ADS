import unittest
import numpy as np

from slotted_aloha import (
    build_transition_matrix,
    enumerate_states,
    stationary_distribution,
    theoretical_results,
)


class SlottedAlohaTests(unittest.TestCase):
    def test_state_space_has_27_states(self):
        states = enumerate_states()
        self.assertEqual(len(states), 27)
        self.assertEqual(states[0], ())
        self.assertTrue(all(len(state) >= 2 for state in states[1:]))

    def test_transition_matrix_rows_sum_to_one(self):
        _, matrix = build_transition_matrix(a=0.30, b=0.10)
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

    def test_theoretical_metrics_are_positive(self):
        _, _, _, metrics = theoretical_results(a=0.30, b=0.10)
        self.assertEqual(metrics["number_of_states"], 27)
        self.assertGreater(metrics["throughput_packets_per_slot"], 0.0)


if __name__ == "__main__":
    unittest.main()
