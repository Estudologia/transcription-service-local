import os
import openai
from typing import List
from transcription import split_transcription
import pdb;
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


def generate_questions_from_transcription(transcription: str, num_questions: int = 3) -> List[str]:
    prompt = f"Dado o seguinte texto em português brasileiro:\n\n{transcription}\n\nGere {num_questions} questões de múltipla escolha com 5 opções cada e indique a opção correta.\n\n"
    print(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um experiente professor de ensino médio especializado em gerar questões de múltipla escolha."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        n=1,
        temperature=0.5,
    )

    # pdb.set_trace()
    generated_questions = response.choices[0].message["content"].strip()
    return generated_questions

def split_transcription(transcription: str, max_tokens: int = 4000) -> List[str]:
    words = transcription.split(" ")
    segments = []
    current_segment = []

    tokens_count = 0
    for word in words:
        tokens_count += len(word.split(" ")) + 1
        if tokens_count > max_tokens:
            segments.append(" ".join(current_segment))
            current_segment = []
            tokens_count = len(word.split(" ")) + 1
        current_segment.append(word)

    if current_segment:
        segments.append(" ".join(current_segment))

    return segments

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

def format_to_object(question_list):
    generated_questions = question_list.replace("\n\n", "\n").split("\n")
    groups = [list(group) for group in zip(*[iter(generated_questions)]*7)]

    list_objects = []
    for question in groups:
        list_objects.append({
            'title': question[0],
            'alternatives': question[1:-1],
            'correct_alternative': question[-1]
        })
    return list_objects


def main(video_url: str):
    video_id = video_url.split('/d/')[1].split('/')[0]
    num_questions = 3
    output_dir = f"questions/{video_id}"
    transcription_dir = f"transcriptions/{video_id}"

    os.makedirs(output_dir, exist_ok=True)
    transcription_files = [f for f in os.listdir(transcription_dir) if f.endswith(".txt")]

    response_list = []
    for i, file_name in enumerate(transcription_files):
        persisted_file = read_file_content(f"questions_{i}.txt", output_dir)
        if persisted_file == False:
            print(f"Lendo a transcrição do segmento {i}...")
            with open(os.path.join(transcription_dir, file_name), "r", encoding="utf-8") as file:
                transcription = file.read()

            print(f"Gerando questões para o segmento {i}...")
            question_list = generate_questions_from_transcription(transcription, num_questions)
            questions_file_name = f"questions_{i}.txt"
            questions_file_path = os.path.join(output_dir, questions_file_name)

            with open(questions_file_path, "w", encoding="utf-8") as file:
                for question in question_list.split("\n\n"):
                    file.write(question)
                    file.write("\n\n")

            print(f"Questões salvas em '{questions_file_path}'")
        else:
            question_list = persisted_file
        response_list.append(format_to_object(question_list))

    return response_list

if __name__ == "__main__":
    main()
