# -*- coding: utf-8 -*-
"""
Flask 音乐 API 应用
支持中文歌名和歌词文件处理，支持文件上传功能，包括视频封面。
"""
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import urllib.parse
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

# 项目根目录路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'static/songs')
LYRICS_DIR = os.path.join(BASE_DIR, 'static/lyrics')
COVERS_DIR = os.path.join(BASE_DIR, 'static/covers')
# 视频文件目录
VIDEO_FOLDER = os.path.join(app.static_folder, 'video')

# 确保目录存在
os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(LYRICS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # 渲染 HTML 页面

# 获取歌曲列表，包括封面视频路径
@app.route('/api/songs', methods=['GET'])
def get_song_list():
    try:
        songs = []
        for song_file in os.listdir(SONGS_DIR):
            if song_file.endswith('.mp3'):
                song_title = song_file[:-4]  # 去掉文件后缀
                song_source = f"/static/songs/{song_file}"
                cover_video = f"/static/covers/{song_title}.mp4"
                # 如果封面视频不存在，则返回空值
                cover_video = cover_video if os.path.exists(os.path.join(COVERS_DIR, f"{song_title}.mp4")) else None
                # 假设歌手名为"Unknown Artist"
                songs.append({
                    "title": song_title,
                    "name": "Delia pika",
                    "source": song_source,
                    "cover": cover_video
                })
        return jsonify({"songs": songs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取歌词文件
@app.route('/api/lyrics/<path:song_name>', methods=['GET'])
def get_lyrics(song_name):
    try:
        decoded_name = urllib.parse.unquote(song_name)  # 解码中文歌名
        lyrics_file = os.path.join(LYRICS_DIR, f'{decoded_name}.lrc')
        if os.path.exists(lyrics_file):
            with open(lyrics_file, 'r', encoding='utf-8') as file:
                lyrics = file.read()
            return jsonify({"lyrics": lyrics})
        else:
            return jsonify({"error": "歌词文件未找到"}), 404
    except Exception as e:
        return jsonify({"error": "获取歌词文件时出错", "details": str(e)}), 500

@app.route('/api/videos', methods=['GET'])
def get_video_list():
    """
    获取 static/video 目录下的所有视频文件名
    """
    try:
        # 列出目录中的所有文件
        videos = sorted([f for f in os.listdir(VIDEO_FOLDER) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))])
        return jsonify({'videos': videos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video/<filename>', methods=['GET'])
def serve_video(filename):
    """
    提供单个视频文件的访问
    """
    try:
        return send_from_directory(VIDEO_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "资源未找到", "details": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "内部服务器错误", "details": str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True)
