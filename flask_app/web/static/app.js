
document.addEventListener('DOMContentLoaded', () => {
  let mediaRecorder;
  let audioChunks = [];
  let isRecording = false;

  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const socket = io.connect('http://localhost:5000');
  socket.on("output-recv", (data) => {
    document.getElementById("output").innerHTML = data;
  });

  startBtn.addEventListener('click', startRecording);
  stopBtn.addEventListener('click', stopRecording);

  function startRecording() {
    isRecording = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    audioChunks = [];

    socket.emit('recording', "start");

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        mediaRecorder = new MediaStreamRecorder.StereoAudioRecorder(stream);
        mediaRecorder.mimeType = 'audio/wav';
        mediaRecorder.leftChannel = false
        mediaRecorder.disableLogs = true
        mediaRecorder.sampleRate = 22050;
        mediaRecorder.audioChannels = 1;
        mediaRecorder.ondataavailable = handleDataAvailable;
        mediaRecorder.onstop = handleRecordingStop;

        mediaRecorder.start(timeslice=250);
      })
      .catch((error) => {
        console.error('Error accessing microphone:', error);
      });
  }

  function stopRecording() {
    isRecording = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;

    if (mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    setTimeout(function() {
      socket.emit('recording', "stop");
    }, 200);
  }

  function handleDataAvailable(event) {
      socket.emit('message', event);
  }

  function handleRecordingStop() {
    
  }
});