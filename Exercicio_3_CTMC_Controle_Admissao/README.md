# Miniprojeto CTMC — Controle de Admissão (Etapa 1)

Disciplina: **ADS29009 — Avaliação de Desempenho de Sistemas**

Este exercício modela uma rede com duas classes de tráfego por meio de uma **Cadeia de Markov a Tempo Contínuo (CTMC)**. A Etapa 1 implementa a geração dos estados válidos e a construção da matriz de transição infinitesimal Q.

## 1. Descrição do exercício

A rede possui capacidade total de C = 5 unidades. Existem duas classes:

- **T1 — prioritária:** possui prioridade de admissão;
- **T2 — não prioritária:** deve respeitar a reserva de duas unidades destinada a T1.

Cada conexão ocupa uma unidade. O estado é (n1, n2), em que n1 e n2 representam as quantidades de conexões T1 e T2.

Os estados válidos respeitam:

\[
n_1+n_2\leq 5,\qquad n_2\leq 5-2=3.
\]

O modelo possui **18 estados válidos**. A matriz Q contém as taxas de chegada e saída entre esses estados.

### Parâmetros

| Parâmetro | Valor | Unidade |
|---|---:|---|
| lambda1 — chegada T1 | 10 | req/min |
| lambda2 — chegada T2 | 15 | req/min |
| mu1 — serviço T1 | 15 | req/min |
| mu2 — serviço T2 | 25 | req/min |

## 2. Arquivos desta pasta

~~~text
Exercicio_3_CTMC_Controle_Admissao/
├── README.md
├── MODELAGEM_ETAPA_1.md
├── modelagem_ctmc.py
├── test_modelagem_ctmc.py
├── requirements.txt
└── resultados/
    ├── estados.csv
    └── matriz_Q.csv
~~~

- **MODELAGEM_ETAPA_1.md:** explicação matemática, estados, transições e observação sobre o enunciado.
- **modelagem_ctmc.py:** gera os 18 estados, constrói e valida Q, exibe os resultados e exporta CSVs.
- **test_modelagem_ctmc.py:** testes automáticos da implementação.
- **requirements.txt:** dependência Python necessária.
- **resultados/:** exemplos dos CSVs gerados pelo programa. A pasta também é atualizada quando o programa é executado.

## 3. Pré-requisitos

- Python 3.10 ou superior;
- pip;
- terminal (Linux, macOS ou PowerShell no Windows).

## 4. Como preparar o ambiente

Abra o terminal dentro desta pasta.

### Linux / macOS

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

### Windows (PowerShell)

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

Se o PowerShell bloquear a ativação do ambiente virtual, pode executar o Python diretamente com **.venv\Scripts\python.exe** ou ajustar a política de execução para o usuário conforme as regras do computador.

## 5. Como executar / “compilar”

Python é uma linguagem interpretada; não é necessário gerar um executável previamente. Com o ambiente virtual ativado, execute:

~~~bash
python modelagem_ctmc.py
~~~

O programa:

1. gera a lista de estados na ordem (n1,n2);
2. constrói a matriz Q de dimensão 18 × 18;
3. verifica as propriedades estruturais da matriz;
4. imprime os estados e a matriz no terminal;
5. cria a pasta resultados/ e grava estados.csv e matriz_Q.csv.

Para escolher outra pasta de saída:

~~~bash
python modelagem_ctmc.py --saida minha_saida
~~~

Os arquivos CSV podem ser abertos no Excel ou LibreOffice Calc.

## 6. Como executar os testes

Com o ambiente virtual ativado:

~~~bash
python -m unittest -v
~~~

Os testes conferem os 18 estados, as restrições de capacidade/reserva, a dimensão de Q, as taxas de transição e a soma zero das linhas.

## 7. Resultado esperado

Ao final da execução, o terminal deve informar:

~~~text
Quantidade de estados: 18
Dimensão de Q: 18 x 18
Matriz Q construída e validada com sucesso.
~~~

A soma de cada linha de Q deve ser zero (com tolerância numérica). Se algum teste falhar, a implementação deve ser revisada antes de avançar para o cálculo da distribuição estacionária.

## 8. Atenção: divergência no enunciado sobre bloqueio de T2

Na página 11, os estados válidos são definidos por n2 ≤ C-R = 3, e a construção da matriz Q segue essa restrição. Porém, a página 14 apresenta a condição n2 = R = 2 como condição de bloqueio de T2. As duas regras não coincidem.

Para a **Etapa 1**, o código segue o conjunto de estados e as transições válidas: T2 pode chegar a três conexões. A fórmula de bloqueio de T2 será tratada explicitamente na etapa dos indicadores, após confirmar com o professor qual condição deve prevalecer.

## 9. Próxima etapa

Com os estados e a matriz Q validados, a próxima etapa será resolver o sistema de equilíbrio pi Q = 0, com a normalização soma(pi) = 1, e calcular os indicadores de desempenho solicitados.
