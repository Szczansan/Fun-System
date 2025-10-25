import streamlit as st
import pandas as pd
import psycopg2
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from Master_Logistic import PART_NAME_LIST, PO_NO_LIST, LIST_TUJUAN


def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        port=st.secrets["postgres"]["port"]
    )


def show_page():
    # Koneksi ke database Supabase
    conn = get_connection()
    c = conn.cursor()

    # Buat tabel kalau belum ada
    c.execute("""
    CREATE TABLE IF NOT EXISTS barang_masuk (
        ID SERIAL PRIMARY KEY,
        TANGGAL TEXT,
        SUPPLIER TEXT,
        BARANG TEXT,
        JUMLAH INTEGER
    )
    """)

    # Buat tabel barang_keluar dengan struktur baru (SUDAH INCLUDE NO_PO dan NO_DO)
    c.execute("""
    CREATE TABLE IF NOT EXISTS barang_keluar (
        NO SERIAL PRIMARY KEY,
        TANGGAL TEXT,
        TUJUAN TEXT,
        PART_NO TEXT,
        PART_NAME TEXT,
        UNIT TEXT,
        PLASTIK TEXT,
        BOX TEXT,
        REMARKS TEXT,
        JUMLAH INTEGER,
        NO_PO TEXT DEFAULT '',
        NO_DO TEXT DEFAULT '',
        CREATED_AT TEXT
    )
    """)

    # HAPUS bagian ALTER TABLE karena kolom sudah ada di CREATE TABLE
    # JADI TIDAK PERLU LAGI ALTER TABLE

    conn.commit()

    # Judul halaman
    st.markdown(
        """
        <h2 style='text-align: center; color: #117A65;'>
            Logistic
        </h2>
        """,
        unsafe_allow_html=True
    )

    # Pilihan menu di sidebar
    menu = st.sidebar.radio("Pilih Menu:", ["📦 Barang Masuk", "🚚 Barang Keluar", "📊 Rekap Harian"])

    # =====================================================================
    # 📦 Barang Masuk
    # =====================================================================
    if menu == "📦 Barang Masuk":
        st.subheader("Input Barang Masuk")

        supplier = st.text_input("Nama Supplier")
        item = st.text_input("Nama Barang")
        qty = st.number_input("Jumlah", min_value=1, step=1)
        tanggal = st.date_input("Tanggal Masuk")

        if st.button("Simpan"):
            if supplier and item:
                # GANTI ? MENJADI %s UNTUK POSTGRESQL
                c.execute("INSERT INTO barang_masuk (TANGGAL, SUPPLIER, BARANG, JUMLAH) VALUES (%s, %s, %s, %s)",
                          (str(tanggal), supplier, item, qty))
                conn.commit()
                st.success(f"Data {item} dari {supplier} sebanyak {qty} pcs berhasil disimpan!")
            else:
                st.warning("Harap isi semua kolom sebelum menyimpan.")

    # =====================================================================
    # 🚚 Barang Keluar
    # =====================================================================
    elif menu == "🚚 Barang Keluar":
        st.subheader("Input Barang Keluar")

        tujuan = st.selectbox("Tujuan Pengiriman", ["- Pilih Tujuan Kirim -"] + LIST_TUJUAN)
        tanggal = st.date_input("Tanggal Keluar")

        no_po = st.selectbox("Nomor PO", ["-Pilih Nomor PO-"] + PO_NO_LIST)
        no_do = st.text_input("DO NO")

        st.write("Masukkan Delivery Order Keluar :")

        # Simpan semua item di list
        data_items = []
        for i in range(8):
            st.markdown(f"**Barang ke-{i + 1}**")

            # Kolom layout
            col1, col2, col3, col4, col5, col6 = st.columns([3.5, 6, 1.5, 1.5, 1.5, 2])

            with col2:
                part_name = st.selectbox(
                    f"Nama Barang ke-{i + 1}",
                    ["- Pilih Barang -"] + list(PART_NAME_LIST.keys()),
                    key=f"part_name_{i}"
                )

            with col1:
                if part_name != "- Pilih Barang -":
                    part_no = PART_NAME_LIST.get(part_name, "")
                    st.info(f"📦 Part Number: **{part_no}**")
                else:
                    part_no = ""

            with col3:
                unit = st.text_input("Unit", key=f"unit_{i}", placeholder="PCS")

            with col4:
                plastik = st.text_input("Plastik", key=f"plastik_{i}", placeholder="-")

            with col5:
                box = st.text_input("Box", key=f"box_{i}", placeholder="-")

            with col6:
                remarks = st.text_input("Remarks", key=f"remarks_{i}", placeholder="-")

            st.markdown("---")

            # Simpan hanya kalau ada isinya
            if part_no and part_name != "- Pilih Barang -" and unit:
                data_items.append({
                    'part_no': part_no,
                    'part_name': part_name,
                    'unit': unit,
                    'plastik': plastik,
                    'box': box,
                    'remarks': remarks
                })

        # Tombol kirim
        if st.button("Kirim"):
            if tujuan and len(data_items) > 0:
                # Simpan ke database - GANTI ? MENJADI %s
                for item_data in data_items:
                    c.execute("""
                        INSERT INTO barang_keluar 
                        (TANGGAL, TUJUAN, PART_NO, PART_NAME, UNIT, PLASTIK, BOX, REMARKS, JUMLAH, NO_PO, NO_DO) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        str(tanggal),
                        tujuan,
                        item_data['part_no'],
                        item_data['part_name'],
                        item_data['unit'],
                        item_data['plastik'],
                        item_data['box'],
                        item_data['remarks'],
                        1,  # default jumlah
                        no_po,
                        no_do
                    ))
                conn.commit()

                # Buat PDF
                buffer = io.BytesIO()
                pdf = canvas.Canvas(buffer, pagesize=A4)
                pdf.setTitle("DELIVERY ORDER")

                # Header
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(20, 820, "PT SHIN SAM-PLUS INDUSTRY")
                pdf.drawString(20, 805, "JL.PERMATA RAYA LOT E1 - KIIC")
                pdf.drawString(20, 790, "KARAWANG (0267) 8637292")

                # Info pengiriman
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(375, 820, "KEPADA YTH")
                pdf.drawString(375, 805, f"{tujuan}")
                pdf.drawString(375, 770, f"PO NO  : {no_po}")
                pdf.drawString(375, 755, f"DO NO : {no_do}")
                pdf.drawString(375, 740, f"DATE : {tanggal}")

                # Header tabel
                y = 710
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(25, y, "PART NO")
                pdf.drawString(173, y, "PART NAME")
                pdf.drawString(320, y, "UNIT")
                pdf.drawString(358, y, "PLASTIK")
                pdf.drawString(420, y, "BOX")
                pdf.drawString(480, y, "REMARKS")
                y -= 5
                pdf.line(1, y, 820, y)
                y -= 14

                pdf.line(1, 723, 820, 723)

                # ===============================================================
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(10, 520, "DRIVER         :")
                pdf.drawString(10, 505, "NO. POLISI     :")
                pdf.setFont("Helvetica", 10)
                pdf.drawString(20, 480, "PREPARED")
                pdf.drawString(100, 480, "CHECKED")
                pdf.drawString(175, 480, "APPROVED")
                pdf.drawString(255, 480, "SECURITY")
                pdf.drawString(340, 480, "RECIVED BY")
                # ===============================================================
                # Data isi
                pdf.setFont("Helvetica", 11)
                for item_data in data_items:
                    part_name = item_data['part_name'][:45] + "..." if len(item_data['part_name']) > 45 else item_data[
                        'part_name']
                    remarks = item_data['remarks'][:15] + "..." if len(item_data['remarks']) > 15 else item_data[
                        'remarks']

                    pdf.drawCentredString(55, y, item_data['part_no'])
                    pdf.drawCentredString(210, y, part_name)
                    pdf.drawCentredString(336, y, item_data['unit'])
                    pdf.drawCentredString(385, y, item_data['plastik'])
                    pdf.drawCentredString(434, y, item_data['box'])
                    pdf.drawCentredString(514, y, remarks)
                    y -= 20

                    if y < 50:
                        pdf.showPage()
                        y = 800
                        pdf.setFont("Helvetica", 8)

                pdf.save()
                buffer.seek(0)

                # Tombol download
                st.success(f"{len(data_items)} item berhasil dikirim ke {tujuan}!")
                st.download_button(
                    label="📄 Download Surat Jalan",
                    data=buffer,
                    file_name=f"Surat_Jalan_{tanggal}_{tujuan}.pdf",
                    mime="application/pdf"
                )

            else:
                st.warning("Isi minimal 1 barang (Part Name, Unit) dan tujuan pengiriman.")

    # =====================================================================
    # 📊 Rekap Harian
    # =====================================================================
    elif menu == "📊 Rekap Harian":
        st.subheader("Rekap Barang Harian")

        tab1, tab2 = st.tabs(["📥 Barang Masuk", "📤 Barang Keluar"])

        with tab1:
            df_masuk = pd.read_sql_query("SELECT * FROM barang_masuk", conn)
            if not df_masuk.empty:
                st.dataframe(df_masuk)
            else:
                st.info("Belum ada data barang masuk.")

        with tab2:
            df_keluar = pd.read_sql_query("""
                SELECT
                    TANGGAL,
                    NO_PO as "NO PO",
                    NO_DO as "NO DO",
                    PART_NAME,
                    PART_NO,
                    TUJUAN
                FROM barang_keluar            
            """, conn)
            if not df_keluar.empty:
                st.dataframe(df_keluar)
            else:
                st.info("Belum ada data barang keluar.")

    # Tutup koneksi di akhir
    conn.close()


# Jangan lupa panggil function show_page()
show_page()