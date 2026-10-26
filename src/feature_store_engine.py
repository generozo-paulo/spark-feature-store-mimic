import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from src.schemas import MIMICTelemetryPoint, ICUFeatureVector

class MIMICFeatureStoreEngine:
    """
    Motor distribuído de Feature Store para séries temporais de UTI e biomarcadores críticos.
    """

    @staticmethod
    def generate_mimic_telemetry(n_patients: int = 50, points_per_patient: int = 24, random_state: int = 42) -> pd.DataFrame:
        """Simula telemetria horária de pacientes em UTI ao longo das primeiras 24 horas."""
        np.random.seed(random_state)
        records = []
        base_time = datetime(2025, 6, 1, 8, 0, 0)

        for p_idx in range(n_patients):
            pid = f"PAC-{p_idx+1:04d}"
            stay_id = f"ICU-{p_idx+1:05d}"
            # Perfil do paciente: 20% com deterioração hemodinâmica
            is_deteriorating = (p_idx % 5 == 0)

            for hour in range(points_per_patient):
                charttime = base_time + timedelta(hours=hour)
                if is_deteriorating:
                    hr = float(np.random.normal(loc=95 + hour*1.2, scale=8)) # taquicardia crescente
                    map_p = float(np.random.normal(loc=72 - hour*0.8, scale=6)) # hipotensão
                    lactate = float(1.2 + (hour * 0.15)) if hour % 6 == 0 else np.nan
                    spo2 = float(np.clip(np.random.normal(loc=95 - hour*0.2, scale=2), 78, 100))
                else:
                    hr = float(np.random.normal(loc=76, scale=6))
                    map_p = float(np.random.normal(loc=82, scale=5))
                    lactate = float(1.1) if hour % 6 == 0 else np.nan
                    spo2 = float(np.clip(np.random.normal(loc=98, scale=1), 92, 100))

                records.append({
                    "patient_id": pid,
                    "icu_stay_id": stay_id,
                    "charttime": charttime.isoformat(),
                    "heart_rate": round(max(hr, 35.0), 1),
                    "map_pressure": round(max(map_p, 30.0), 1),
                    "lactate_mmol_l": round(lactate, 2) if pd.notnull(lactate) else None,
                    "spo2_pct": round(spo2, 1)
                })

        return pd.DataFrame(records)

    @staticmethod
    def compute_icu_feature_store(telemetry_df: pd.DataFrame) -> pd.DataFrame:
        """Agregação temporal point-in-time e extração de features fisiológicas complexas."""
        df = telemetry_df.copy()
        df["shock_index"] = df["heart_rate"] / df["map_pressure"]

        # Forward-fill de lactato (amostragem intermitente clássica em UTI)
        df["lactate_filled"] = df.groupby("icu_stay_id")["lactate_mmol_l"].ffill().bfill()

        # Agregação por episódio de UTI
        feature_df = df.groupby(["icu_stay_id", "patient_id"]).agg(
            hr_mean_24h=("heart_rate", "mean"),
            hr_max_24h=("heart_rate", "max"),
            map_min_24h=("map_pressure", "min"),
            shock_index_max=("shock_index", "max"),
            lactate_last_known=("lactate_filled", "last"),
            spo2_min_24h=("spo2_pct", "min")
        ).reset_index()

        feature_df["hr_mean_24h"] = feature_df["hr_mean_24h"].round(1)
        feature_df["hr_max_24h"] = feature_df["hr_max_24h"].round(1)
        feature_df["map_min_24h"] = feature_df["map_min_24h"].round(1)
        feature_df["shock_index_max"] = feature_df["shock_index_max"].round(3)
        feature_df["lactate_last_known"] = feature_df["lactate_last_known"].round(2)

        # Regra de Ground Truth (Sepsis / Shock 48h): Shock Index > 1.0 ou Lactato > 2.0 mmol/L
        feature_df["sepsis_risk_label_48h"] = (
            (feature_df["shock_index_max"] >= 1.0) | (feature_df["lactate_last_known"] >= 2.5)
        ).astype(int)

        feature_df["feature_timestamp"] = datetime.now().isoformat()
        return feature_df
