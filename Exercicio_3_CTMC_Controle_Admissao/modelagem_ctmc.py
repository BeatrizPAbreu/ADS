#!/usr/bin/env python3
"""Etapa 1 do miniprojeto CTMC: estados válidos e matriz infinitesimal Q.

Modelo de controle de admissão com duas classes de tráfego:
- T1: prioritária;
- T2: não prioritária.

A ordem dos estados segue a apresentação do enunciado: n1 crescente e,
para cada n1, n2 crescente.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import numpy as np


# Parâmetros fornecidos pelo professor (taxas em requisições por minuto).
C = 5
R = 2
LAMBDA1 = 10.0
LAMBDA2 = 15.0
MU1 = 15.0
MU2 = 25.0

State = tuple[int, int]


def gerar_estados(capacidade: int = C, reserva: int = R) -> list[State]:
    """Retorna os estados (n1, n2) que respeitam capacidade e reserva.

    Restrições do enunciado:
        n1 + n2 <= C
        n2 <= C - R
    """
    if capacidade < 0:
        raise ValueError("A capacidade deve ser não negativa.")
    if not 0 <= reserva <= capacidade:
        raise ValueError("A reserva deve estar entre zero e a capacidade.")

    estados: list[State] = []
    max_t2 = capacidade - reserva

    for n1 in range(capacidade + 1):
        for n2 in range(max_t2 + 1):
            if n1 + n2 <= capacidade:
                estados.append((n1, n2))

    return estados


def construir_matriz_q(
    estados: Iterable[State],
    lambda1: float = LAMBDA1,
    lambda2: float = LAMBDA2,
    mu1: float = MU1,
    mu2: float = MU2,
) -> np.ndarray:
    """Constrói a matriz geradora Q para a lista ordenada de estados.

    Entradas fora da diagonal são taxas de transição. A diagonal é o
    negativo da soma das taxas de saída do estado, de modo que cada linha
    some zero.
    """
    taxas = (lambda1, lambda2, mu1, mu2)
    if any(taxa < 0 for taxa in taxas):
        raise ValueError("As taxas do modelo devem ser não negativas.")

    lista_estados = list(estados)
    if len(set(lista_estados)) != len(lista_estados):
        raise ValueError("A lista de estados contém duplicatas.")

    indice = {estado: pos for pos, estado in enumerate(lista_estados)}
    quantidade = len(lista_estados)
    q = np.zeros((quantidade, quantidade), dtype=float)

    for i, (n1, n2) in enumerate(lista_estados):
        # Chegada de T1: só ocorre se o estado resultante for válido.
        destino = (n1 + 1, n2)
        if destino in indice:
            q[i, indice[destino]] += lambda1

        # Chegada de T2: só ocorre se o estado resultante for válido.
        destino = (n1, n2 + 1)
        if destino in indice:
            q[i, indice[destino]] += lambda2

        # Saída de uma conexão T1. n1 conexões independentes,
        # cada uma com taxa individual mu1.
        if n1 > 0:
            destino = (n1 - 1, n2)
            if destino in indice:
                q[i, indice[destino]] += n1 * mu1

        # Saída de uma conexão T2.
        if n2 > 0:
            destino = (n1, n2 - 1)
            if destino in indice:
                q[i, indice[destino]] += n2 * mu2

        # Diagonal principal: menos a taxa total de saída do estado.
        q[i, i] = -np.sum(q[i, :])

    return q


def salvar_arquivos(estados: list[State], q: np.ndarray, pasta_saida: Path) -> None:
    """Salva a lista de estados e a matriz Q em arquivos CSV."""
    pasta_saida.mkdir(parents=True, exist_ok=True)

    with (pasta_saida / "estados.csv").open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["indice", "n1_T1", "n2_T2"])
        for indice, (n1, n2) in enumerate(estados):
            escritor.writerow([indice, n1, n2])

    rotulos = [f"({n1},{n2})" for n1, n2 in estados]
    with (pasta_saida / "matriz_Q.csv").open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["estado", *rotulos])
        for rotulo, linha in zip(rotulos, q):
            escritor.writerow([rotulo, *[f"{valor:.10g}" for valor in linha]])


def validar_modelo(estados: list[State], q: np.ndarray) -> None:
    """Executa verificações estruturais básicas e interrompe se falharem."""
    if len(estados) != 18:
        raise AssertionError(f"Esperados 18 estados; encontrados {len(estados)}.")
    if q.shape != (18, 18):
        raise AssertionError(f"Esperada matriz 18x18; dimensão encontrada: {q.shape}.")
    if not np.allclose(q.sum(axis=1), 0.0):
        raise AssertionError("A soma de pelo menos uma linha de Q não é zero.")

    fora_diagonal = q.copy()
    np.fill_diagonal(fora_diagonal, 0.0)
    if np.any(fora_diagonal < 0.0):
        raise AssertionError("Há taxa negativa fora da diagonal principal.")
    if np.any(np.diag(q) > 0.0):
        raise AssertionError("A diagonal principal não pode conter valores positivos.")


def imprimir_resultados(estados: list[State], q: np.ndarray) -> None:
    """Exibe os estados e Q com rótulos para facilitar a conferência."""
    print("ESTADOS VÁLIDOS")
    for indice, estado in enumerate(estados):
        print(f"{indice:2d}: {estado}")

    rotulos = [f"({n1},{n2})" for n1, n2 in estados]
    largura = 9
    print("\nMATRIZ Q (taxas em req/min)")
    print("Estado".ljust(largura) + "".join(rotulo.rjust(largura) for rotulo in rotulos))
    for rotulo, linha in zip(rotulos, q):
        valores = "".join(f"{valor:9.2f}" for valor in linha)
        print(rotulo.ljust(largura) + valores)

    print("\nVERIFICAÇÕES")
    print(f"Quantidade de estados: {len(estados)}")
    print(f"Dimensão de Q: {q.shape[0]} x {q.shape[1]}")
    print(f"Maior valor absoluto da soma das linhas: {np.max(np.abs(q.sum(axis=1))):.3e}")
    print("Matriz Q construída e validada com sucesso.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera os estados válidos e a matriz Q do miniprojeto CTMC."
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path("resultados"),
        help="Pasta onde serão gravados estados.csv e matriz_Q.csv (padrão: resultados).",
    )
    args = parser.parse_args()

    estados = gerar_estados()
    q = construir_matriz_q(estados)
    validar_modelo(estados, q)
    imprimir_resultados(estados, q)
    salvar_arquivos(estados, q, args.saida)
    print(f"\nArquivos CSV salvos em: {args.saida.resolve()}")


if __name__ == "__main__":
    main()
