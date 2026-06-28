from flask import Flask, render_template, request, jsonify, send_file, abort
from dotenv import load_dotenv
from pytubefix import YouTube
import os
import uuid
import threading
import tempfile
import base64

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

TOKEN_FILE = os.path.join(tempfile.gettempdir(), "pytubefix_oauth_token.json")


def setup_oauth_token():
    """Recria o arquivo de token a partir da env var, se ainda não existir."""
    if os.path.exists(TOKEN_FILE):
        return

    encoded_token = os.getenv("YOUTUBE_OAUTH_TOKEN_B64")
    if not encoded_token:
        return

    try:
        token_bytes = base64.b64decode(encoded_token)
        with open(TOKEN_FILE, "wb") as f:
            f.write(token_bytes)
    except Exception as e:
        print(f"Falha ao restaurar token OAuth: {e}")

setup_oauth_token()


jobs = {}
jobs_lock = threading.Lock()


def get_video_info(url):
    """Busca metadados do vídeo e as opções de qualidade disponíveis."""
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, token_file=TOKEN_FILE)

    progressive_streams = (
        yt.streams.filter(progressive=True, file_extension="mp4")
        .order_by("resolution")
        .desc()
    )

    qualities = []
    seen = set()
    for stream in progressive_streams:
        if stream.resolution and stream.resolution not in seen:
            qualities.append(stream.resolution)
            seen.add(stream.resolution)

    has_audio_only = yt.streams.get_audio_only() is not None

    return {
        "title": yt.title,
        "author": yt.author,
        "thumbnail": yt.thumbnail_url,
        "qualities": qualities,
        "has_audio_only": has_audio_only,
    }


def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c not in '\\/:*?"<>|').strip()


def run_download(job_id, url, quality):
    """Roda em uma thread separada e atualiza o progresso em `jobs`."""

    def progress_callback(stream, chunk, bytes_remaining):
        total = stream.filesize
        downloaded = total - bytes_remaining
        percent = int(downloaded / total * 100) if total else 0
        with jobs_lock:
            jobs[job_id]["progress"] = percent

    try:
        yt = YouTube(
            url,
            use_oauth=True,
            allow_oauth_cache=True,
            token_file=TOKEN_FILE,
            on_progress_callback=progress_callback,
        )

        with jobs_lock:
            jobs[job_id]["status"] = "downloading"
            jobs[job_id]["title"] = yt.title

        if quality == "audio":
            stream = yt.streams.get_audio_only()
            extension = "m4a"
        else:
            stream = yt.streams.filter(
                progressive=True, file_extension="mp4", res=quality
            ).first()
            if stream is None:
                stream = yt.streams.get_highest_resolution()
            extension = "mp4"

        tmp_dir = tempfile.mkdtemp()
        filename = sanitize_filename(f"{yt.title}.{extension}")
        filepath = os.path.join(tmp_dir, filename)

        stream.download(output_path=tmp_dir, filename=filename)

        with jobs_lock:
            jobs[job_id]["status"] = "finished"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["filepath"] = filepath
            jobs[job_id]["filename"] = filename

    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/api/info", methods=["POST"])
def api_info():
    data = request.get_json(silent=True) or {}
    url = data.get("url")

    if not url:
        return jsonify({"error": "Por favor insira uma URL válida!"}), 400

    try:
        info = get_video_info(url)
        return jsonify(info)
    except Exception as e:
        return (
            jsonify({"error": f"Não foi possível obter informações do vídeo: {str(e)}"}),
            400,
        )


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    quality = data.get("quality", "highest")

    if not url:
        return jsonify({"error": "Por favor insira uma URL válida!"}), 400

    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {"status": "starting", "progress": 0}

    thread = threading.Thread(target=run_download, args=(job_id, url, quality), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/progress/<job_id>")
def api_progress(job_id):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify({"error": "Job não encontrado"}), 404

    return jsonify(
        {
            "status": job.get("status"),
            "progress": job.get("progress", 0),
            "title": job.get("title"),
            "error": job.get("error"),
        }
    )


@app.route("/api/file/<job_id>")
def api_file(job_id):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job or job.get("status") != "finished":
        abort(404)

    filepath = job["filepath"]
    filename = job["filename"]

    if not os.path.exists(filepath):
        abort(404)

    mimetype = "audio/mp4" if filename.endswith(".m4a") else "video/mp4"
    return send_file(filepath, as_attachment=True, download_name=filename, mimetype=mimetype)


if __name__ == "__main__":
    app.run(debug=True)