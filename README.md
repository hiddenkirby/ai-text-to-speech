# ai-speech-to-text

## This is a sample application that uses a replicate.com model called vaibhavs10/incredibly-fast-whisper to generate speech to text

## It then uses mistralai/mixtral-8x7b-instruct-v0.1 (small llm, fast) to correct the text grammar and such

1. run `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Make sure you at least have a .env file with the following:
   REPLICATE_API_TOKEN="<your-api-token>"
   AWS_ACCESS_KEY="<your-aws-access-key>">"
   AWS_SECRET_KEY="<your-aws-secret-key>"
5. `python3 app.py`

## This will spin up a local UI on port 8080

1. Press the record icon to start recording
2. Press the stop icon to stop recording
3. You will see the text that was generated from the audio
