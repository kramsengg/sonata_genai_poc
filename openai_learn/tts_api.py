from pathlib import Path
from openai import OpenAI

client = OpenAI()

speeach_file_path = Path(__file__).parent / "speech.mp3"

response = client.audio.speech.create(
    model="tts-1-hd",
    voice="alloy",
    input="Hi Ramachandran! Today is wonderful day to build something people love!"
)

response.stream_to_file(speeach_file_path)

# res = client.audio.speech.with_streaming_response(
#     text="Today is wonderful day to build something people love!",
#     engine="voice_ban",
#     sample_rate = 22050

# )

# with open(speeach_file_path, "wb") as f:
#     for chunk in res.iter_content(1024):
#         f.write(chunk)



