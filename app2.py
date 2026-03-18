import streamlit as st
import joblib
import pandas as pd
import numpy as np

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Seakeeping Monitor V2", layout="wide")
st.title("🚢 Monitor Seakeeping Kapal Ikan (Versi 2)")
st.markdown("Analisis Respon Signifikan pada Gelombang Acak (*Irregular Waves*)")

# 2. Fungsi Load Model
@st.cache_resource
def load_model():
    # Pastikan nama file .sav sama dengan yang kamu simpan di Colab tadi
    return joblib.load('model_seakeeping_final.sav')

try:
    model = load_model()

    # 3. Sidebar Input (4 Variabel)
    st.sidebar.header("⚙️ Parameter Input")
    hs = st.sidebar.slider("Tinggi Gelombang Signifikan / Hs (m)", 0.5, 5.0, 1.5)
    tp = st.sidebar.slider("Periode Puncak / Tp (s)", 2.0, 12.0, 6.0)
    spd = st.sidebar.slider("Kecepatan Kapal (Knot)", 0, 20, 10)
    hdg = st.sidebar.slider("Heading / Arah Gelombang (Deg)", 0, 180, 90)

    # 4. Proses Prediksi
    # Nama kolom HARUS SAMA PERSIS dengan saat training di Colab
    input_data = pd.DataFrame([[hs, tp, spd, hdg]], 
                             columns=['Hs_m', 'Tp_s', 'Speed_Kts', 'Heading_deg'])
    
    prediction = model.predict(input_data)
    h_sig, p_sig, r_sig = prediction[0][0], prediction[0][1], prediction[0][2]

    # 5. Dashboard Hasil (Metrics)
    st.subheader("📊 Respon Signifikan Kapal")
    c1, c2, c3 = st.columns(3)
    
    # Menampilkan hasil dengan indikator warna (Delta)
    c1.metric("Heave Signifikan", f"{h_sig:.2f} m")
    c2.metric("Pitch Signifikan", f"{p_sig:.2f} °")
    c3.metric("Roll Signifikan", f"{r_sig:.2f} °")

    # 6. Analisis Keselamatan (Indeks Operabilitas)
    st.divider()
    st.subheader("🚨 Status Keselamatan (Standard NORDFORSK)")
    
    # Kriteria Batas
    limit_roll = 3.0
    limit_pitch = 1.5
    
    is_roll_safe = r_sig <= limit_roll
    is_pitch_safe = p_sig <= limit_pitch
    
    # Hitung Skor
    skor = (int(is_roll_safe) + int(is_pitch_safe)) / 2 * 100

    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.write("**Hasil Evaluasi:**")
        st.write(f"Roll (Maks 3°): {'✅ AMAN' if is_roll_safe else '❌ BAHAYA'}")
        st.write(f"Pitch (Maks 1.5°): {'✅ AMAN' if is_pitch_safe else '❌ BAHAYA'}")
        
    with col_b:
        if skor == 100:
            st.success(f"**INDEKS OPERABILITAS: {skor:.0f}%**\n\nKapal layak beroperasi penuh.")
        elif skor >= 50:
            st.warning(f"**INDEKS OPERABILITAS: {skor:.0f}%**\n\nWaspada! Batasi aktivitas di dek.")
        else:
            st.error(f"**INDEKS OPERABILITAS: {skor:.0f}%**\n\nBahaya! Segera ubah heading atau cari perlindungan.")

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.info("Pastikan file 'model_seakeeping_final.sav' sudah di-upload ke GitHub.")

# Footer
st.divider()
st.caption("Dikembangkan untuk Riset Operabilitas Kapal Ikan Kecil")
