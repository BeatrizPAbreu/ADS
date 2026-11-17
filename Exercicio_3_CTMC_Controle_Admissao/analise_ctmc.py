#!/usr/bin/env python3
"""Etapa 2 do miniprojeto CTMC: distribuição estacionária e indicadores."""

from __future__ import annotations
import argparse
import csv
import math
from pathlib import Path
import numpy as np

from modelagem_ctmc import C, R, LAMBDA1, LAMBDA2, MU1, MU2, construir_matriz_q, gerar_estados


def calcular_distribuicao_estacionaria(q: np.ndarray) -> np.ndarray:
    """Resolve pi Q = 0 com sum(pi)=1, retornando pi como vetor linha."""
    if q.ndim != 2 or q.shape[0] != q.shape[1]:
        raise ValueError("Q precisa ser uma matriz quadrada.")
    if not np.allclose(q.sum(axis=1), 0.0, atol=1e-10):
        raise ValueError("Q inválida: as linhas devem somar zero.")

    n = q.shape[0]
    sistema = q.T.copy()
    lado_direito = np.zeros(n, dtype=float)
    sistema[-1, :] = 1.0
    lado_direito[-1] = 1.0

    try:
        pi = np.linalg.solve(sistema, lado_direito)
    except np.linalg.LinAlgError as exc:
        raise ValueError("Não foi possível resolver o sistema estacionário.") from exc

    pi[np.abs(pi) < 1e-14] = 0.0
    if np.any(pi < -1e-10):
        raise ArithmeticError("A solução contém probabilidades negativas.")
    pi = np.clip(pi, 0.0, None)
    pi /= pi.sum()

    if not np.isclose(pi.sum(), 1.0, atol=1e-10):
        raise ArithmeticError("A distribuição não está normalizada.")
    if not np.allclose(pi @ q, 0.0, atol=1e-9):
        raise ArithmeticError("A solução não satisfaz pi Q = 0.")
    return pi


def calcular_distribuicao_produto(estados: list[tuple[int, int]]) -> tuple[np.ndarray, float]:
    """Calcula a forma-produto estacionária como validação independente."""
    pesos = np.array([
        (LAMBDA1 / MU1) ** n1 / math.factorial(n1)
        * (LAMBDA2 / MU2) ** n2 / math.factorial(n2)
        for n1, n2 in estados
    ], dtype=float)
    normalizador = float(pesos.sum())
    return pesos / normalizador, normalizador


def calcular_indicadores(estados: list[tuple[int, int]], pi: np.ndarray) -> dict[str, float]:
    """Calcula indicadores e expõe as duas leituras para o bloqueio T2."""
    if len(estados) != len(pi):
        raise ValueError("O vetor pi deve ter uma probabilidade por estado.")

    n1 = np.array([estado[0] for estado in estados], dtype=float)
    n2 = np.array([estado[1] for estado in estados], dtype=float)
    total = n1 + n2

    capacidade_maxima = total == C
    bloqueio_t2_pagina14 = capacidade_maxima | (n2 == R)
    bloqueio_t2_regra_q = capacidade_maxima | (n2 == C - R)

    return {
        "probabilidade_bloqueio_T1": float(pi[capacidade_maxima].sum()),
        "probabilidade_bloqueio_T2_literal_pagina14": float(pi[bloqueio_t2_pagina14].sum()),
        "probabilidade_bloqueio_T2_regra_admissao_Q": float(pi[bloqueio_t2_regra_q].sum()),
        "utilizacao_media": float(np.dot(total, pi) / C),
        "numero_medio_conexoes_T1": float(np.dot(n1, pi)),
        "numero_medio_conexoes_T2": float(np.dot(n2, pi)),
        "fracao_tempo_capacidade_maxima": float(pi[capacidade_maxima].sum()),
    }


