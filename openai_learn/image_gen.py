from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="a white siamesc cat",
    n=1,
    quality="standard",
    size="1024x1024"
)

image_url = response.data[0].url

print (image_url)