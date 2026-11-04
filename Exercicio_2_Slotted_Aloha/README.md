# Exercício 2 — Slotted Aloha com probabilidade adaptativa

**Disciplina:** Avaliação de Desempenho de Sistemas — IFSC  
**Modelo:** DTMC com cinco estações e seis estados agregados.

## 1. Regras do sistema

Existem cinco estações. Quem não participou da colisão anterior transmite com probabilidade **a**. Quem participou de colisão usa **b** no slot atual, com 0 < b < a < 1. Um slot com zero transmissões é ocioso; com uma, há sucesso; com duas ou mais, há colisão. A adaptação dura apenas o slot seguinte e não há fila persistente ou retransmissão.

## 2. Redução de 27 para 6 estados

O modelo detalhado tinha 27 estados porque registrava a identidade exata das estações que colidiram:

~~~text
1 + C(5,2) + C(5,3) + C(5,4) + C(5,5) = 27
~~~

Para calcular vazão total, a identidade das estações não altera as probabilidades, pois todas são homogêneas e usam os mesmos valores de a e b. O modelo foi agregado pelo número de transmissões no slot anterior:

| Estado | Evento anterior | Estações que usam b agora |
|---|---|---:|
| E0 | Nenhuma transmissão (slot ocioso) | 0 |
| E1 | Uma transmissão (sucesso) | 0 |
| E2 | Colisão de duas estações | 2 |
| E3 | Colisão de três estações | 3 |
| E4 | Colisão de quatro estações | 4 |
| E5 | Colisão de cinco estações | 5 |

E0 e E1 são separados para identificar diretamente ociosidade e sucesso, mas suas linhas em P são iguais: nos dois casos todas as estações usam a no slot seguinte. Em E2–E5, respectivamente 2–5 estações usam b.

Essa agregação preserva as métricas globais de vazão, slots ociosos e colisões. Ela deixa de registrar a identidade das estações e, portanto, não serve para calcular vazão individual ou justiça entre estações.

## 3. Construção da matriz de transição

Se k é o estado atual, o número de estações usando b é:

~~~text
m(k) = 0, para k = 0 ou 1
m(k) = k, para k = 2, 3, 4 ou 5
~~~

O próximo estado j é o número de estações que transmitem no slot atual: j=0 significa ociosidade, j=1 sucesso, e j≥2 colisão. Para obter j transmissões, r ocorrem entre as m(k) estações que usam b, e j-r entre as demais que usam a:

~~~text
P(k,j) = soma, para r de max(0, j-(5-m(k))) até min(j,m(k)), de:

         C(m(k),r) b^r (1-b)^(m(k)-r)
         × C(5-m(k),j-r) a^(j-r) (1-a)^((5-m(k))-(j-r))
~~~

A matriz P tem dimensão **6 × 6**. A soma de cada linha deve ser 1. O programa exporta a matriz para resultados/matriz_transicao_P.csv.

Em E0 e E1, todas as estações usam a. Com a=0,30, ambas as linhas são [0,16807; 0,36015; 0,30870; 0,13230; 0,02835; 0,00243].

## 4. Distribuição estacionária e métricas

O programa resolve:

~~~text
pi × P = pi
soma(pi) = 1
~~~

As métricas globais são diretamente identificadas na distribuição estacionária:

~~~text
Vazão Q = pi(E1)
Slots ociosos I = pi(E0)
Slots com colisão C = pi(E2) + pi(E3) + pi(E4) + pi(E5)
Q + I + C = 1
~~~

A unidade de vazão é pacotes entregues por slot. A implementação também calcula as probabilidades condicionais de cada evento em cada estado e pondera esses valores por pi.

## 5. Resultados de referência

Para a=0,30 e b=0,10:

| Estado | Probabilidade estacionária |
|---|---:|
| E0 — ocioso | 0,223211 |
| E1 — sucesso | 0,383423 |
| E2 — colisão de 2 | 0,272075 |
| E3 — colisão de 3 | 0,100390 |
| E4 — colisão de 4 | 0,019344 |
| E5 — colisão de 5 | 0,001557 |

| Métrica | Resultado teórico |
|---|---:|
| Vazão | 0,383423 pacotes/slot |
| Slots ociosos | 22,3211% |
| Slots com colisão | 39,3366% |

Esses resultados coincidem com a formulação original de 27 estados para os mesmos parâmetros. A redução muda a representação da cadeia, não as métricas globais.

## 6. Arquivos e execução

- slotted_aloha.py: monta a matriz 6 × 6, calcula pi e as métricas, simula slots e grava os resultados.
- test_model.py: testes automatizados da quantidade de estados, matriz, distribuição e preservação das métricas.
- requirements.txt: dependência NumPy.
- resultados/: arquivos CSV e JSON gerados durante a execução; a pasta é criada automaticamente e ignorada pelo Git.

No Linux:

~~~bash
git clone https://github.com/BeatrizPAbreu/ADS.git
cd ADS/Exercicio_2_Slotted_Aloha
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python slotted_aloha.py --a 0.30 --b 0.10 --simulate 100000 --seed 2026
python -m unittest -v
~~~

Parâmetros disponíveis: --a (padrão 0.30), --b (padrão 0.10), --simulate (padrão 100000), --seed (padrão 2026) e --output-dir (padrão resultados). Deve ser respeitada a condição 0 < b < a < 1.

A simulação de Monte Carlo deve produzir valores próximos dos teóricos, mas não necessariamente idênticos, por causa da aleatoriedade e do número finito de slots.