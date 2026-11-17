# Miniprojeto CTMC — Controle de Admissão

Disciplina: **ADS29009 — Avaliação de Desempenho de Sistemas**

Modelagem e análise de uma rede com duas classes de tráfego por meio de uma Cadeia de Markov a Tempo Contínuo (CTMC).

## Parâmetros do sistema

- Capacidade total: C = 5 unidades.
- Reserva mínima para tráfego prioritário T1: R = 2 unidades.
- Chegadas: lambda1 = 10 req/min e lambda2 = 15 req/min.
- Serviços: mu1 = 15 req/min e mu2 = 25 req/min.

O estado é (n1,n2), em que n1 e n2 são as conexões T1 e T2. Os estados válidos respeitam n1+n2 ≤ 5 e n2 ≤ C-R=3.

## Estrutura

\`\`\`text
Exercicio_3_CTMC_Controle_Admissao/
├── README.md
├── MODELAGEM_ETAPA_1.md
├── ETAPA_2_RESULTADOS.md
├── modelagem_ctmc.py
├── analise_ctmc.py
├── test_modelagem_ctmc.py
├── test_analise_ctmc.py
├── requirements.txt
└── resultados/
    ├── estados.csv
    ├── matriz_Q.csv
    ├── distribuicao_estacionaria.csv
    └── indicadores_etapa2.csv
\`\`\`

## Preparação do ambiente

Requer Python 3.10 ou superior e pip.

### Linux / macOS

\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
\`\`\`

### Windows (PowerShell)

\`\`\`powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
\`\`\`

## Etapa 1 — Estados e matriz Q

\`\`\`bash
python modelagem_ctmc.py
\`\`\`

Gera os 18 estados válidos, constrói a matriz infinitesimal Q (18 × 18), verifica se cada linha soma zero e exporta estados.csv e matriz_Q.csv para a pasta resultados/.

## Etapa 2 — Equilíbrio e indicadores

\`\`\`bash
python analise_ctmc.py
\`\`\`

Resolve pi Q = 0 com soma(pi)=1, confere a solução pela forma-produto e calcula os indicadores de desempenho. Exporta distribuicao_estacionaria.csv e indicadores_etapa2.csv para a pasta resultados/.

A saída inclui duas interpretações do bloqueio T2: a expressão literal da página 14 (n2=R) e a regra coerente com a matriz Q (n2=C-R). O motivo está documentado em ETAPA_2_RESULTADOS.md e precisa ser confirmado com o professor.

## Testes automatizados

\`\`\`bash
python -m unittest -v
\`\`\`

O comando executa os testes das Etapas 1 e 2.

## Observação sobre o bloqueio T2

A página 11 limita n2 a C-R=3 e a matriz Q segue essa regra. A página 14, porém, usa n2=R=2 na definição de bloqueio de T2. Como as condições divergem, o programa apresenta os dois cálculos separadamente sem escolher silenciosamente um deles.

## Próxima etapa

A Etapa 3 implementará uma simulação da CTMC durante T=10.000 minutos e comparará a distribuição e os indicadores simulados com os resultados analíticos desta etapa.
