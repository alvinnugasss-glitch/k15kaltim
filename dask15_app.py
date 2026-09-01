import streamlit as st
import pandas as pd
import base64
import copy
from datetime import date
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman & Tema Warna
st.set_page_config(page_title="Dashboard OJT Kaltim K15", layout="wide", page_icon="⚓")

st.markdown("""
    <style>
    .stApp { background-color: var(--background-color); }
    h1, h2, h3 { color: var(--text-color); }
    .metric-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-left: 5px solid #1E3A8A;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-title {
        font-size: 14px;
        color: var(--text-color);
        opacity: 0.8;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        color: var(--text-color);
        font-weight: 700;
    }
    .mhs-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: var(--text-color);
    }
    .progress-section-title {
        font-weight: 700;
        color: #3b82f6;
        margin-top: 10px;
        margin-bottom: 5px;
        font-size: 14px;
        border-bottom: 1px solid rgba(128,128,128,0.2);
        padding-bottom: 3px;
    }
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: center;
        background-color: var(--secondary-background-color);
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Koneksi & Inisialisasi Data
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_students_db = conn.read(worksheet="Mahasiswa", ttl=0)
    if df_students_db.empty: raise Exception()
except:
    default_mhs = [
        {
            "id": 1, "Nama": "Raden Mas Alvin Sastrowardhana", "Asal Domisili": "Samarinda", 
            "Program Studi": "Teknik Perancangan dan Konstruksi Kapal", "Perusahaan": "PT Dumas Surabaya", 
            "Foto": "https://ui-avatars.com/api/?name=Alvin&background=EAB308&color=fff&size=200",
            "Logbook": "• Week 1: ✅ Selesai\n• Week 2: ✅ Selesai",
            "Laporan": "• Selesai Bab 1\n• On Progress Bab 2",
            "TugasAkhir": "Penelitian stabilitas dan olah gerak hopper barge.\n\nNote: Mulai OJT lebih awal pada 28 Juli 2026."
        }
    ]
    for i in range(2, 12):
        default_mhs.append({
            "id": i, "Nama": f"Mahasiswa {i}", "Asal Domisili": "-", 
            "Program Studi": "-", "Perusahaan": "-", 
            "Foto": f"https://ui-avatars.com/api/?name=M+{i}&background=EAB308&color=fff&size=200",
            "Logbook": "• Belum diisi", "Laporan": "• Belum diisi", "TugasAkhir": "Belum ditentukan"
        })
    df_students_db = pd.DataFrame(default_mhs)

if 'students' not in st.session_state:
    st.session_state['students'] = df_students_db.to_dict('records')

if 'proker_list' not in st.session_state:
    st.session_state['proker_list'] = [
        {
            "id": 1, "Nama Agenda": "Penerimaan OJT", "Status": "Selesai", "Progres": 100, "PIC": "Divisi Internal",
            "Waktu Pelaksanaan": ["2026-08-28", "2026-08-29", "2026-08-30"], "Rentang Waktu Persiapan": "Agustus (Minggu ke-1 s.d ke-3)",
            "Ketua": "Billy", "Sekretaris": "Bila", "Bendahara": "Faisal",
            "Divisi": [{"Nama Divisi": "Perlengkapan", "PIC Divisi": "Joko", "Anggota Panitia": "Doni, Budi", "Jobdesk": "Mempersiapkan lokasi dan alat"}],
            "Tautan": [{"Keterangan": "Proposal", "URL": "https://drive.google.com/..."}],
            "Tahapan": [{"Tahapan Kegiatan": "Pembentukan panitia", "B_Mulai": "Agustus", "M_Mulai": "W1", "B_Selesai": "Agustus", "M_Selesai": "W1"}],
            "Evaluasi": "Lancar", "Color": "#E74C3C"
        }
    ]

if 'album_list' not in st.session_state:
    st.session_state['album_list'] = [p["Nama Agenda"] for p in st.session_state['proker_list']]

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

BULAN = ["Agustus", "September", "Oktober", "November", "Desember"]
MINGGU = ["W1", "W2", "W3", "W4"]
TUPLES = [(b, m) for b in BULAN for m in MINGGU]
WAKTU_LIST = [f"{b} (Minggu ke-{w})" for b in BULAN for w in range(1, 5)]

def get_week_index(bulan, minggu):
    return BULAN.index(bulan) * 4 + MINGGU.index(minggu)

def render_time_schedule():
    st.subheader("📅 Time Schedule Program Kerja & Agenda")
    st.caption("Periode Agustus – Desember")
    
    schedule_data = []
    for p in st.session_state['proker_list']:
        if not p.get("Tahapan"): continue
        for i, t in enumerate(p["Tahapan"]):
            if not t.get("Tahapan Kegiatan") or str(t.get("Tahapan Kegiatan")).strip() == "": continue
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
                    styles_df.at[idx, col] = f'background-color: {proker_color}20; font-weight: 600; border-bottom: 1px solid rgba(128,128,128,0.2);'
                elif isinstance(val, str) and val.startswith("#"):
                    styles_df.at[idx, col] = f'background-color: {val}; color: {val}; border-radius: 4px;'
                else:
                    styles_df.at[idx, col] = f'border-bottom: 1px solid rgba(128,128,128,0.2);'
        
        df_schedule = df_schedule.drop(columns=["_Raw_PK", "_Color"])
        styles_df = styles_df.drop(columns=["_Raw_PK", "_Color"])
        st.dataframe(df_schedule.style.apply(lambda x: styles_df, axis=None), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data tahapan program kerja.")

# 3. Sistem Login Admin
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

# 4. Navigasi Halaman Utama
menu = st.radio(" ", ["Beranda", "Daftar Mahasiswa OJT", "Progres Program Kerja", "Dokumentasi Kegiatan"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

if menu == "Beranda":
    st.title("📊 Dashboard Progres OJT Korwil Kaltim K15")
    st.markdown("Sistem pemantauan agenda dan program kerja mahasiswa OJT Korwil Kaltim K15.")
    
    total_mhs = len(st.session_state['students'])
    total_proker = len(st.session_state['proker_list'])
    proker_selesai = sum(1 for p in st.session_state['proker_list'] if p["Status"] == "Selesai")
    proker_berjalan = sum(1 for p in st.session_state['proker_list'] if p["Status"] != "Selesai")
    persen_keterlaksanaan = int((proker_selesai / total_proker * 100)) if total_proker > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-title">Total Mahasiswa</div><div class="metric-value">{total_mhs} Orang</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-title">Total Proker/Agenda</div><div class="metric-value">{total_proker}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-title">Sedang Berjalan</div><div class="metric-value">{proker_berjalan}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-title">Selesai</div><div class="metric-value">{proker_selesai}</div></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="metric-card"><div class="metric-title">Keterlaksanaan</div><div class="metric-value">{persen_keterlaksanaan}%</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 Grafik Prosentase Progres Program Kerja & Agenda")
    if total_proker > 0:
        chart_df = pd.DataFrame([{"Program Kerja": p["Nama Agenda"], "Progres (%)": p["Progres"]} for p in st.session_state['proker_list']]).set_index("Program Kerja")
        st.bar_chart(chart_df, color="#EAB308", use_container_width=True)
    
    st.markdown("---")
    render_time_schedule()

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
                new_logbook = st.text_area("Logbook", mhs_data.get("Logbook", ""))
                new_laporan = st.text_area("Laporan Akhir OJT", mhs_data.get("Laporan", ""))
                new_tugas_akhir = st.text_area("Topik Tugas Akhir", mhs_data.get("TugasAkhir", ""))
                
                foto_file = st.file_uploader("Pilih file foto profil (Maksimal 2 MB)", type=['jpg', 'jpeg', 'png'])
                
                if st.form_submit_button("Simpan Perubahan"):
                    foto_url = mhs_data["Foto"]
                    if foto_file:
                        if foto_file.size > 2 * 1024 * 1024:
                            st.error("Gagal: Ukuran file foto melebihi batas maksimal 2 MB!")
                        else:
                            encoded = base64.b64encode(foto_file.read()).decode()
                            foto_url = f"data:{foto_file.type};base64,{encoded}"
                    
                    st.session_state['students'][idx].update({
                        "Nama": new_nama, "Asal Domisili": new_domisili,
                        "Program Studi": new_prodi, "Perusahaan": new_perusahaan,
                        "Logbook": new_logbook, "Laporan": new_laporan, "TugasAkhir": new_tugas_akhir,
                        "Foto": foto_url
                    })
                    st.success("Data mahasiswa berhasil diperbarui!")
                    st.rerun()

    cols = st.columns(3)
    for i, mhs in enumerate(st.session_state['students']):
        with cols[i % 3]: 
            st.markdown(f"""
                <div class="mhs-card">
                    <img src="{mhs['Foto']}" style="width: 100%; border-radius: 8px; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 18px;">{mhs['Nama']}</h3>
                    <p style="margin: 5px 0; font-size: 13px;"><b>🏢 Perusahaan:</b> {mhs['Perusahaan']}</p>
                    <p style="margin: 5px 0; font-size: 13px;"><b>🎓 Prodi:</b> {mhs['Program Studi']}</p>
                    <p style="margin: 5px 0 15px 0; font-size: 13px;"><b>📍 Domisili:</b> {mhs['Asal Domisili']}</p>
                    <hr style="margin: 10px 0; border: 0; border-top: 1px solid rgba(128,128,128,0.2);">
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="progress-section-title">1. Logbook</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 13px; white-space: pre-wrap;'>{mhs.get('Logbook', '-')}</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="progress-section-title">2. Laporan Akhir OJT</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 13px; white-space: pre-wrap;'>{mhs.get('Laporan', '-')}</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="progress-section-title">3. Tugas Akhir</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 13px; white-space: pre-wrap;'>{mhs.get('TugasAkhir', '-')}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

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
                "Divisi": [{"Nama Divisi": "", "PIC Divisi": "", "Anggota Panitia": "", "Jobdesk": ""}],
                "Tautan": [{"Keterangan": "", "URL": ""}],
                "Tahapan": [{"Tahapan Kegiatan": "", "B_Mulai": "Agustus", "M_Mulai": "W1", "B_Selesai": "Agustus", "M_Selesai": "W1"}],
                "Waktu Pelaksanaan": [date.today()]
            } if is_new else next(p for p in st.session_state['proker_list'] if p["Nama Agenda"] == pilihan)
            
            with st.form("form_proker"):
                st.markdown("**1. Data & Status Agenda**")
                colA, colB = st.columns(2)
                nama_agenda = colA.text_input("Nama Agenda", data_aktif.get("Nama Agenda", ""))
                pic = colB.text_input("Penanggung Jawab (PIC)", data_aktif.get("PIC", ""))
                
                status_options = ["Persiapan", "Berjalan", "Selesai"]
                default_status_idx = status_options.index(data_aktif.get("Status", "Persiapan")) if data_aktif.get("Status") in status_options else 0
                status = colA.selectbox("Status", status_options, index=default_status_idx)
                
                if status == "Persiapan":
                    prog = 25
                elif status == "Berjalan":
                    prog = 75
                else:
                    prog = 100
                
                colB.metric("Otomatis Progres (%)", f"{prog}%")
                
                st.markdown("**2. Waktu Pelaksanaan (Bisa Pilih Banyak Tanggal Berulang)**")
                existing_dates = data_aktif.get("Waktu Pelaksanaan", [date.today()])
                if not isinstance(existing_dates, list):
                    existing_dates = [date.today()]
                
                # Menggunakan st.data_editor untuk input tanggal berulang secara praktis
                df_dates_input = pd.DataFrame({"Tanggal Pelaksanaan": existing_dates})
                df_dates_edited = st.data_editor(
                    df_dates_input,
                    column_config={"Tanggal Pelaksanaan": st.column_config.DateColumn("Tanggal Pelaksanaan", format="YYYY-MM-DD", required=True)},
                    num_rows="dynamic", use_container_width=True, key=f"dates_edit_{pilihan}"
                )

                colW1, colW2 = st.columns(2)
                default_persiapan = data_aktif.get("Rentang Waktu Persiapan", WAKTU_LIST[0])
                idx_persiapan = WAKTU_LIST.index(default_persiapan) if default_persiapan in WAKTU_LIST else 0
                rentang_persiapan = colW1.selectbox("Rentang Waktu Persiapan Acara", WAKTU_LIST, index=idx_persiapan)
                warna_chart = colW2.color_picker("Pilih Warna Label Timeline", data_aktif.get("Color", "#3498DB"))
                
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
                ketua = colD1.text_input("Ketua Pelaksana", data_aktif.get("Ketua", "Billy"))
                sekretaris = colD2.text_input("Sekretaris", data_aktif.get("Sekretaris", "Bila"))
                bendahara = colD3.text_input("Bendahara", data_aktif.get("Bendahara", "Faisal"))
                
                st.markdown("Daftar Divisi, PIC, Anggota Panitia, dan Jobdesk:")
                df_divisi = st.data_editor(
                    pd.DataFrame(data_aktif.get("Divisi", [])), 
                    num_rows="dynamic", use_container_width=True,
                    column_config={
                        "Nama Divisi": st.column_config.TextColumn("Nama Divisi"),
                        "PIC Divisi": st.column_config.TextColumn("Nama PIC Divisi"),
                        "Anggota Panitia": st.column_config.TextColumn("Daftar Anggota Panitia"),
                        "Jobdesk": st.column_config.TextColumn("Jobdesk")
                    }
                )
                
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
                        
                        # Mengambil list tanggal yang diinput secara dinamis
                        raw_dates = df_dates_edited["Tanggal Pelaksanaan"].dropna().tolist()
                        clean_dates = [str(d) for d in raw_dates if str(d).strip() != ""]
                        
                        new_data = {
                            "Nama Agenda": nama_agenda, "Status": status, "Progres": prog, "PIC": pic,
                            "Waktu Pelaksanaan": clean_dates if clean_dates else [str(date.today())], 
                            "Rentang Waktu Persiapan": rentang_persiapan,
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
                # Menampilkan daftar tanggal pelaksanaan (bisa lebih dari satu/berulang tanpa tanggal selesai)
                waktu_pelaksanaan_val = row.get('Waktu Pelaksanaan', '-')
                if isinstance(waktu_pelaksanaan_val, list):
                    waktu_str = ", ".join([str(d) for d in waktu_pelaksanaan_val])
                else:
                    waktu_str = str(waktu_pelaksanaan_val)

                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); padding: 15px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);'>
                    <p style='margin: 5px 0;'><b>📌 Penanggung Jawab (PIC):</b> {row.get('PIC', '-')}</p>
                    <p style='margin: 5px 0;'><b>⚡ Status:</b> {row.get('Status', '-')}</p>
                    <p style='margin: 5px 0;'><b>📅 Tanggal Pelaksanaan (Berulang):</b> {waktu_str}</p>
                    <p style='margin: 5px 0;'><b>⏳ Rentang Waktu Persiapan:</b> {row.get('Rentang Waktu Persiapan', '-')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with t2:
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); padding: 15px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); margin-bottom: 15px;'>
                    <h4 style='margin-top: 0; color: #3b82f6;'>👔 Badan Pengurus Inti</h4>
                    <p style='margin: 4px 0;'>• <b>Ketua Pelaksana:</b> {row.get('Ketua', '-')}</p>
                    <p style='margin: 4px 0;'>• <b>Sekretaris:</b> {row.get('Sekretaris', '-')}</p>
                    <p style='margin: 4px 0;'>• <b>Bendahara:</b> {row.get('Bendahara', '-')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📋 Pembagian Divisi & Anggota Panitia")
                if row.get("Divisi"):
                    for div in row["Divisi"]:
                        nama_div = div.get('Nama Divisi', '')
                        pic_div = div.get('PIC Divisi', '-')
                        anggota = div.get('Anggota Panitia', '-')
                        job = div.get('Jobdesk', '-')
                        st.markdown(f"""
                        <div style='background-color: var(--secondary-background-color); padding: 12px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-bottom: 8px;'>
                            <b>📌 {nama_div}</b><br>
                            &nbsp;&nbsp;&nbsp;&nbsp;• <b>PIC Divisi:</b> {pic_div}<br>
                            &nbsp;&nbsp;&nbsp;&nbsp;• <b>Anggota:</b> {anggota}<br>
                            &nbsp;&nbsp;&nbsp;&nbsp;• <b>Jobdesk:</b> {job}
                        </div>
                        """, unsafe_allow_html=True)
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

elif menu == "Dokumentasi Kegiatan":
    st.title("📸 Dokumentasi Kegiatan")
    if st.session_state['logged_in']:
        uploaded_files = st.file_uploader("Unggah Foto Dokumentasi (Maks 2 MB per file)", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
        if uploaded_files and st.button("Simpan Foto"):
            for f in uploaded_files:
                if f.size > 2 * 1024 * 1024:
                    st.error(f"File {f.name} gagal diunggah karena ukurannya melebihi 2 MB!")
                else:
                    encoded = base64.b64encode(f.read()).decode()
                    st.success(f"Foto {f.name} berhasil disimpan!")
