import os
import PIL.Image  # type: ignore
import chainlit as cl  # type: ignore
import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv

load_dotenv()  # Make sure this line is executed *before* accessing the environment variable

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") 

print("GOOGLE_API_KEY: ", GOOGLE_API_KEY[1:-2])

# loading model
client = genai.configure(api_key=GOOGLE_API_KEY[1:-2])

# 
def append_messages(img=None, query=None, audio=None):
    message_list = []

    if img:
        message_list.append([query, img])

    if query and not audio:
        message_list.append(f""" "role": "user", "content": {query} """)

    if audio:
        message_list.append([query, audio])

    # -------model inserting------- #
    if audio == None:
        model = genai.GenerativeModel( model_name="gemini-1.5-pro" )
    else:
        model = genai.GenerativeModel( model_name="gemini-1.5-flash" )

    
    print("message_list[0]: ", message_list[0], model)
    response = model.generate_content(message_list[0])
    print(">>>>>>>>>>>>>>>", {response.text})
    return response.text


def audio_process(audio_path):
    # rb == read binary
    audio_file = open(audio_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcription.text


# chainlit ui and input geting point
@cl.on_message
async def chat(msg: cl.Message):

    images = [file for file in msg.elements if "image" in file.mime]
    audio = [file for file in msg.elements if "audio" in file.mime]

    text = None

    if len(images) > 0:
        img = PIL.Image.open(images[0].path)
        print("img >>>>>>", img)

    if len(audio) > 0:
        print("path of audio: ", audio[0].path)
        audio = audio[0].path

    response_msg = cl.Message(content="")

    if len(images) == 0 and len(audio) == 0:
        # for query
        response = append_messages(query=msg.content)
    elif len(audio) == 0:
        # for image with query
        response = append_messages(img=img, query=msg.content)
    else:
        # for audio
        audio_file = genai.upload_file(path=audio)
        print("audio_file: ", audio_file)
        response = append_messages(query=msg.content, audio=audio_file)

    response_msg.content = response

    await response_msg.send()
