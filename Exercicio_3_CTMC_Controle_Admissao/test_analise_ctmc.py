"""Testes automatizados da Etapa 2: equilíbrio e indicadores CTMC."""

import unittest
import numpy as np

from modelagem_ctmc import construir_matriz_q, gerar_estados
from analise_ctmc import (
    calcular_distribuicao_estacionaria,
    calcular_distribuicao_produto,
    calcular_indicadores,
)


class TestAnaliseCTMC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estados = gerar_estados()
        cls.q = construir_matriz_q(cls.estados)
        cls.pi = calcular_distribuicao_estacionaria(cls.q)
        cls.indicadores = calcular_indicadores(cls.estados, cls.pi)

    def test_probabilidades_normalizadas(self):
        self.assertAlmostEqual(float(self.pi.sum()), 1.0, places=10)
        self.assertTrue(np.all(self.pi >= 0.0))

    def test_equilibrio_estacionario(self):
        np.testing.assert_allclose(self.pi @ self.q, np.zeros(len(self.estados)), atol=1e-9)

    def test_estado_vazio(self):
        indice = self.estados.index((0, 0))
        self.assertAlmostEqual(self.pi[indice], 0.2830944829, places=8)

    def test_forma_produto_confere_com_equilibrio(self):
        pi_produto, normalizador = calcular_distribuicao_produto(self.estados)
        np.testing.assert_allclose(self.pi, pi_produto, atol=1e-10)
        self.assertAlmostEqual(normalizador, 3.5323895748, places=9)

    def test_indicadores_basicos(self):
        self.assertAlmostEqual(self.indicadores["probabilidade_bloqueio_T1"], 0.0064898148, places=8)
        self.assertAlmostEqual(self.indicadores["utilizacao_media"], 0.2496509666, places=8)
        self.assertAlmostEqual(self.indicadores["numero_medio_conexoes_T1"], 0.6623401235, places=8)
        self.assertAlmostEqual(self.indicadores["numero_medio_conexoes_T2"], 0.5859147097, places=8)

    def test_duas_interpretacoes_do_bloqueio_t2(self):
        self.assertAlmostEqual(self.indicadores["probabilidade_bloqueio_T2_literal_pagina14"], 0.1027419390, places=8)
        self.assertAlmostEqual(self.indicadores["probabilidade_bloqueio_T2_regra_admissao_Q"], 0.0234754838, places=8)

    def test_capacidade_maxima_igual_bloqueio_t1(self):
        self.assertAlmostEqual(
            self.indicadores["fracao_tempo_capacidade_maxima"],
            self.indicadores["probabilidade_bloqueio_T1"], places=12
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
