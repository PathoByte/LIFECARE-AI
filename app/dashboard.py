import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# Load data and model
@st.cache_data
def load_data():
    return pd.read_csv('data/processed_health_data.csv')

@st.cache_resource
def load_model():
    return joblib.load('models/anomaly_model.pkl')

df = load_data()
model = load_model()

# Predict anomalies
df['anomaly_score'] = model.decision_function(df[['heart_rate', 'blood_oxygen']])
df['anomaly'] = ['Anomaly' if x < 0 else 'Normal' for x in df['anomaly_score']]

# --- UI ---
st.set_page_config(layout="wide")
st.title("🩺 Real-World Health Monitor (Kaggle Data)")

# Metrics
latest = df.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Heart Rate", f"{latest['heart_rate']} bpm", 
            delta_color="inverse" if latest['anomaly'] == 'Anomaly' else "normal")
col2.metric("Blood Oxygen", f"{latest['blood_oxygen']}%")
col3.metric("Status", latest['anomaly'], 
            delta="⚠️ Alert" if latest['anomaly'] == 'Anomaly' else "✅ Normal")

# Interactive Plotly chart
st.subheader("Live Vitals Trend")
fig = px.line(df.tail(100), x='timestamp', y=['heart_rate', 'blood_oxygen'],
              color_discrete_map={'heart_rate': 'red', 'blood_oxygen': 'blue'})
st.plotly_chart(fig, use_container_width=True)

# Anomaly details
st.subheader("Anomaly Detection Results")
st.dataframe(df[df['anomaly'] == 'Anomaly'].tail(10))

# Health advice
st.subheader("AI Recommendations")
if latest['anomaly'] == 'Anomaly':
    st.error("""
    🚨 Critical Alert: 
    - Rest immediately and measure vitals again.
    - Contact healthcare provider if symptoms persist.
    """)
else:
    st.success("""
    ✅ All systems normal. 
    - Maintain hydration and regular activity.
    """)