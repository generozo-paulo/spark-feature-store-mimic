# Especificação Contratual (SDD) - Spark Feature Store for MIMIC Critical Care

## 1. Escopo & Objetivos
Feature Store distribuída inspirada no schema MIMIC-IV para modelos preditivos de UTI (ex: predição de choque séptico e mortalidade em 48h).
Implementa:
1. Extração de variáveis temporais em janelas móveis de 6h, 12h e 24h pós-admissão em UTI.
2. Controle estrito de vazamento de dados (**Data Leakage Prevention**) com agregação point-in-time (`as-of join`).
3. Repositório central de features com metadata de linhagem e esquema versionado.

## 2. Contratos de Entrada (Pydantic)

### 2.1 Série Temporal de Sinais Vitais / Laboratório (`MIMICTelemetryPoint`)
- `patient_id`: str
- `icu_stay_id`: str
- `charttime`: str
- `heart_rate`: float
- `map_pressure`: float
- `lactate_mmol_l`: Optional[float] = None
- `spo2_pct`: float

## 3. Contratos de Saída (Pydantic)

### 3.1 Feature Vector de UTI (`ICUFeatureVector`)
- `icu_stay_id`: str
- `patient_id`: str
- `feature_timestamp`: str
- `hr_mean_24h`: float
- `hr_max_24h`: float
- `map_min_24h`: float
- `shock_index_max`: float # HR / MAP
- `lactate_last_known`: float
- `sepsis_risk_label_48h`: int
