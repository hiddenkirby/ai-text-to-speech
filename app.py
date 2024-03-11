import replicate
import boto3

import os
import tempfile
from flask import Flask, request, jsonify, render_template

import numpy as np
import librosa

from dotenv import load_dotenv
# load environment variables from .env file
load_dotenv()

bucket_name = os.environ.get("AWS_S3_BUCKET")
aws_access_key = os.environ.get("AWS_ACCESS_KEY")
aws_secret = os.environ.get("AWS_SECRET_KEY")

s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret
)

app = Flask(__name__)

def has_sound(audio_path, threshold=0.01):
    y, sr = librosa.load(audio_path, sr=None)
    D = np.abs(librosa.stft(y))
    avg_amplitude = np.mean(D)
    print(f"AMPLITUDE: {avg_amplitude}")
    return avg_amplitude > threshold

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/process-audio', methods=['POST'])
def process_audio_data():
    audio_data = request.files['audio'].read()

    with tempfile.NamedTemporaryFile(delete=False,suffix=".wav") as f:
        f.write(audio_data)
        f.flush()
        if has_sound(f.name):
            s3.upload_file(f.name, bucket_name, f.name)
            temp_audio_uri = f"https://{bucket_name}.s3.amazonaws.com/{f.name}"

            output = replicate.run(
                "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
                input={
                    "task": "transcribe",
                    "audio": temp_audio_uri,
                    "language": "None",
                    "timestamp": "chunk",
                    "batch_size": 64,
                    "diarise_audio": False
                }
            )
            print(output)

            return jsonify({"transcript": output["text"]})
        else:
            return jsonify({"transcript": ''})
    
@app.route('/improve', methods=['POST'])
def improve():
    data = request.get_json()
    transcript = data.get("transcript", "")
    print('Transcript recieved: ',transcript)
    prompt_text = """
    Correct errors in the transcript: amend punctuation, substitute incorrect words.
    Add nothing extra.

    Only return the corrected text.
    """

    prompt = f"""
    Transcript: {transcript}
    ----------
    {prompt_text}
    """

    print('Full prompt to mixtral: ', prompt)

    result = ""

    # The mistralai/mixtral-8x7b-instruct-v0.1 model can stream output as it's running.
    for event in replicate.stream(
        "mistralai/mixtral-8x7b-instruct-v0.1",
        input={
            "top_k": 50,
            "top_p": 0.9,
            "prompt": prompt,
            "temperature": 0.6,
            "max_new_tokens": 1024,
            "prompt_template": "<s>[INST] {prompt} [/INST] ",
            "presence_penalty": 0,
            "frequency_penalty": 0
        },
    ):
    
        result += str(event)

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)