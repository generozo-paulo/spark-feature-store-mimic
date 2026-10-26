import pytest
from src.feature_store_engine import MIMICFeatureStoreEngine

def test_telemetry_generation():
    telemetry = MIMICFeatureStoreEngine.generate_mimic_telemetry(n_patients=10, points_per_patient=12)
    assert len(telemetry) == 120
    assert "heart_rate" in telemetry.columns
    assert "map_pressure" in telemetry.columns

def test_feature_store_computation():
    telemetry = MIMICFeatureStoreEngine.generate_mimic_telemetry(n_patients=20, points_per_patient=24)
    features = MIMICFeatureStoreEngine.compute_icu_feature_store(telemetry)
    assert len(features) == 20
    assert "shock_index_max" in features.columns
    assert "lactate_last_known" in features.columns
    assert "sepsis_risk_label_48h" in features.columns
    assert (features["shock_index_max"] > 0).all()
