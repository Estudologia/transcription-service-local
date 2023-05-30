import os
import transcription;
import questions;
from flask import Flask, json, request, jsonify;
import pdb;
import time;
import threading;

api = Flask(__name__)

def read_file_content(file_name, output_dir):
    # Construct the file path by joining the output_dir and file_name
    file_path = os.path.join(output_dir, file_name)
    try:
        # Try to open the file in read mode
        with open(file_path, 'r') as file:
            # Read the content of the file
            content = file.read()
            return content
    except FileNotFoundError:
        # File not found, return False
        return False

def async_transcription(video_url):
  transcription.main(video_url)

@api.route('/', methods=['GET'])
def welcome():
  return jsonify({"success": True}), 200

@api.route('/checkenv.json', methods=['GET'])
def check_env():
  return json.dumps(os.getenv('OPENAI_API_KEY'))

@api.route('/taxonomies.json', methods=['GET'])
def get_taxonomies():
  time.sleep(65)
  taxonomies = [{"id": 1, "name": "Taxonomy One"}, {"id": 2, "name": "Taxonomy Two"}]
  return json.dumps(taxonomies)

@api.route('/get_video_transcription.json', methods=['POST'])
def post_video_transcription():
  video_url = request.args.get('video_url')
  print(video_url)

  transcription_text, segments = transcription.main(video_url)
  question_list = questions.main(video_url)

  # pdb.set_trace()

  return jsonify({
    "video_url": video_url,
    "success": True,
    "transcription": transcription_text,
    "segments": segments,
    "questions": question_list
  }), 200

@api.route('/video_transcription.json', methods=['POST'])
def video_transcription():
  video_url = request.args.get('video_url')
  video_id = video_url.split('/d/')[1].split('/')[0]
  print(video_url)
  print(video_id)

  # CHECK FILE EXISTS
  persisted_file = read_file_content("transcription.txt", f"all_transcriptions/{video_id}")
  if persisted_file == False:
    try:
      # transcription.download_video_and_extract_audio(video_id)
      t = threading.Thread(target=async_transcription, args=(video_url,))
      t.start()
      return jsonify({ "success": True, "message": "Processing" })
    except:
      return jsonify({ "success": False, "message": "ERROR" })
  else:
    return jsonify({ "video_url": video_url, "success": True, "transcription": persisted_file }), 200

if __name__ == '__main__':
    api.run(debug=True, port=8000)
