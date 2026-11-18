"""Testes automatizados da modelagem CTMC (Etapa 1)."""

import unittest

import numpy as np

from modelagem_ctmc import construir_matriz_q, gerar_estados, validar_modelo


class TestModelagemCTMC(unittest.TestCase):
    def setUp(self):
        self.estados = gerar_estados()
        self.indice = {estado: i for i, estado in enumerate(self.estados)}
        self.q = construir_matriz_q(self.estados)

    def test_quantidade_e_conjunto_de_estados(self):
        self.assertEqual(len(self.estados), 18)
        self.assertIn((5, 0), self.estados)
        self.assertIn((0, 3), self.estados)
        self.assertNotIn((0, 4), self.estados)
        self.assertNotIn((2, 4), self.estados)

    def test_restricoes_de_todos_os_estados(self):
        for n1, n2 in self.estados:
            self.assertGreaterEqual(n1, 0)
            self.assertGreaterEqual(n2, 0)
            self.assertLessEqual(n1 + n2, 5)
            self.assertLessEqual(n2, 3)

    def test_dimensao_e_soma_das_linhas(self):
        self.assertEqual(self.q.shape, (18, 18))
        np.testing.assert_allclose(self.q.sum(axis=1), np.zeros(18))

    def test_taxas_de_chegada_no_estado_vazio(self):
        i = self.indice[(0, 0)]
        self.assertEqual(self.q[i, self.indice[(1, 0)]], 10.0)
        self.assertEqual(self.q[i, self.indice[(0, 1)]], 15.0)
        self.assertEqual(self.q[i, i], -25.0)

    def test_t2_nao_ultrapassa_tres_conexoes(self):
        i = self.indice[(0, 3)]
        self.assertEqual(self.q[i, i], -(10.0 + 3 * 25.0))
        self.assertEqual(self.q[i, self.indice[(1, 3)]], 10.0)
        self.assertNotIn((0, 4), self.indice)

    def test_saida_de_multiplas_conexoes(self):
        i = self.indice[(2, 1)]
        self.assertEqual(self.q[i, self.indice[(1, 1)]], 2 * 15.0)
        self.assertEqual(self.q[i, self.indice[(2, 0)]], 1 * 25.0)

    def test_validacao_estrutural(self):
        validar_modelo(self.estados, self.q)


if __name__ == "__main__":
    unittest.main(verbosity=2)
