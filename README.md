# transcription-service-local

pip3 install -r ./requirements.txt
gunicorn flaskapi:api --timeout 1200

export OPENAI_API_KEY=XXXXXX
http://localhost:8000/checkenv.json
