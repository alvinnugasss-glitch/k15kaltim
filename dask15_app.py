import streamlit as st
import pandas as pd
import base64
import copy

# 1. Konfigurasi Halaman & Tema Warna
st.set_page_config(page_title="Dashboard OJT Kaltim K15", layout="wide", page_icon="⚓")

# Custom CSS untuk card shape, metrik, dan card progres mahasiswa
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3 { color: #0F172A; }
    .stProgress .st-bo { background-color: #EAB308; }
    div[data-testid="stSidebar"] { background-color: #1E3A8A; }
    div[data-testid="stSidebar"] * { color: white !important; }
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: center;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #1E3A8A;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-title {
        font-size: 14px;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        color: #0F172A;
        font-weight: 700;
    }
    .mhs-card {
        background-color: #ffffff;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .progress-section-title {
        font-weight: 700;
        color: #1E3A8A;
        margin-top: 10px;
        margin-bottom: 5px;
        font-size: 14px;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Helper & Inisialisasi Data (Session State)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'students' not in st.session_state:
    st.session_state['students'] = [
        {
            "id": 1, "Nama": "Raden Mas Alvin Sastrowardhana", "Asal Domisili": "Samarinda", 
            "Program Studi": "Teknik Perancangan dan Konstruksi Kapal", "Perusahaan": "PT Dumas Surabaya", 
            "Foto": "https://ui-avatars.com/api/?name=Alvin&background=EAB308&color=fff&size=200",
            # Menggunakan struktur data dictionary/list yang lebih rapi untuk admin editor
            "Logbook": [{"Minggu": "Week 1", "Status": "Selesai"}, {"Minggu": "Week 2", "Status": "Selesai"}, {"Minggu": "Week 3", "Status": "Selesai"}, {"Minggu": "Week 4", "Status": "Belum"}, {"Minggu": "Week 5", "Status": "Belum"}],
            "Laporan": [{"Bab/Progres": "Selesai Bab 1"}, {"Bab/Progres": "On Progress Bab 2"}, {"Bab/Progres": "On Progress Bab 3"}],
            "TugasAkhir": "Sedang mempersiapkan penelitian mengenai stabilitas dan olah gerak hopper barge. Apabila tidak kendala topik ini akan saya gunakan.\n\nNote: Mulai OJT lebih awal pada 28 Juli 2026."
        }
    ]
    for i in range(2, 12):
        st.session_state['students'].append({
            "id": i, "Nama": f"Mahasiswa {i}", "Asal Domisili": "-", 
            "Program Studi": "-", "Perusahaan": "-", 
            "Foto": f"https://ui-avatars.com/api/?name=M+{i}&background=EAB308&color=fff&size=200",
            "Logbook": [{"Minggu": "Week 1", "Status": "Belum"}],
            "Laporan": [{"Bab/Progres": "Belum dimulai"}],
            "TugasAkhir": "Belum ditentukan"
        })

if 'proker_list' not in st.session_state:
    st.session_state['proker_list'] = [
        {
            "id": 1, "Nama Agenda": "Penerimaan OJT", "Status": "Selesai", "Progres": 100, "PIC": "Divisi Internal",
            "Waktu Pelaksanaan": "Agustus (Minggu ke-4)", "Rentang Waktu Persiapan": "Agustus (Minggu ke-1 s.d ke-3)",
            "Ketua": "Budi", "Sekretaris": "Ani", "Bendahara": "Citra",
            "Divisi": [{"Nama Divisi": "Perlengkapan", "Jobdesk": "Mempersiapkan lokasi dan alat"}, 
                       {"Nama Divisi": "Pubdok", "Jobdesk": "Desain poster"}],
            "Tautan": [{"Keterangan": "Proposal Kegiatan", "URL": "https://drive.google.com/..."}],
            "Tahapan": [
                {"Tahapan Kegiatan": "Pembentukan panitia & konsep", "B_Mulai": "Agustus", "M_Mulai": "W1", "B_Selesai": "Agustus", "M_Selesai": "W1"},
                {"Tahapan Kegiatan": "Penyusunan proposal & anggaran", "B_Mulai": "Agustus", "M_Mulai": "W1", "B_Selesai": "Agustus", "M_Selesai": "W2"},
                {"Tahapan Kegiatan": "Persiapan teknis & perlengkapan", "B_Mulai": "Agustus", "M_Mulai": "W2", "B_Selesai": "Agustus", "M_Selesai": "W3"},
                {"Tahapan Kegiatan": "Pelaksanaan Penerimaan OJT", "B_Mulai": "Agustus", "M_Mulai": "W4", "B_Selesai": "Agustus", "M_Selesai": "W4"},
                {"Tahapan Kegiatan": "Evaluasi & laporan", "B_Mulai": "September", "M_Mulai": "W1", "B_Selesai": "September", "M_Selesai": "W1"}
            ],
            "Evaluasi": "Berjalan lancar", "Color": "#E74C3C"
        }
    ]

if 'album_list' not in st.session_state:
    st.session_state['album_list'] = [p["Nama Agenda"] for p in st.session_state['proker_list']]

if 'album_data' not in st.session_state:
    st.session_state['album_data'] = { album: [] for album in st.session_state['album_list'] }

BULAN = ["Agustus", "September", "Oktober", "November", "Desember"]
MINGGU = ["W1", "W2", "W3", "W4"]
TUPLES = [(b, m) for b in BULAN for m in MINGGU]

def get_week_index(bulan, minggu):
    return BULAN.index(bulan) * 4 + MINGGU.index(minggu)

def render_time_schedule():
    st.subheader("📅 Time Schedule Program Kerja & Agenda")
    st.caption("Periode Agustus – Desember")
    
    schedule_data = []
    for p in st.session_state['proker_list']:
        if not p.get("Tahapan"): continue
        
        for i, t in enumerate(p["Tahapan"]):
            if not t.get("Tahapan Kegiatan") or str(t.get("Tahapan Kegiatan")).strip() == "":
                continue
                
            row = {
                "Program Kerja": p["Nama Agenda"], 
                "_Raw_PK": p["Nama Agenda"],
                "_Color": p.get("Color", "#EAB308"),
                "Tahapan Kegiatan": t["Tahapan Kegiatan"]
            }
            
            start_idx = get_week_index(t.get("B_Mulai", "Agustus"), t.get("M_Mulai", "W1"))
            end_idx = get_week_index(t.get("B_Selesai", "Agustus"), t.get("M_Selesai", "W1"))
            
            for idx, (b, m) in enumerate(TUPLES):
                col_name = f"{b} {m}" 
                if start_idx <= idx <= end_idx:
                    row[col_name] = p.get("Color", "#EAB308") 
                else:
                    row[col_name] = ""
            schedule_data.append(row)
    
    df_schedule = pd.DataFrame(schedule_data)
    if not df_schedule.empty:
        styles_df = pd.DataFrame('', index=df_schedule.index, columns=df_schedule.columns)
        
        for idx, row in df_schedule.iterrows():
            proker_color = row["_Color"]
            
            for col in df_schedule.columns:
                if col in ["_Raw_PK", "_Color"]: continue
                val = row[col]
                
                if col in ["Program Kerja", "Tahapan Kegiatan"]:
                    styles_df.at[idx, col] = f'background-color: {proker_color}20; color: #0F172A; font-weight: 600; border-bottom: 1px solid #eaedf2;'
                elif isinstance(val, str) and val.startswith("#"):
                    styles_df.at[idx, col] = f'background-color: {val}; color: {val}; border-radius: 4px;'
                else:
                    styles_df.at[idx, col] = f'background-color: #ffffff; border-bottom: 1px solid #eaedf2;'
        
        df_schedule = df_schedule.drop(columns=["_Raw_PK", "_Color"])
        styles_df = styles_df.drop(columns=["_Raw_PK", "_Color"])
        
        st.dataframe(df_schedule.style.apply(lambda x: styles_df, axis=None), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data tahapan program kerja.")

# 3. Sistem Login
def login():
    st.sidebar.markdown("### 🔐 Admin Panel")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "kaltim15":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.sidebar.error("Username atau Password salah")

if not st.session_state['logged_in']:
    login()
else:
    st.sidebar.markdown("👋 **Halo, Admin!**")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# 4. Navigasi Halaman
menu = st.radio(" ", ["Beranda", "Daftar Mahasiswa OJT", "Progres Program Kerja", "Dokumentasi Kegiatan"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

# --- HALAMAN BERANDA ---
if menu == "Beranda":
    st.title("📊 Dashboard Progres OJT Korwil Kaltim K15")
    st.markdown("Sistem pemantauan agenda dan program kerja mahasiswa OJT Korwil Kaltim K15.")
    
    total_mhs = len(st.session_state['students'])
    total_proker = len(st.session_state['proker_list'])
    proker_selesai = sum(1 for p in st.session_state['proker_list'] if p["Status"] == "Selesai")
    proker_berjalan = sum(1 for p in st.session_state['proker_list'] if p["Status"] != "Selesai")
    persen_keterlaksanaan = int((proker_selesai / total_proker * 100)) if total_proker > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Mahasiswa</div><div class="metric-value">{total_mhs} Orang</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Proker/Agenda</div><div class="metric-value">{total_proker}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Sedang Berjalan</div><div class="metric-value">{proker_berjalan}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Selesai</div><div class="metric-value">{proker_selesai}</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Keterlaksanaan</div><div class="metric-value">{persen_keterlaksanaan}%</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📈 Grafik Prosentase Progres Program Kerja & Agenda")
    if total_proker > 0:
        chart_df = pd.DataFrame([
            {"Program Kerja": p["Nama Agenda"], "Progres (%)": p["Progres"]} 
            for p in st.session_state['proker_list']
        ]).set_index("Program Kerja")
        st.bar_chart(chart_df, color="#EAB308", use_container_width=True)
    else:
        st.info("Belum ada data program kerja untuk ditampilkan pada grafik.")

    st.markdown("---")
    render_time_schedule()

# --- HALAMAN DAFTAR MAHASISWA ---
elif menu == "Daftar Mahasiswa OJT":
    st.title("👥 Daftar Mahasiswa OJT")
    
    if st.session_state['logged_in']:
        with st.expander("✏️ Edit Data & Progres Mahasiswa (Mode Admin)", expanded=False):
            pilih_mhs = st.selectbox("Pilih Mahasiswa:", [m["Nama"] for m in st.session_state['students']])
            idx = next(i for i, m in enumerate(st.session_state['students']) if m["Nama"] == pilih_mhs)
            mhs_data = st.session_state['students'][idx]
            
            with st.form("form_mhs"):
                new_nama = st.text_input("Nama Lengkap", mhs_data["Nama"])
                new_domisili = st.text_input("Asal Domisili", mhs_data["Asal Domisili"])
                new_prodi = st.text_input("Program Studi", mhs_data["Program Studi"])
                new_perusahaan = st.text_input("Perusahaan", mhs_data["Perusahaan"])
                
                st.markdown("---")
                st.markdown("**Perbarui Progres Akademik Mahasiswa (Praktis via Tabel)**")
                
                # Revisi 2: Input menggunakan st.data_editor agar lebih rapi, terstruktur, dan praktis
                st.markdown("📅 **Logbook (Minggu & Status)**")
                df_logbook_edit = st.data_editor(
                    pd.DataFrame(mhs_data.get("Logbook", [])),
                    column_config={"Status": st.column_config.SelectboxColumn("Status", options=["Selesai", "Belum"])},
                    num_rows="dynamic", use_container_width=True, key=f"log_{idx}"
                )
                
                st.markdown("📑 **Laporan Akhir OJT (Bab/Progres)**")
                df_laporan_edit = st.data_editor(
                    pd.DataFrame(mhs_data.get("Laporan", [])),
                    num_rows="dynamic", use_container_width=True, key=f"lap_{idx}"
                )
                
                new_tugas_akhir = st.text_area("📌 Topik Tugas Akhir", mhs_data.get("TugasAkhir", ""))
                foto_file = st.file_uploader("Pilih file foto profil (Maks 2MB)", type=['jpg', 'jpeg', 'png'])
                
                if st.form_submit_button("Simpan Perubahan"):
                    clean_logbook = [l for l in df_logbook_edit.to_dict('records') if str(l.get("Minggu", "")).strip() != ""]
                    clean_laporan = [lp for lp in df_laporan_edit.to_dict('records') if str(lp.get("Bab/Progres", "")).strip() != ""]
                    
                    st.session_state['students'][idx].update({
                        "Nama": new_nama, "Asal Domisili": new_domisili,
                        "Program Studi": new_prodi, "Perusahaan": new_perusahaan,
                        "Logbook": clean_logbook, "Laporan": clean_laporan, "TugasAkhir": new_tugas_akhir
                    })
                    if foto_file and foto_file.size <= 2 * 1024 * 1024:
                        encoded = base64.b64encode(foto_file.read()).decode()
                        st.session_state['students'][idx]["Foto"] = f"data:{foto_file.type};base64,{encoded}"
                    st.success("Data berhasil diperbarui!")
                    st.rerun()

    # Tampilan Grid Profil Mahasiswa dengan Tampilan Progres yang Disederhanakan & Rapi
    cols = st.columns(3)
    for i, mhs in enumerate(st.session_state['students']):
        with cols[i % 3]: 
            st.markdown(f"""
                <div class="mhs-card">
                    <img src="{mhs['Foto']}" style="width: 100%; border-radius: 8px; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 18px; color: #0F172A;">{mhs['Nama']}</h3>
                    <p style="margin: 5px 0; font-size: 13px; color: #475569;"><b>🏢 Perusahaan:</b> {mhs['Perusahaan']}</p>
                    <p style="margin: 5px 0; font-size: 13px; color: #475569;"><b>🎓 Prodi:</b> {mhs['Program Studi']}</p>
                    <p style="margin: 5px 0 15px 0; font-size: 13px; color: #475569;"><b>📍 Domisili:</b> {mhs['Asal Domisili']}</p>
                    <hr style="margin: 10px 0; border: 0; border-top: 1px solid #E2E8F0;">
            """, unsafe_allow_html=True)
            
            # Revisi 1: Tampilan logbook disederhanakan menggunakan badge/ikon bersih
            st.markdown('<div class="progress-section-title">1. Logbook</div>', unsafe_allow_html=True)
            logbook_items = mhs.get('Logbook', [])
            if logbook_items:
                log_text = ""
                for l in logbook_items:
                    minggu = l.get("Minggu", "")
                    status = l.get("Status", "Belum")
                    icon = "✅" if status == "Selesai" else "⭕"
                    log_text += f"• {minggu}: {icon} {status}<br>"
                st.markdown(f"<div style='font-size: 13px; color: #334155;'>{log_text}</div>", unsafe_allow_html=True)
            else:
                st.caption("Belum ada data logbook.")
            
            # Revisi 1: Tampilan laporan akhir OJT disederhanakan
            st.markdown('<div class="progress-section-title">2. Laporan Akhir OJT</div>', unsafe_allow_html=True)
            laporan_items = mhs.get('Laporan', [])
            if laporan_items:
                lap_text = ""
                for lp in laporan_items:
                    lap_text += f"• {lp.get('Bab/Progres', '')}<br>"
                st.markdown(f"<div style='font-size: 13px; color: #334155;'>{lap_text}</div>", unsafe_allow_html=True)
            else:
                st.caption("Belum ada data laporan.")
            
            # Revisi 1: Tampilan topik tugas akhir disederhanakan
            st.markdown('<div class="progress-section-title">3. Tugas Akhir</div>', unsafe_allow_html=True)
            tugas_akhir_text = mhs.get('TugasAkhir', '-')
            st.markdown(f"<div style='font-size: 13px; color: #334155; white-space: pre-wrap;'>{tugas_akhir_text}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# --- HALAMAN PROGRAM KERJA ---
elif menu == "Progres Program Kerja":
    st.title("📑 Progres & Detail Program Kerja")
    
    render_time_schedule()
    st.markdown("---")

    if st.session_state['logged_in']:
        with st.expander("🛠️ Tambah / Edit / Hapus Data Proker (Admin)", expanded=False):
            opsi_proker = ["-- Tambah Proker Baru --"] + [p["Nama Agenda"] for p in st.session_state['proker_list']]
            pilihan = st.selectbox("Pilih Aksi:", opsi_proker)
            
            is_new = pilihan == "-- Tambah Proker Baru --"
            data_aktif = {
                "Divisi": [{"Nama Divisi": "", "Jobdesk": ""}],
                "Tautan": [{"Keterangan": "", "URL": ""}],
                "Tahapan": [{"Tahapan Kegiatan": "", "B_Mulai": "Agustus", "M_Mulai": "W1", "B_Selesai": "Agustus", "M_Selesai": "W1"}]
            } if is_new else next(p for p in st.session_state['proker_list'] if p["Nama Agenda"] == pilihan)
            
            with st.form("form_proker"):
                st.markdown("**1. Data & Status Agenda**")
                colA, colB = st.columns(2)
                nama_agenda = colA.text_input("Nama Agenda", data_aktif.get("Nama Agenda", ""))
                pic = colB.text_input("Penanggung Jawab (PIC)", data_aktif.get("PIC", ""))
                
                status = colA.selectbox("Status", ["Perencanaan", "Berjalan", "Selesai"], 
                                      index=["Perencanaan", "Berjalan", "Selesai"].index(data_aktif.get("Status", "Perencanaan")))
                prog = colB.slider("Progres (%)", 0, 100, 100 if status == "Selesai" else data_aktif.get("Progres", 0), disabled=(status == "Selesai"))
                
                st.markdown("**2. Waktu Pelaksanaan & Persiapan**")
                colW1, colW2 = st.columns(2)
                waktu_pelaksanaan = colW1.text_input("Waktu Pelaksanaan Acara", data_aktif.get("Waktu Pelaksanaan", ""))
                rentang_persiapan = colW2.text_input("Rentang Waktu Persiapan Acara", data_aktif.get("Rentang Waktu Persiapan", ""))
                warna_chart = colW1.color_picker("Pilih Warna Label Timeline", data_aktif.get("Color", "#3498DB"))
                
                st.markdown("**3. Tahapan Kegiatan (Untuk Time Schedule)**")
                df_tahapan = st.data_editor(
                    pd.DataFrame(data_aktif.get("Tahapan", [])), 
                    column_config={
                        "B_Mulai": st.column_config.SelectboxColumn("Bulan Mulai", options=BULAN),
                        "M_Mulai": st.column_config.SelectboxColumn("Minggu Mulai", options=MINGGU),
                        "B_Selesai": st.column_config.SelectboxColumn("Bulan Selesai", options=BULAN),
                        "M_Selesai": st.column_config.SelectboxColumn("Minggu Selesai", options=MINGGU)
                    },
                    num_rows="dynamic", use_container_width=True
                )

                st.markdown("**4. Struktur Inti & Divisi**")
                colD1, colD2, colD3 = st.columns(3)
                ketua = colD1.text_input("Ketua Pelaksana", data_aktif.get("Ketua", ""))
                sekretaris = colD2.text_input("Sekretaris", data_aktif.get("Sekretaris", ""))
                bendahara = colD3.text_input("Bendahara", data_aktif.get("Bendahara", ""))
                
                df_divisi = st.data_editor(pd.DataFrame(data_aktif.get("Divisi", [])), num_rows="dynamic", use_container_width=True)
                
                st.markdown("**5. Tautan Arsip & Evaluasi**")
                df_tautan = st.data_editor(pd.DataFrame(data_aktif.get("Tautan", [])), num_rows="dynamic", use_container_width=True)
                evaluasi = st.text_area("Catatan Evaluasi", data_aktif.get("Evaluasi", "-"))
                
                st.markdown("---")
                hapus_proker = False
                if not is_new:
                    hapus_proker = st.checkbox("⚠️ Centang kotak ini jika Anda ingin MENGHAPUS Program Kerja ini sepenuhnya.")
                
                col_btn1, col_btn2 = st.columns(2)
                submit = col_btn1.form_submit_button("💾 Simpan / Perbarui Data Proker")
                duplikasi = col_btn2.form_submit_button("📑 Duplikasi Rincian Progres Ini") if not is_new else False
                
                if submit:
                    if hapus_proker:
                        st.session_state['proker_list'] = [p for p in st.session_state['proker_list'] if p["Nama Agenda"] != pilihan]
                        if pilihan in st.session_state['album_list']:
                            st.session_state['album_list'].remove(pilihan)
                        st.success("Program Kerja berhasil dihapus!")
                    else:
                        clean_divisi = [d for d in df_divisi.to_dict('records') if str(d.get("Nama Divisi", "")).strip() != ""]
                        clean_tautan = [t for t in df_tautan.to_dict('records') if str(t.get("Keterangan", "")).strip() != ""]
                        clean_tahapan = [th for th in df_tahapan.to_dict('records') if str(th.get("Tahapan Kegiatan", "")).strip() != ""]
                        
                        new_data = {
                            "Nama Agenda": nama_agenda, "Status": status, "Progres": prog, "PIC": pic,
                            "Waktu Pelaksanaan": waktu_pelaksanaan, "Rentang Waktu Persiapan": rentang_persiapan,
                            "Ketua": ketua, "Sekretaris": sekretaris, "Bendahara": bendahara, 
                            "Divisi": clean_divisi, "Tautan": clean_tautan, "Tahapan": clean_tahapan, 
                            "Evaluasi": evaluasi, "Color": warna_chart
                        }
                        if is_new:
                            new_data["id"] = len(st.session_state['proker_list']) + 1
                            st.session_state['proker_list'].append(new_data)
                            if nama_agenda not in st.session_state['album_list']:
                                st.session_state['album_list'].append(nama_agenda)
                                st.session_state['album_data'][nama_agenda] = []
                        else:
                            idx_proker = next(i for i, p in enumerate(st.session_state['proker_list']) if p["Nama Agenda"] == pilihan)
                            old_name = data_aktif["Nama Agenda"]
                            new_data["id"] = data_aktif["id"]
                            st.session_state['proker_list'][idx_proker] = new_data
                            
                            if old_name != nama_agenda and old_name in st.session_state['album_list']:
                                idx_alb = st.session_state['album_list'].index(old_name)
                                st.session_state['album_list'][idx_alb] = nama_agenda
                                st.session_state['album_data'][nama_agenda] = st.session_state['album_data'].pop(old_name, [])
                                
                        st.success("Data berhasil disimpan!")
                    st.rerun()

                if duplikasi:
                    proker_copy = copy.deepcopy(data_aktif)
                    proker_copy["Nama Agenda"] = f"{proker_copy['Nama Agenda']} (Copy)"
                    proker_copy["id"] = len(st.session_state['proker_list']) + 1
                    st.session_state['proker_list'].append(proker_copy)
                    
                    new_album_name = proker_copy["Nama Agenda"]
                    if new_album_name not in st.session_state['album_list']:
                        st.session_state['album_list'].append(new_album_name)
                        st.session_state['album_data'][new_album_name] = []
                        
                    st.success("Rincian Progres berhasil diduplikasi!")
                    st.rerun()

    st.markdown("### Rincian Progres")
    if len(st.session_state['proker_list']) == 0:
        st.info("Belum ada data program kerja. Silakan tambah melalui menu Admin.")
        
    for row in st.session_state['proker_list']:
        with st.expander(f"📁 {row['Nama Agenda']} - ({row['Progres']}%)"):
            st.progress(row['Progres'])
            
            t1, t2, t3 = st.tabs(["Detail Utama", "Struktur & Jobdesk", "Arsip & Evaluasi"])
            with t1:
                st.markdown(f"**PIC:** {row.get('PIC', '-')}")
                st.markdown(f"**Status:** {row.get('Status', '-')}")
                st.markdown(f"**Waktu Pelaksanaan:** {row.get('Waktu Pelaksanaan', '-')}")
                st.markdown(f"**Rentang Waktu Persiapan Acara:** {row.get('Rentang Waktu Persiapan', '-')}")
            
            with t2:
                st.markdown(f"**Ketua Pelaksana:** {row.get('Ketua', '-')} | **Sekretaris:** {row.get('Sekretaris', '-')} | **Bendahara:** {row.get('Bendahara', '-')}")
                st.markdown("**📋 Daftar Divisi:**")
                if row.get("Divisi"):
                    for div in row["Divisi"]:
                        st.markdown(f"- **{div.get('Nama Divisi', '')}:** {div.get('Jobdesk', '')}")
                else:
                    st.caption("Belum ada data divisi.")
                    
            with t3:
                st.markdown("**🔗 Tautan Arsip:**")
                if row.get("Tautan"):
                    for link in row["Tautan"]:
                        st.markdown(f"- [{link.get('Keterangan', 'Tautan')}]({link.get('URL', '#')})")
                else:
                    st.caption("Belum ada tautan.")
                st.info(f"**Evaluasi:** {row.get('Evaluasi', '-')}")

# --- HALAMAN DOKUMENTASI ---
elif menu == "Dokumentasi Kegiatan":
    st.title("📸 Dokumentasi Kegiatan")
    
    if st.session_state['logged_in']:
        st.info("💡 Mode Admin: Album foto dokumentasi di bawah ini terhubung secara otomatis dengan daftar Nama Proker/Agenda yang Anda buat.")
    
    current_proker_names = [p["Nama Agenda"] for p in st.session_state['proker_list']]
    for p_name in current_proker_names:
        if p_name not in st.session_state['album_list']:
            st.session_state['album_list'].append(p_name)
        if p_name not in st.session_state['album_data']:
            st.session_state['album_data'][p_name] = []
            
    if st.session_state['album_list']:
        kegiatan = st.selectbox("Pilih Nama Proker Agenda (Album):", st.session_state['album_list'])
        
        if st.session_state['logged_in']:
            uploaded_files = st.file_uploader(f"Unggah Foto Dokumentasi untuk '{kegiatan}'", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
            if uploaded_files and st.button("💾 Simpan Foto ke Album"):
                for f in uploaded_files:
                    encoded = base64.b64encode(f.read()).decode()
                    if kegiatan not in st.session_state['album_data']:
                        st.session_state['album_data'][kegiatan] = []
                    st.session_state['album_data'][kegiatan].append(f"data:{f.type};base64,{encoded}")
                st.success(f"{len(uploaded_files)} foto berhasil diunggah!")
                st.rerun()

        photos = st.session_state['album_data'].get(kegiatan, [])
        if photos:
            st.markdown("""
                <style>
                .collage-img {
                    border: 5px solid #1E3A8A; 
                    border-radius: 12px; 
                    margin-bottom: 20px;
                    box-shadow: 4px 4px 12px rgba(0,0,0,0.2);
                    object-fit: cover;
                }
                </style>
                """, unsafe_allow_html=True)
            
            cols = st.columns(3)
            for i, photo in enumerate(photos):
                with cols[i % 3]:
                    st.markdown(f'<img src="{photo}" class="collage-img" style="width: 100%; height: auto;">', unsafe_allow_html=True)
        else:
            st.info(f"Belum ada foto dokumentasi di dalam album '{kegiatan}'. (Mode Admin: Silakan unggah foto di atas)")
            st.image("https://images.unsplash.com/photo-1542744173-8e7e53415bb0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", caption=f"Placeholder: {kegiatan}", use_container_width=True)