#!/usr/bin/env python3
"""DTMC analysis of adaptive Slotted Aloha with five stations."""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

N_STATIONS = 5
State = Tuple[int, ...]  # 1-based IDs of stations using b in the current slot


def enumerate_states(n: int = N_STATIONS) -> List[State]:
    """Empty state plus every possible collision set (size at least two)."""
    states: List[State] = [()]
    for size in range(2, n + 1):
        states.extend(combinations(range(1, n + 1), size))
    return states


def station_probabilities(state: State, a: float, b: float,
                          n: int = N_STATIONS) -> List[float]:
    """Transmission probability for each station in the current slot."""
    low_probability_stations = set(state)
    return [b if station in low_probability_stations else a
            for station in range(1, n + 1)]


def outcome_probability(transmitting: State, probs: List[float]) -> float:
    """Probability that exactly the stations in transmitting transmit."""
    selected = set(transmitting)
    result = 1.0
    for station, prob in enumerate(probs, start=1):
        result *= prob if station in selected else (1.0 - prob)
    return result


def build_transition_matrix(a: float, b: float, n: int = N_STATIONS):
    """Build P. The next state is the collision set observed in this slot."""
    states = enumerate_states(n)
    index: Dict[State, int] = {state: i for i, state in enumerate(states)}
    p_matrix = np.zeros((len(states), len(states)), dtype=float)
    collision_states = states[1:]

    for row, current_state in enumerate(states):
        probs = station_probabilities(current_state, a, b, n)

        # No collision: zero or one station transmits, so next state is empty.
        p_matrix[row, index[()]] = outcome_probability((), probs)
        for station in range(1, n + 1):
            p_matrix[row, index[()]] += outcome_probability((station,), probs)

        # Two or more transmissions: the exact transmitting set collides.
        for next_state in collision_states:
            p_matrix[row, index[next_state]] = outcome_probability(next_state, probs)

    return states, p_matrix


def stationary_distribution(p_matrix: np.ndarray) -> np.ndarray:
    """Solve pi P = pi and sum(pi) = 1 by replacing one dependent equation."""
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
                      n: int = N_STATIONS):
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
    """Simulate slots using the same one-slot adaptive rule as the DTMC."""
    rng = random.Random(seed)
    state: State = ()
    successes = idle_slots = collision_slots = 0

    for _ in range(slots):
        probs = station_probabilities(state, a, b, n)
        transmitting = tuple(
            station for station, prob in enumerate(probs, start=1)
            if rng.random() < prob
        )
        if len(transmitting) == 0:
            idle_slots += 1
            state = ()
        elif len(transmitting) == 1:
            successes += 1
            state = ()
        else:
            collision_slots += 1
            state = transmitting

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


def write_station_csv(path: Path, states, pi, a: float, b: float):
    """Write stationary state probabilities and conditional slot metrics."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "state", "stations_using_b", "stationary_probability",
            "idle_probability", "success_probability", "collision_probability"
        ])
        for i, state in enumerate(states):
            idle, success, collision = per_state_metrics(state, a, b)
            label = "E" if not state else "{" + ",".join(map(str, state)) + "}"
            writer.writerow([
                label,
                "-" if not state else ",".join(map(str, state)),
                f"{pi[i]:.12g}",
                f"{idle:.12g}",
                f"{success:.12g}",
                f"{collision:.12g}",
            ])


def main():
    parser = argparse.ArgumentParser(
        description="DTMC for adaptive Slotted Aloha with five stations."
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
    print(f"Soma de pi = {theory['stationary_distribution_sum']:.12f}")
    print(f"Maior erro na soma das linhas de P = {theory['maximum_row_sum_error']:.3e}")


if __name__ == "__main__":
    main()
