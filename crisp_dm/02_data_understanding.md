# CRISP-DM: Entendimento de Dados (Data Understanding - MIMIC Critical Care)

## 1. Problema de Engenharia de Features em Terapia Intensiva
Dados de monitores multiparamétricos em UTI registram telemetria minuto a minuto, enquanto exames laboratoriais como lactato e gasometria são esporádicos.
O cálculo manual ou inconsistente de variáveis em janelas temporais leva a inconsistências de treino/serviço (**Train-Serve Skew**) e vazamento de dados futuros.

## 2. Princípios da Feature Store MIMIC
- **Imutabilidade e Reuso**: Um único pipeline distribui features tanto para treino batch quanto para inferência online.
- **Join Point-in-Time**: Features calculadas rigorosamente até o momento do evento $T$, sem acesso a medições posteriores.
- **Relações Fisiológicas Complexas**: Cálculo do *Shock Index* ($\frac{\text{Heart Rate}}{\text{Mean Arterial Pressure}}$) em tempo real.
