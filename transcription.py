import os
import openai
from typing import List, Tuple
from moviepy.editor import *
from dotenv import load_dotenv
import gdown
from pydub import AudioSegment
from pydub.utils import mediainfo
import pdb

load_dotenv()

__all__ = ["split_transcription"]


def download_from_google_drive(video_id: str, output_path: str) -> None:
    gdrive_url = f"https://drive.google.com/uc?id={video_id}"
    gdown.download(gdrive_url, output_path, quiet=False)

def compress_mp3(video_id: str, audio_format, audio_path, compressed_audio_path):
    # Lê o arquivo de entrada
    sound = AudioSegment.from_file(audio_path, format="mp3")

    # Aplica a compressão (ajuste o valor de 'bitrate' conforme necessário)
    compressed_sound = sound.export(compressed_audio_path, format="mp3", bitrate="48k")

    # info = mediainfo(audio_path)
    # info_compressed = mediainfo(compressed_audio_path)
    # pdb.set_trace()

    # Imprime o tamanho do arquivo original e comprimido
    original_size = os.path.getsize(audio_path)
    compressed_size = os.path.getsize(compressed_audio_path)
    print(f"Tamanho original do arquivo: {original_size} bytes")
    print(f"Tamanho do arquivo comprimido: {compressed_size} bytes")


def download_video_and_extract_audio(video_id: str, audio_format: str = "mp3") -> Tuple[str, str]:
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(f"temp_audio/{video_id}") if not os.path.exists(f"temp_audio/{video_id}") else None
    video_path = os.path.join(project_dir, f"temp_audio/{video_id}/video.mp4")
    audio_path = os.path.join(project_dir, f"temp_audio/{video_id}/audio.{audio_format}")
    compressed_audio_path = os.path.join(project_dir, f"temp_audio/{video_id}/audio_compressed.{audio_format}")

    # Download video
    download_from_google_drive(video_id, video_path)

    # Extract audio from video
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)

    compress_mp3(video_id, audio_format, audio_path, compressed_audio_path)

    # Remove video file
    os.remove(video_path)
    os.remove(audio_path)

    return compressed_audio_path, audio_format

def transcribe_audio(file_path: str, audio_format: str = "mp3") -> str:
    with open(file_path, "rb") as audio_file:
        response = openai.Audio.transcribe('whisper-1', audio_file)

    transcription = response["text"]
    return transcription


def save_transcription_to_file(transcription: str, file_name: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    transcription_file_path = os.path.join(output_dir, file_name)

    with open(transcription_file_path, "w", encoding="utf-8") as file:
        file.write(transcription)


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


def split_audio_into_segments(audio_path: str, segment_length: int = 1500) -> list:
    audio = AudioFileClip(audio_path)
    duration = int(audio.duration)

    segments = []
    for start_time in range(0, duration, segment_length):
        end_time = min(start_time + segment_length, duration)
        segment = audio.subclip(start_time, end_time)
        segment_path = f"{audio_path}_{start_time}_{end_time}.mp3"
        segment.write_audiofile(segment_path)
        segments.append(segment_path)

    return segments


def split_transcription(transcription: str, num_segments: int) -> List[str]:
    words = transcription.split()
    segment_size = len(words) // num_segments

    segments = []
    for i in range(num_segments):
        start = i * segment_size
        end = (i + 1) * segment_size if i < num_segments - 1 else len(words)
        segment = " ".join(words[start:end])
        segments.append(segment)

    return segments


def main(video_url: str):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    video_id = video_url.split('/d/')[1].split('/')[0]

    # GET PERSISTED FILE OR GENERATE TRANSCRIPTION FROM YOUTUBE
    persisted_file = read_file_content("transcription.txt", f"all_transcriptions/{video_id}")
    if persisted_file == False:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        compressed_audio_path = os.path.join(project_dir, f"temp_audio/{video_id}/audio_compressed.mp3")
        if (os.path.exists(compressed_audio_path) and os.path.getsize(compressed_audio_path) > 0):
            print("Transcribing audio from file persisted")
            transcription_text = transcribe_audio(compressed_audio_path, "mp3")
        else:
            print("Downloading and extracting audio from googleDrive video...")
            audio_path, audio_format = download_video_and_extract_audio(video_id)

            print("Transcribing audio")
            transcription_text = transcribe_audio(audio_path, audio_format=audio_format)

        # print("Splitting audio into segments...")
        # audio_segments = split_audio_into_segments(audio_path, segment_length=1500)
        # print("Transcribing audio segments using Whisper...")
        # transcriptions = []
        # for segment_path in audio_segments:
        #     transcriptions.append(transcribe_audio(segment_path, audio_format=audio_format))
        #     os.remove(segment_path)
        # transcription_text = " ".join(transcriptions)

        # Remove o arquivo de áudio
        # os.remove(audio_path)
    else:
        transcription_text = persisted_file

    print("Splitting transcription into segments...")
    segments = split_transcription(transcription_text, num_segments=5)

    print("Saving transcription segments to 'transcriptions' folder...")
    transcription_output_dir = f"transcriptions/{video_id}"
    for i, segment in enumerate(segments):
        segment_file_name = f"transcription_segment_{i}.txt"
        save_transcription_to_file(segment, segment_file_name, transcription_output_dir)
    print("Transcription segments saved.")

    if persisted_file == False:
        save_transcription_to_file(transcription_text, "transcription.txt", f"all_transcriptions/{video_id}")

    print(f"Transcriptions saved to 'transcription.txt'")
    return transcription_text, segments


if __name__ == "__main__":
    main()
