from groq import Groq
from dotenv import load_dotenv
load_dotenv()

def transcribe(uuid):
    groq = Groq(max_retries = 3)
    filename = f'scripts/{uuid}_script.mp3'

    try:
        with open(filename, 'rb') as file:
            transcripton = groq.audio.transcriptions.create(
                file = (filename, file.read()),
                model = 'whisper-large-v3-turbo',
                response_format = 'verbose_json'
            )

            return { 'transcripton': transcripton, 'done': True }
    except Exception as e:
        return { 'msg': e, 'done': False }