def salvar_resultados(estados, pi, indicadores, pasta: Path) -> None:
    """Exporta a distribuição estacionária e os indicadores em CSV."""
    pasta.mkdir(parents=True, exist_ok=True)
    with (pasta / "distribuicao_estacionaria.csv").open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["indice", "n1_T1", "n2_T2", "probabilidade", "percentual"])
        for i, ((n1, n2), prob) in enumerate(zip(estados, pi)):
            writer.writerow([i, n1, n2, f"{prob:.12f}", f"{100 * prob:.8f}"])

    descricoes = {
        "probabilidade_bloqueio_T1": ("Probabilidade de bloqueio T1", "probabilidade"),
        "probabilidade_bloqueio_T2_literal_pagina14": ("Probabilidade de bloqueio T2 (literal da página 14)", "probabilidade"),
        "probabilidade_bloqueio_T2_regra_admissao_Q": ("Probabilidade de bloqueio T2 (regra consistente com Q)", "probabilidade"),
        "utilizacao_media": ("Utilização média do sistema", "fração da capacidade"),
        "numero_medio_conexoes_T1": ("Número médio de conexões T1", "conexões"),
        "numero_medio_conexoes_T2": ("Número médio de conexões T2", "conexões"),
        "fracao_tempo_capacidade_maxima": ("Fração do tempo em capacidade máxima", "fração do tempo"),
    }
    with (pasta / "indicadores_etapa2.csv").open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["indicador", "valor", "unidade"])
        for chave, valor in indicadores.items():
            nome, unidade = descricoes[chave]
            writer.writerow([nome, f"{valor:.12f}", unidade])


def imprimir_resultados(estados, pi, indicadores, q) -> None:
    """Mostra no terminal pi, indicadores e verificações do equilíbrio."""
    print("DISTRIBUIÇÃO ESTACIONÁRIA (pi)")
    print("Estado       Probabilidade       Percentual")
    for (n1, n2), prob in zip(estados, pi):
        print(f"({n1},{n2})       {prob: .10f}       {100 * prob: .6f}%")

    nomes = {
        "probabilidade_bloqueio_T1": "Bloqueio T1",
        "probabilidade_bloqueio_T2_literal_pagina14": "Bloqueio T2 (literal página 14)",
        "probabilidade_bloqueio_T2_regra_admissao_Q": "Bloqueio T2 (regra consistente com Q)",
        "utilizacao_media": "Utilização média",
        "numero_medio_conexoes_T1": "Número médio de conexões T1",
        "numero_medio_conexoes_T2": "Número médio de conexões T2",
        "fracao_tempo_capacidade_maxima": "Fração do tempo em capacidade máxima",
    }
    print("\nINDICADORES DE DESEMPENHO")
    for chave, valor in indicadores.items():
        if chave in {"numero_medio_conexoes_T1", "numero_medio_conexoes_T2"}:
            print(f"{nomes[chave]}: {valor:.8f} conexões")
        else:
            print(f"{nomes[chave]}: {valor:.8f} ({100 * valor:.4f}%)")

    print(f"\nNormalização: soma(pi) = {pi.sum():.12f}")
    print(f"Resíduo máximo de pi Q: {np.max(np.abs(pi @ q)):.3e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Calcula pi e indicadores da Etapa 2 da CTMC.")
    parser.add_argument("--saida", type=Path, default=Path("resultados"),
                        help="Pasta dos CSVs de saída (padrão: resultados).")
    args = parser.parse_args()

    estados = gerar_estados()
    q = construir_matriz_q(estados)
    pi = calcular_distribuicao_estacionaria(q)

    # Verificação independente: a forma-produto deve reproduzir a solução pi Q=0.
    pi_produto, normalizador = calcular_distribuicao_produto(estados)
    if not np.allclose(pi, pi_produto, atol=1e-10):
        raise ArithmeticError("A solução de pi Q = 0 diverge da forma-produto de validação.")

    indicadores = calcular_indicadores(estados, pi)
    imprimir_resultados(estados, pi, indicadores, q)
    print(f"Constante normalizadora da forma-produto: Z = {normalizador:.12f}")
    print("Conferência independente: forma-produto = solução de pi Q = 0.")

    salvar_resultados(estados, pi, indicadores, args.saida)
    print(f"\nArquivos CSV salvos em: {args.saida.resolve()}")


if __name__ == "__main__":
    main()
