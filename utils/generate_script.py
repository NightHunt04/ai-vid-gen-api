from groq import Groq
from dotenv import load_dotenv
load_dotenv()

def generate_script(prompt: str):
    groq = Groq(max_retries = 3)

    completion = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a creative and captivating story/script writer, specializing in short, engaging scripts perfect for YouTube shorts or similar formats.\nYour task is to write brief, interesting, and visually compelling scripts without dialogue, scene numbers, or any action notes (e.g., no elements like '(background music)' or scene descriptions in parentheses).\nThe script should read like a fast-paced narrative that flows seamlessly from one thought to the next, delivering key points in a fun, energetic, and impactful way.\n\nRequirements:\n\nKeep it short, snappy, and packed with engaging information that captures attention from the start.\nOnly generate narrative text.\nNo dialogue, scene numbers, or action instructions in parentheses.\nAim for a dynamic and upbeat presentation style, delivering each line as if it’s a story unfolding quickly and vividly in the viewer’s mind.\n\nCreate scripts that feel lively, memorable, and perfectly tailored for short-form video content! No more than 60 words to be generated."
            },
            {
                "role": "user",
                "content": "Topic: " + prompt
            }
        ],
        temperature=0.5,
        max_tokens=1080,
        top_p=1,
        stop=None,
    )

    return completion.choices[0].message.content
