from flask import Flask, render_template, jsonify, session
from flask_socketio import SocketIO
from flask_cors import CORS
import io
import os
import wave
import time
import asyncio
import multiprocessing as mp
from multiprocessing import Process
import librosa
from faster_whisper import WhisperModel

def save_audio_data(audio_data):
    # Choose a suitable path and filename for saving the audio file
    save_path = os.path.join(app.root_path, 'uploads')  # 'uploads' is a folder in your Flask app
    os.makedirs(save_path, exist_ok=True)
    # You can generate a unique filename based on timestamp or other criteria
    filename = 'audio_recording.wav'
    file_path = os.path.join(save_path, filename)

    with wave.open(f"sound_{int(time.time())}.wav", "w") as f:
        # 1 Channels.
        f.setnchannels(2)
        # 1 bytes per sample.
        f.setsampwidth(2)
        f.setframerate(22050)
        f.writeframes(bytes(audio_data))
    return file_path

app = Flask(__name__,
            static_url_path='',  
            static_folder='web/static', 
            template_folder='web/templates')
CORS(app, resources={r"/*": {"origins": "*"}})
#CORS(app, resources={r"/*": {"origins": "http://localhost:*"}})
socketio = SocketIO(app,cors_allowed_origins="*")
@app.route('/')
def hello():
    return render_template('index.html')

@socketio.on('recording')
def handle_recording(message):
    if message == "stop":
        saved_file_path = save_audio_data(session["datablob"])
        print('Audio data saved to:', saved_file_path)
        socketio.emit('stop_recording', namespace='/')
        session["datablob"].clear
        session["recv_counter"] = 0
        
        return jsonify({'status': 'Recording stopped'})
    elif message == "start":        
        session["datablob"] = []  
        session["text"] = ""
        session["length"] = 0.0
        socketio.emit('start_recording', namespace='/')
        session["recv_counter"] = 0
        session["req_running"] = True
        session["model"] = WhisperModel("base", device="cpu")
        y, _ = librosa.load("tempaudio.wav", sr=16000, mono=True)
        session["req_running"] = False
        return jsonify({'status': 'Recording started'})

def transcribe_whisper(data):
    global model

@socketio.on('message')
def handle_message(message):
    global model
    print('Received:', len(message))
    # WAV Header goes till Byte 43
    session["length"] += 0.25
    if session["length"] > 10:
        session["datablob"] = []
    session["datablob"] += message[44:]
    session["recv_counter"] += 1
    if session["recv_counter"] > 4 and session["req_running"] == False:
        session["req_running"] = True
        session["recv_counter"] = 0
        with wave.open("tempaudio.wav", "w") as f:
            # 1 Channels.
            f.setnchannels(2)
            # 1 bytes per sample.
            f.setsampwidth(2)
            f.setframerate(22050)
            f.writeframes(bytes(session["datablob"]))
        y, _ = librosa.load("tempaudio.wav", sr=16000, mono=True)
        timenow = time.time()
        segments, info = session["model"].transcribe(y, beam_size=1)
        txt = ""
        for segment in segments:
            txt += segment.text
        timeafter = time.time()        
        print(f"{timeafter-timenow}")
        socketio.emit("output-recv", txt)
        session["req_running"] = False


if __name__ == '__main__':    
    socketio.run(app, debug=True, port=5000)
    