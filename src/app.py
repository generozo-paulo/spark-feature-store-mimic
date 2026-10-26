import streamlit as st
import pandas as pd
import plotly.express as px
from src.feature_store_engine import MIMICFeatureStoreEngine

st.set_page_config(
    page_title="MIMIC-IV Distributed ICU Feature Store",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ MIMIC-IV Critical Care Distributed Feature Store")
st.markdown("""
Repositório centralizado de **Features Fisiológicas de UTI** processadas em janelas temporais de 24h sem vazamento de dados (**Point-in-Time Joins**) para predição precoce de sepse e choque hemodinâmico.
""")

@st.cache_data
def get_data():
    telemetry = MIMICFeatureStoreEngine.generate_mimic_telemetry(n_patients=60)
    features = MIMICFeatureStoreEngine.compute_icu_feature_store(telemetry)
    return telemetry, features

raw_telemetry, feature_store_df = get_data()

tab1, tab2, tab3 = st.tabs(["📦 Repositório Feature Store", "📈 Telemetria Temporal (MIMIC Signals)", "🧬 Dicionário & Metadata de Linhagem"])

with tab1:
    st.subheader("Features Prontas para Treinamento e Inferência Online")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Pacientes / Leitos", len(feature_store_df))
    c2.metric("Pacientes em Risco de Sepse (48h)", f"{feature_store_df['sepsis_risk_label_48h'].sum()} ({feature_store_df['sepsis_risk_label_48h'].mean():.1%})")
    c3.metric("Média Shock Index Máx.", f"{feature_store_df['shock_index_max'].mean():.2f}")
    c4.metric("Lactato Médio", f"{feature_store_df['lactate_last_known'].mean():.2f} mmol/L")

    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = px.histogram(
            feature_store_df,
            x="shock_index_max",
            color="sepsis_risk_label_48h",
            title="Distribuição do Shock Index Máximo (Alerta se > 1.0)",
            labels={"shock_index_max": "Shock Index Máx.", "sepsis_risk_label_48h": "Risco de Choque (1/0)"},
            color_discrete_map={0: "#2ca02c", 1: "#d62728"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        fig2 = px.scatter(
            feature_store_df,
            x="hr_max_24h",
            y="map_min_24h",
            color="sepsis_risk_label_48h",
            size="lactate_last_known",
            title="Mapa Hemodinâmico: FC Máxima vs. PAM Mínima",
            labels={"hr_max_24h": "FC Máx. 24h (bpm)", "map_min_24h": "PAM Mín. 24h (mmHg)"},
            color_discrete_map={0: "#2ca02c", 1: "#d62728"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Tabela da Feature Store (Batch View)")
    st.dataframe(feature_store_df, use_container_width=True)

with tab2:
    st.subheader("Telemetria Horária de Pacientes Selecionados")
    selected_patient = st.selectbox("Selecione o leito/paciente para inspecionar:", feature_store_df["patient_id"].unique())
    patient_telemetry = raw_telemetry[raw_telemetry["patient_id"] == selected_patient].sort_values("charttime")

    fig_time = px.line(
        patient_telemetry,
        x="charttime",
        y=["heart_rate", "map_pressure"],
        title=f"Evolução Temporal das Primeiras 24h ({selected_patient})",
        labels={"value": "Medição", "charttime": "Hora do Registro", "variable": "Sinal Vital"}
    )
    st.plotly_chart(fig_time, use_container_width=True)

with tab3:
    st.subheader("Metadados, Esquema e Linhagem da Feature Store")
    metadata = pd.DataFrame([
        {"Feature Name": "hr_mean_24h", "Entity": "icu_stay_id", "Type": "Double", "Window": "24 hours", "Description": "Frequência cardíaca média nas primeiras 24 horas"},
        {"Feature Name": "map_min_24h", "Entity": "icu_stay_id", "Type": "Double", "Window": "24 hours", "Description": "Pressão arterial média mínima registrada no leito"},
        {"Feature Name": "shock_index_max", "Entity": "icu_stay_id", "Type": "Double", "Window": "24 hours", "Description": "Razão máxima entre FC e PAM (indicador precoce de choque)"},
        {"Feature Name": "lactate_last_known", "Entity": "icu_stay_id", "Type": "Double", "Window": "Point-in-time", "Description": "Último valor de lactato arterial disponível antes do evento"}
    ])
    st.dataframe(metadata, use_container_width=True)
