import transcription;
import csv;
import time;
import threading;
import subprocess;
import os;

def process_csv_part(batch_number, csv_data):
  destination_path = "/media/davidleandro/SSD_Externo/RAW_VIDEOS/"
  print("Carregando... ("+ str(batch_number) +")");
  for row in csv_data:
    video_path = destination_path+ "temp_audio/" + row[1]+"/video.mp4"
    rclone_command = "rclone copyto GDRIVE:NAS-2023-DRIVE/UPLOAD/\""+ row[0] +"/"+ row[3] +"\" " + video_path
    if not (os.path.exists(video_path) and os.path.getsize(video_path) > 0):
      result = subprocess.run(rclone_command, shell=True, capture_output=True, text=True)
      print(result)
    transcription.download_video_and_extract_audio(row[1], destination_path)

  print("Carregou ("+ str(batch_number) +")");

def split_csv(file_path, num_parts):
  with open(file_path, 'r') as file:
    reader = csv.reader(file, delimiter=";")
    rows = list(reader)
    total_rows = len(rows)
    rows_per_part = total_rows // num_parts

    start = 0
    threads = []

    # Cria as threads para processar cada parte
    for i in range(num_parts):
      print("Processando " + str(i+1));
      end = start + rows_per_part

      if i == num_parts - 1:
        end = total_rows  # A última parte inclui as linhas restantes

      part = rows[start:end]

      thread = threading.Thread(target=process_csv_part, args=((i+1), part,))
      thread.start()
      threads.append(thread)

      start = end

    # Aguarda todas as threads terminarem
    for thread in threads:
      thread.join()


csv_file = 'teste2.csv'
threads = input("Quantas threads vão ser criadas em paralelo? ");
thread_count = int(threads);
split_csv(csv_file, thread_count)
