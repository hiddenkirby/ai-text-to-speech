const recordButton = document.getElementById('recordButton');
const transcriptDiv = document.getElementById('transcript');

let isRecording = false;
let mediaRecorder;
let intervalId;
let full_transcript = '';

recordButton.addEventListener('click', () => {
  if (!isRecording) {
    startRecording();
    recordButton.textContent = 'Stop Recording';
  } else {
    stopRecording();
    recordButton.textContent = 'Start Recording';
  }
  isRecording = !isRecording;
});

async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });

  function createRecorder() {
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.addEventListener('dataavailable', async (event) => {
      const audioBlob = event.data;
      const formData = new FormData();
      formData.append('audio', audioBlob);

      const transcript_response = await fetch('/process-audio', {
        method: 'POST',
        body: formData,
      });

      const transcript_data = await transcript_response.json();
      if (transcript_data.transcript != null) {
        full_transcript += transcript_data.transcript;
        transcriptDiv.textContent = full_transcript;
      }
    });

    mediaRecorder.start();
  }

  createRecorder();

  intervalId = setInterval(() => {
    mediaRecorder.stop();
    createRecorder();
  }, 2000);
}

function stopRecording() {
  clearInterval(intervalId);
  mediaRecorder.stop();
}
