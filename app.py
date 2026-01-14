from flask import Flask, render_template, request, session, redirect, url_for
import json
import joblib
import numpy as np

model = joblib.load("model/decision_tree.pkl")
level_encoder = joblib.load("model/level_encoder.pkl")
label_encoder = joblib.load("model/label_encoder.pkl")

# ================== MAPPING TINGKAT ==================
TINGKAT_ORDER = ["mudah", "normal", "sulit"]

def tingkat_selanjutnya(level):
    if level not in TINGKAT_ORDER:
        return level
    idx = TINGKAT_ORDER.index(level)
    return TINGKAT_ORDER[min(idx + 1, len(TINGKAT_ORDER) - 1)]

def tingkat_sebelumnya(level):
    if level not in TINGKAT_ORDER:
        return level
    idx = TINGKAT_ORDER.index(level)
    return TINGKAT_ORDER[max(idx - 1, 0)]


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
@app.route("/feedback")
def feedback():
    skor = float(request.args.get("skor"))
    waktu = float(request.args.get("waktu"))
    level = request.args.get("level")

    level_encoded = level_encoder.transform([level])[0]
    X = [[skor, waktu, level_encoded]]

    hasil = label_encoder.inverse_transform(model.predict(X))[0]

    keputusan = ""
    next_level = None
    redirect_to = None

    if hasil == "paham":
        if level == "mudah":
            keputusan = "naik_level"
            next_level = "normal"
        elif level == "normal":
            keputusan = "naik_level"
            next_level = "sulit"
        else:
            keputusan = "lulus"
            redirect_to = "/"

    elif hasil == "kurang_paham":
        keputusan = "penguatan"
        redirect_to = url_for("materi_pengayaan", level=level)

    elif hasil == "tidak_paham":
        if level == "mudah":
            keputusan = "penguatan"
            redirect_to = url_for("materi_pengayaan", level=level)
        else:
            keputusan = "turun_level"
            next_level = "mudah" if level == "normal" else "normal"

    return render_template(
        "feedback.html",
        hasil=hasil,
        keputusan=keputusan,
        level=level,
        next_level=next_level,
        redirect_to=redirect_to,
        skor=skor,
        waktu=waktu
    )


@app.route("/materi_pengayaan/<level>")
def materi_pengayaan(level):
    with open("data/materi_pengayaan.json", "r", encoding="utf-8") as f:
        materi = json.load(f)

    if level not in materi:
        return "Materi pengayaan tidak tersedia", 404

    return render_template(
        "materi_pengayaan.html",
        level=level,
        materi=materi[level]
    )


if __name__ == "__main__":
    app.run(debug=True)
