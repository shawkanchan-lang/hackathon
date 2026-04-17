import os
import whisper
from flask import Flask, render_template, request
from moviepy.editor import VideoFileClip

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the Whisper model (base is fast and relatively accurate)
model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "No video uploaded", 400
    
    file = request.files['video']
    video_path = os.path.join(UPLOAD_FOLDER, file.filename)
    audio_path = os.path.join(UPLOAD_FOLDER, "temp_audio.mp3")
    file.save(video_path)

    try:
        # 1. Extract audio from video
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)

        # 2. Transcribe using Whisper
        result = model.transcribe(audio_path)
        captions = result['text']

        # Cleanup temporary files
        video.close()
        return render_template('index.html', captions=captions)
    
    except Exception as e:
        return f"Error processing video: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
