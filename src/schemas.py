from pydantic import BaseModel, Field
from typing import Optional, List

class MIMICTelemetryPoint(BaseModel):
    patient_id: str
    icu_stay_id: str
    charttime: str
    heart_rate: float
    map_pressure: float
    lactate_mmol_l: Optional[float] = None
    spo2_pct: float

class ICUFeatureVector(BaseModel):
    icu_stay_id: str
    patient_id: str
    feature_timestamp: str
    hr_mean_24h: float
    hr_max_24h: float
    map_min_24h: float
    shock_index_max: float
    lactate_last_known: float
    sepsis_risk_label_48h: int
