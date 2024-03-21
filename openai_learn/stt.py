from openai import OpenAI
from pathlib import Path
client = OpenAI()
speeach_file_path = Path(__file__).parent / "speech.mp3"
audio_file = open(speeach_file_path,'rb')

transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="text",
    #timestamp_granularities=["word"]
)

print(transcript)