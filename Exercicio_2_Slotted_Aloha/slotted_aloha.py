#!/usr/bin/env python3
"""DTMC analysis of adaptive Slotted Aloha with six aggregated states."""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path
from typing import List, Tuple

import numpy as np

N_STATIONS = 5
State = int  # Number of transmissions in the previous slot: 0, 1, ..., 5


def enumerate_states(n: int = N_STATIONS) -> List[State]:
    """Return the n+1 aggregated states E0, E1, ..., En."""
    return list(range(n + 1))


def low_probability_count(state: State, n: int = N_STATIONS) -> int:
    """Number of stations using b now, based on the previous slot outcome.

    E0 is an idle slot and E1 is a successful one-station transmission. Neither
    causes adaptation. For Ek with k >= 2, exactly k stations collided and use b.
    """
    if not isinstance(state, int) or not 0 <= state <= n:
        raise ValueError(f"State must be an integer from 0 to {n}.")
    return state if state >= 2 else 0


def station_probabilities(state: State, a: float, b: float,
                          n: int = N_STATIONS) -> List[float]:
    """Transmission probabilities for a representative set of stations.

    Since stations are homogeneous, only the number using b matters for total
    throughput. The first k entries represent the k stations involved in the
    previous collision; their identities do not affect aggregate results.
    """
    k = low_probability_count(state, n)
    return [b if station < k else a for station in range(n)]


def count_probability(current_state: State, next_count: int,
                      a: float, b: float, n: int = N_STATIONS) -> float:
    """Probability that exactly next_count stations transmit in the next slot.

    This is a Poisson-binomial count. Of the k stations using b, r transmit;
    of the remaining n-k stations using a, next_count-r transmit.
    """
    if not 0 <= next_count <= n:
        raise ValueError(f"next_count must be between 0 and {n}.")

    k = low_probability_count(current_state, n)
    normal_count = n - k
    probability = 0.0
    min_reduced = max(0, next_count - normal_count)
    max_reduced = min(next_count, k)

    for reduced_transmissions in range(min_reduced, max_reduced + 1):
        normal_transmissions = next_count - reduced_transmissions
        probability += (
            math.comb(k, reduced_transmissions)
            * b ** reduced_transmissions
            * (1.0 - b) ** (k - reduced_transmissions)
            * math.comb(normal_count, normal_transmissions)
            * a ** normal_transmissions
            * (1.0 - a) ** (normal_count - normal_transmissions)
        )
    return probability


def build_transition_matrix(a: float, b: float, n: int = N_STATIONS):
    """Build the (n+1) x (n+1) transition matrix over E0, ..., En.

    The next state is the number of stations transmitting in the current slot:
    0 means idle, 1 means successful transmission, and 2..n means collision.
    """
    states = enumerate_states(n)
    p_matrix = np.zeros((len(states), len(states)), dtype=float)
    for row, current_state in enumerate(states):
        for column, next_state in enumerate(states):
            p_matrix[row, column] = count_probability(
                current_state, next_state, a, b, n
            )
    return states, p_matrix


def stationary_distribution(p_matrix: np.ndarray) -> np.ndarray:
    """Solve pi P = pi with sum(pi) = 1."""
    n_states = p_matrix.shape[0]
    system = p_matrix.T - np.eye(n_states)
    rhs = np.zeros(n_states)
    system[-1, :] = 1.0
    rhs[-1] = 1.0
    pi = np.linalg.solve(system, rhs)
    pi[np.abs(pi) < 1e-13] = 0.0
    pi = np.clip(pi, 0.0, None)
    return pi / pi.sum()


def per_state_metrics(state: State, a: float, b: float,
                      n: int = N_STATIONS) -> Tuple[float, float, float]:
    """Return idle, successful-transmission, and collision probabilities."""
    probs = station_probabilities(state, a, b, n)
    idle = math.prod(1.0 - p for p in probs)
    success = sum(
        probs[i] * math.prod(1.0 - probs[j] for j in range(n) if j != i)
        for i in range(n)
    )
    collision = max(0.0, 1.0 - idle - success)
    return idle, success, collision


def theoretical_results(a: float, b: float, n: int = N_STATIONS):
    states, p_matrix = build_transition_matrix(a, b, n)
    pi = stationary_distribution(p_matrix)
    metrics = [per_state_metrics(state, a, b, n) for state in states]

    idle = float(sum(pi[i] * metrics[i][0] for i in range(len(states))))
    throughput = float(sum(pi[i] * metrics[i][1] for i in range(len(states))))
    collision = float(sum(pi[i] * metrics[i][2] for i in range(len(states))))

    summary = {
        "stations": n,
        "a": a,
        "b": b,
        "number_of_states": len(states),
        "throughput_packets_per_slot": throughput,
        "idle_slot_fraction": idle,
        "collision_slot_fraction": collision,
        "stationary_distribution_sum": float(pi.sum()),
        "maximum_row_sum_error": float(
            np.max(np.abs(p_matrix.sum(axis=1) - 1.0))
        ),
    }
    return states, p_matrix, pi, summary


