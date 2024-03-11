import replicate
import boto3

import os
import tempfile
from flask import Flask, request, jsonify, render_template

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

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/process-audio', methods=['POST'])
def process_audio_data():
    audio_data = request.files['audio'].read()

    with tempfile.NamedTemporaryFile(delete=False,suffix=".wav") as f:
        f.write(audio_data)
        f.flush()
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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)