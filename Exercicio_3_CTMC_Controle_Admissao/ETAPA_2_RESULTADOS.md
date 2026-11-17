# Etapa 2 — Distribuição estacionária e indicadores de desempenho

## 1. Objetivo

A partir da matriz infinitesimal Q construída na Etapa 1, obter a distribuição estacionária pi e calcular os indicadores pedidos no miniprojeto (página 8 do material): probabilidades de bloqueio de T1 e T2, utilização média, número médio de conexões de cada classe e fração do tempo na capacidade máxima.

Parâmetros: C=5, R=2, lambda1=10 req/min, lambda2=15 req/min, mu1=15 req/min e mu2=25 req/min.

## 2. Distribuição estacionária

A distribuição estacionária satisfaz:

\[
\pi Q=0,\qquad \sum_{s\in S}\pi(s)=1.
\]

Como Q foi construída na convenção em que cada linha soma zero, o código resolve o sistema equivalente Q transposta vezes pi-coluna igual a zero, substituindo uma equação pela condição de normalização.

A solução também possui forma-produto:

\[
\pi(n_1,n_2)=\frac{1}{Z}
\frac{(\lambda_1/\mu_1)^{n_1}}{n_1!}
\frac{(\lambda_2/\mu_2)^{n_2}}{n_2!},
\]

para os estados válidos. A constante de normalização é a soma dos pesos nos 18 estados:

\[
Z=3{,}532389574760.
\]

O programa resolve pi Q=0 e compara o vetor obtido com essa forma-produto como verificação independente. Os resultados coincidem numericamente.

### Distribuição estacionária calculada

| Estado | pi | Percentual |
|---|---:|---:|
| (0,0) | 0,28309448 | 28,3094% |
| (0,1) | 0,16985669 | 16,9857% |
| (0,2) | 0,05095701 | 5,0957% |
| (0,3) | 0,01019140 | 1,0191% |
| (1,0) | 0,18872966 | 18,8730% |
| (1,1) | 0,11323779 | 11,3238% |
| (1,2) | 0,03397134 | 3,3971% |
| (1,3) | 0,00679427 | 0,6794% |
| (2,0) | 0,06290989 | 6,2910% |
| (2,1) | 0,03774593 | 3,7746% |
| (2,2) | 0,01132378 | 1,1324% |
| (2,3) | 0,00226476 | 0,2265% |
| (3,0) | 0,01397997 | 1,3980% |
| (3,1) | 0,00838798 | 0,8388% |
| (3,2) | 0,00251640 | 0,2516% |
| (4,0) | 0,00233000 | 0,2330% |
| (4,1) | 0,00139800 | 0,1398% |
| (5,0) | 0,00031067 | 0,0311% |

A soma das 18 probabilidades é 1. O resíduo numérico máximo de pi Q na execução de referência foi da ordem de 10 elevado a -15.

## 3. Indicadores

### 3.1 Bloqueio de T1

Conforme a página 14, T1 é bloqueado quando a capacidade total está ocupada:

\[
P_{rej,T1}=\sum_{n_1+n_2=C}\pi(n_1,n_2).
\]

Resultado: **0,00648981 = 0,6490%**.

### 3.2 Bloqueio de T2 — divergência no enunciado

A página 14 do PDF afirma que T2 é bloqueado quando n1+n2=C ou n2=R. Aplicando literalmente a expressão, com R=2:

\[
P_{rej,T2}^{(pág.14)}
=\sum_{\{(n_1,n_2): n_1+n_2=5\ ou\ n_2=2\}}\pi(n_1,n_2).
\]

Resultado literal: **0,10274194 = 10,2742%**.

Entretanto, os estados e a matriz Q da Etapa 1 permitem no máximo C-R=3 conexões T2. Pela regra de admissão implementada, uma chegada T2 é recusada quando a capacidade total está ocupada ou quando já existem três conexões T2:

\[
P_{rej,T2}^{(Q)}
=\sum_{\{(n_1,n_2): n_1+n_2=5\ ou\ n_2=C-R=3\}}\pi(n_1,n_2).
\]

Resultado compatível com Q: **0,02347548 = 2,3475%**.

**Atenção:** os dois valores não são intercambiáveis. O primeiro reproduz literalmente o slide; o segundo corresponde à política de admissão representada pelos estados e por Q. É necessário confirmar com o professor se n2=R na página 14 é erro de digitação ou se existe uma regra adicional que não foi incorporada à matriz Q.

### 3.3 Utilização média

Fórmula da página 15:

\[
U=\frac{1}{C}\sum_{(n_1,n_2)}(n_1+n_2)\pi(n_1,n_2).
\]

Resultado: **0,24965097 = 24,9651%**.

### 3.4 Número médio de conexões simultâneas

\[
L_1=\sum_{(n_1,n_2)}n_1\pi(n_1,n_2),\qquad
L_2=\sum_{(n_1,n_2)}n_2\pi(n_1,n_2).
\]

Resultados: **L1 = 0,66234012 conexões** e **L2 = 0,58591471 conexões**. A média total é 1,24825483 conexões.

### 3.5 Fração do tempo em capacidade máxima

\[
P_{max}=\sum_{n_1+n_2=5}\pi(n_1,n_2).
\]

Resultado: **0,00648981 = 0,6490%**. Coincide com o bloqueio T1 porque T1 só é bloqueado quando as cinco unidades estão ocupadas.

## 4. Resumo

| Indicador | Resultado |
|---|---:|
| Bloqueio T1 | 0,6490% |
| Bloqueio T2 — literal da página 14 | 10,2742% |
| Bloqueio T2 — consistente com Q | 2,3475% |
| Utilização média | 24,9651% |
| Média de conexões T1 | 0,6623 |
| Média de conexões T2 | 0,5859 |
| Tempo em capacidade máxima | 0,6490% |

Para os parâmetros fornecidos, o bloqueio de T1 fica abaixo de 3% (0,6490%). O valor final do bloqueio T2 depende da confirmação da regra divergente no material.

## 5. Execução

Na pasta do exercício, com o ambiente virtual e NumPy instalados:

\`\`\`bash
python analise_ctmc.py
python -m unittest -v
\`\`\`

O programa gera os arquivos resultados/distribuicao_estacionaria.csv e resultados/indicadores_etapa2.csv.
