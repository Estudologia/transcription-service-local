# transcription-service-local

pip3 install -r ./requirements.txt
sudo apt install gunicorn

export OPENAI_API_KEY=XXXXXX
gunicorn flaskapi:api --timeout 1200

http://localhost:8000/checkenv.json
