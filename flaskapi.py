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


def async_download_video_and_extract_audio(video_url):
  transcription.download_video_and_extract_audio(video_url)


def async_audio_to_txt(video_id):
  project_dir = os.path.dirname(os.path.abspath(__file__))
  compressed_audio_path = os.path.join(project_dir, f"temp_audio/{video_id}/audio_compressed.mp3")
  transcribe_audio(compressed_audio_path, "mp3")


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


@api.route('/massive_transcription.json', methods=['POST'])
def massive_transcription():
  path = 'temp_audio'
  processed_files_path = 'massive-transcription-data/processed_files.txt'
  files_to_process = os.listdir(path)
  count = 0

  for file in files_to_process:
    processed_files = open(processed_files_path, 'r+')
    processed_files_name = [processed_files_name.strip() for processed_files_name in processed_files.readlines()]
    video_exist = os.path.exists(f"temp_audio/{file}/video.mp4")
    audio_not_exist = not os.path.exists(f"temp_audio/{file}/audio.mp3")
    audio_compressed_not_exist = not os.path.exists(f"temp_audio/{file}/audio_compressed.mp3")

    if (file not in processed_files_name) and video_exist and audio_not_exist and audio_compressed_not_exist:
      try:
        count += 1
        t = threading.Thread(target=async_download_video_and_extract_audio, args=(file,))
        t.start()
        processed_files.write(file+'\n')
        processed_files.close()
        if count % 5 == 0:
          time.sleep(5*60)
      except:
        return jsonify({"Error": "\nError in file: " % file})

  return jsonify({"Finished": "True"})

@api.route('/audio_to_txt.json', methods=['GET'])
def audio_to_txt():
  processing_pending_path = 'massive-transcription-data/processing_pending.txt'
  pending_files = open(processing_pending_path, 'r')
  pending_path_name = [p.strip() for p in pending_files.readlines()]
  current_pending_path_name = pending_path_name
  pending_files.close()
  count = 0

  for folder_name in pending_path_name:
    try:
      count += 1
      t = threading.Thread(target=async_audio_to_txt, args=(folder_name,))
      t.start()
      print(folder_name)
      current_pending_path_name.remove(folder_name)
      with open(processing_pending_path, 'w') as file:
        file.write(current_pending_path_name)

      if count % 5 == 0:
        time.sleep(5*60)
    except:
      print("\nError in folder: %s" % folder_name)


  return jsonify({"Finished": "True"})


if __name__ == '__main__':
  api.run(debug=True, port=8000)
