# Etapa 1 — Modelagem da CTMC e construção da matriz Q

## 1. Objetivo

Modelar uma rede com controle de admissão de duas classes de tráfego usando uma Cadeia de Markov a Tempo Contínuo (CTMC). Nesta etapa são definidos os estados válidos e construída a matriz de transição infinitesimal (matriz geradora) Q.

## 2. Parâmetros do enunciado

| Parâmetro | Significado | Valor |
|---|---|---:|
| C | Capacidade total do sistema | 5 unidades |
| R | Reserva mínima para T1 | 2 unidades |
| lambda1 | Taxa de chegada de T1 | 10 req/min |
| lambda2 | Taxa de chegada de T2 | 15 req/min |
| mu1 | Taxa de serviço de cada conexão T1 | 15 req/min |
| mu2 | Taxa de serviço de cada conexão T2 | 25 req/min |

T1 é o tráfego prioritário e T2 é o tráfego não prioritário. Cada sessão ocupa uma unidade de capacidade.

## 3. Representação dos estados

Um estado é representado pelo par:

\[
(n_1,n_2)
\]

em que n1 é o número de conexões T1 e n2 é o número de conexões T2.

Conforme as restrições de capacidade e reserva apresentadas no enunciado, um estado é válido quando:

\[
n_1+n_2\leq C=5
\]

\[
n_2\leq C-R=3.
\]

Assim, o conjunto possui 18 estados, na ordem usada pelo programa:

~~~text
(0,0), (0,1), (0,2), (0,3),
(1,0), (1,1), (1,2), (1,3),
(2,0), (2,1), (2,2), (2,3),
(3,0), (3,1), (3,2),
(4,0), (4,1),
(5,0)
~~~

A ordem é importante porque define a correspondência entre cada estado e a linha/coluna da matriz Q.

## 4. Transições e taxas

A partir de um estado (n1,n2), podem ocorrer quatro eventos:

| Evento | Próximo estado | Taxa |
|---|---|---:|
| Chegada de T1 | (n1+1,n2) | lambda1, se o próximo estado for válido |
| Chegada de T2 | (n1,n2+1) | lambda2, se o próximo estado for válido |
| Saída de T1 | (n1-1,n2) | n1 × mu1, se n1 > 0 |
| Saída de T2 | (n1,n2-1) | n2 × mu2, se n2 > 0 |

A taxa de saída é multiplicada pelo número de conexões da classe porque qualquer conexão ativa daquela classe pode terminar.

Se o estado de destino não pertence ao conjunto de estados válidos, a transição de chegada não é incluída. Isso representa o bloqueio da nova solicitação no modelo de admissão.

## 5. Matriz infinitesimal Q

Q[i,j] representa a taxa de transição do estado i para o estado j, para i diferente de j. A diagonal principal é definida por:

\[
Q_{ii}=-\sum_{j\ne i}Q_{ij}.
\]

Portanto, as taxas fora da diagonal são não negativas e a soma dos elementos de cada linha é zero:

\[
\sum_j Q_{ij}=0.
\]

Para este exercício, Q possui dimensão 18 × 18. As taxas são expressas em requisições por minuto.

## 6. Observação sobre o enunciado

O conjunto de estados e a definição da matriz Q indicam que n2 pode chegar a C-R=3. Já a expressão de bloqueio de T2 na página 14 do material informa n2=R, isto é, n2=2. Essa condição não coincide com a restrição de admissão usada para construir os estados e as transições de chegada.

Nesta Etapa 1, o código segue as restrições explícitas do conjunto de estados e da matriz Q: T2 pode ocupar até C-R=3 unidades. A definição da probabilidade de bloqueio deve ser conferida/explicitada com o professor antes da Etapa 2.

## 7. Validações implementadas

O programa verifica automaticamente:

- existência de exatamente 18 estados;
- dimensão 18 × 18 da matriz Q;
- soma zero em cada linha;
- taxas fora da diagonal não negativas;
- valores da diagonal não positivos.

Também há testes unitários para estados, restrições, taxas de chegada e saída.
