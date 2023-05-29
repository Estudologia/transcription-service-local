import transcription
import questions

def main():
    print("Processing the transcription...")
    video_url = input("Enter the GoogleDrive URL: ")
    transcription.main(video_url)

    print("Generating and saving questions...")
    questions.main(video_url)

    print("All tasks completed successfully.")

if __name__ == "__main__":
    main()