def simulate(a: float, b: float, slots: int, seed: int,
             n: int = N_STATIONS):
    """Simulate the six-state aggregate chain using Monte Carlo slots."""
    rng = random.Random(seed)
    state: State = 0
    successes = idle_slots = collision_slots = 0

    for _ in range(slots):
        probs = station_probabilities(state, a, b, n)
        transmitting_count = sum(rng.random() < prob for prob in probs)
        if transmitting_count == 0:
            idle_slots += 1
        elif transmitting_count == 1:
            successes += 1
        else:
            collision_slots += 1
        state = transmitting_count

    return {
        "slots": slots,
        "seed": seed,
        "successes": successes,
        "throughput_packets_per_slot": successes / slots,
        "idle_slots": idle_slots,
        "idle_slot_fraction": idle_slots / slots,
        "collision_slots": collision_slots,
        "collision_slot_fraction": collision_slots / slots,
    }


def state_label(state: State) -> str:
    return f"E{state}"


def previous_event_label(state: State) -> str:
    if state == 0:
        return "Idle slot"
    if state == 1:
        return "Successful transmission"
    return f"Collision involving {state} stations"


def write_station_csv(path: Path, states, pi, a: float, b: float):
    """Write stationary probabilities and conditional slot metrics by state."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "state", "previous_slot_event", "stations_using_b",
            "stationary_probability", "idle_probability",
            "success_probability", "collision_probability"
        ])
        for i, state in enumerate(states):
            idle, success, collision = per_state_metrics(state, a, b)
            reduced_count = low_probability_count(state)
            writer.writerow([
                state_label(state),
                previous_event_label(state),
                "-" if reduced_count == 0 else reduced_count,
                f"{pi[i]:.12g}",
                f"{idle:.12g}",
                f"{success:.12g}",
                f"{collision:.12g}",
            ])


def write_transition_matrix(path: Path, states, p_matrix):
    """Export the labeled (n+1) x (n+1) transition matrix P as CSV."""
    labels = [state_label(state) for state in states]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["from/to", *labels])
        for label, row in zip(labels, p_matrix):
            writer.writerow([label, *(f"{prob:.12g}" for prob in row)])


def main():
    parser = argparse.ArgumentParser(
        description="Six-state DTMC for adaptive Slotted Aloha with five stations."
    )
    parser.add_argument("--a", type=float, default=0.30,
                        help="normal transmission probability (default: 0.30)")
    parser.add_argument("--b", type=float, default=0.10,
                        help="reduced probability after collision (default: 0.10)")
    parser.add_argument("--simulate", type=int, default=100000,
                        help="number of Monte Carlo slots (default: 100000)")
    parser.add_argument("--seed", type=int, default=2026,
                        help="random seed for reproducibility (default: 2026)")
    parser.add_argument("--output-dir", type=Path, default=Path("resultados"),
                        help="directory for CSV and JSON output")
    args = parser.parse_args()

    if not (0.0 < args.b < args.a < 1.0):
        parser.error("Parameters must satisfy 0 < b < a < 1.")
    if args.simulate < 1:
        parser.error("--simulate must be a positive integer.")

    states, p_matrix, pi, theory = theoretical_results(args.a, args.b)
    simulation = simulate(args.a, args.b, args.simulate, args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    write_station_csv(
        args.output_dir / "distribuicao_estacionaria.csv",
        states, pi, args.a, args.b
    )
    write_transition_matrix(
        args.output_dir / "matriz_transicao_P.csv", states, p_matrix
    )
    with (args.output_dir / "resumo_resultados.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump({"theoretical": theory, "simulation": simulation},
                  file, indent=2, ensure_ascii=False)

    print("\n=== Slotted Aloha adaptativo: resultados ===")
    print(f"Estações: {theory['stations']} | a={args.a:.4f} | b={args.b:.4f}")
    print(f"Estados da DTMC: {theory['number_of_states']}")
    print("\nAnálise teórica (distribuição estacionária):")
    print(f"  Vazão média:       {theory['throughput_packets_per_slot']:.6f} pacotes/slot")
    print(f"  Slots ociosos:     {theory['idle_slot_fraction']:.6f} "
          f"({100 * theory['idle_slot_fraction']:.3f}%)")
    print(f"  Slots com colisão: {theory['collision_slot_fraction']:.6f} "
          f"({100 * theory['collision_slot_fraction']:.3f}%)")
    print("\nSimulação de Monte Carlo:")
    print(f"  Slots simulados:   {simulation['slots']}")
    print(f"  Vazão observada:   {simulation['throughput_packets_per_slot']:.6f} pacotes/slot")
    print(f"  Slots ociosos:     {simulation['idle_slot_fraction']:.6f} "
          f"({100 * simulation['idle_slot_fraction']:.3f}%)")
    print(f"  Slots com colisão: {simulation['collision_slot_fraction']:.6f} "
          f"({100 * simulation['collision_slot_fraction']:.3f}%)")
    print(f"\nArquivos gerados em: {args.output_dir.resolve()}")
    print("  - resumo_resultados.json")
    print("  - distribuicao_estacionaria.csv")
    print("  - matriz_transicao_P.csv")
    print(f"Soma de pi = {theory['stationary_distribution_sum']:.12f}")
    print(f"Maior erro na soma das linhas de P = {theory['maximum_row_sum_error']:.3e}")


if __name__ == "__main__":
    main()
