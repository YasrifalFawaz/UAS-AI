from flask import Flask, render_template, request, session, redirect, url_for
import json
import joblib
import numpy as np

model = joblib.load("model/decision_tree.pkl")
level_encoder = joblib.load("model/level_encoder.pkl")
label_encoder = joblib.load("model/label_encoder.pkl")

app = Flask(__name__)
app.secret_key = "emotion-adaptive-ai"

# Load materi
with open("data/materi.json", "r", encoding="utf-8") as f:
    MATERI = json.load(f)

# ================== START ==================
@app.route("/")
def index():
    return render_template("index.html")

# ================== (1) MATERI ==================
@app.route("/tingkat_kesulitan", methods=["GET", "POST"])
def tingkat_kesulitan():
    if request.method == "POST":
        level = request.form["level"]
        session["level"] = level
        return redirect("/materi")

    return render_template("tingkat_kesulitan.html")


@app.route("/materi/<tingkat>")
def materi(tingkat):
    with open("data/materi.json", "r", encoding="utf-8") as f:
        data_materi = json.load(f)

    # validasi tingkat kesulitan
    if tingkat not in data_materi:
        return "Tingkat kesulitan tidak valid", 404

    materi_level = data_materi[tingkat]

    return render_template(
        "materi.html",
        tingkat=tingkat,
        materi=materi_level
    )
# ================== (2) SOAL ==================
@app.route("/soal/<tingkat>", methods=["GET", "POST"])
def soal(tingkat):
    with open("data/soal.json", "r", encoding="utf-8") as f:
        data_soal = json.load(f)

    if tingkat not in data_soal:
        return "Tingkat tidak valid", 404

    soal_level = data_soal[tingkat]

    if request.method == "POST":
        jawaban_user = request.form.to_dict()
        waktu = int(jawaban_user.pop("waktu"))

        benar = 0
        total = 0

        # ===== PILIHAN GANDA =====
        for i, soal in enumerate(soal_level["pilihan_ganda"]):
            total += 1
            if jawaban_user.get(f"pg{i}") == str(soal["jawaban"]):
                benar += 1

        # ===== ESSAY =====
        for i, soal in enumerate(soal_level["essay"]):
            total += 1
            if jawaban_user.get(f"essay{i}") == str(soal["jawaban"]):
                benar += 1

        skor = benar / total

        return redirect(
            url_for(
                "feedback",
                skor=skor,
                waktu=waktu,
                level=tingkat
            )
)


    return render_template(
        "soal.html",
        tingkat=tingkat,
        soal=soal_level
    )



# ================== (3) FEEDBACK + AI ==================
@app.route("/feedback", methods=["GET"])
def feedback():
    skor = float(request.args.get("skor"))
    waktu = int(request.args.get("waktu"))
    level = request.args.get("level")

    level_encoded = level_encoder.transform([level])[0]
    X_input = np.array([[skor, waktu, level_encoded]])

    pred_encoded = model.predict(X_input)[0]
    hasil = label_encoder.inverse_transform([pred_encoded])[0]

    if hasil == "paham":
        feedback_text = "Anda sudah memahami materi dengan baik."
        rekomendasi = "Lanjut ke materi berikutnya."
    elif hasil == "kurang_paham":
        feedback_text = "Pemahaman cukup, namun perlu penguatan."
        rekomendasi = "Pelajari ulang materi dengan contoh tambahan."
    else:
        feedback_text = "Pemahaman masih kurang."
        rekomendasi = "Ulangi materi dari dasar."

    return render_template(
        "feedback.html",
        skor=skor,
        waktu=waktu,
        level=level,
        hasil=hasil,
        feedback=feedback_text,
        rekomendasi=rekomendasi
    )

# ================== AI SEARCHING ==================
def ai_search(jumlah_salah):
    """
    AI Searching + Learning:
    memilih materi berdasarkan pengalaman kesalahan siswa
    """
    if jumlah_salah <= 1:
        return 0  # ulang materi dasar
    else:
        return 1  # materi alternatif (lebih detail)

# ================== HASIL ==================
@app.route("/hasil")
def hasil():
    return render_template("hasil.html")

if __name__ == "__main__":
    app.run(debug=True)
