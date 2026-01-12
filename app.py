from flask import Flask, render_template, request, session, redirect, url_for
import json

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

    if request.method == "POST":
        jawaban_user = request.form.to_dict()
        waktu = int(jawaban_user.pop("waktu"))

        soal_level = data_soal[tingkat]
        benar = 0

        for i, soal in enumerate(soal_level):
            if jawaban_user.get(f"q{i}") == soal["jawaban"]:
                benar += 1

        return redirect(
            f"/feedback?benar={benar}&total={len(soal_level)}&waktu={waktu}&tingkat={tingkat}"
        )       


    return render_template(
        "soal.html",
        tingkat=tingkat,
        soal=data_soal[tingkat]
    )


# ================== (3) FEEDBACK + AI ==================
@app.route("/feedback")
def feedback():
    benar = int(request.args.get("benar"))
    total = int(request.args.get("total"))
    waktu = int(request.args.get("waktu"))
    tingkat = request.args.get("tingkat")

    skor = benar / total

    # RULE-BASED AI
    if skor >= 0.8 and waktu <= 60:
        status = "sangat_baik"
        pesan = "Anda menjawab dengan benar dan cepat. Pemahaman Anda sangat baik."
        rekomendasi = "Lanjut ke tingkat yang lebih sulit."
        next_url = "/tingkat_kesulitan"

    elif skor >= 0.8:
        status = "baik"
        pesan = "Jawaban Anda benar, namun membutuhkan waktu cukup lama."
        rekomendasi = "Disarankan mempelajari penguatan materi."
        next_url = f"/materi/{tingkat}"

    else:
        status = "perlu_ulang"
        pesan = "Pemahaman Anda belum optimal."
        rekomendasi = "Silakan mengulang materi dengan penjelasan lebih sederhana."
        next_url = f"/materi/{tingkat}"

    return render_template(
        "feedback.html",
        benar=benar,
        total=total,
        waktu=waktu,
        pesan=pesan,
        rekomendasi=rekomendasi,
        next_url=next_url
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
