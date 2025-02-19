from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from dotenv import load_dotenv
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os, io

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    if not video_url:
        flash('Por favor insira uma URL válida!', 'error')
        return redirect(url_for('home'))
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        buffer = io.BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)
        filename = yt.title + '.mp4'
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='video/mp4')
    except Exception as e:
        flash(f'Ocorreu um erro ao tentar baixar o video, {str(e)}', 'error')
        return redirect(url_for('home'))
    
@app.route('/doacoes', methods=['GET'])
def doacoes():
    return render_template('doacoes.html')