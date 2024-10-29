import requests, json, random
from groq import Groq
import subprocess, os
import ffmpeg
from datetime import timedelta
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
load_dotenv()

def seconds_to_time_string(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(td.microseconds / 10000)  

    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:02}"

def trim_video_optimized(orientation, input_file: str, output_file: str, end_time: float, start_time: int = 0):
    try:
        resolutions = [(960, 540), (540, 960), (540, 540)]

        target_resolution = None
        if orientation == 'portrait': target_resolution = resolutions[0]
        elif orientation == 'landscape': target_resolution = resolutions[1]
        else: target_resolution = resolutions[2]
        
        video = VideoFileClip(
            input_file,
            audio=False,
            target_resolution= target_resolution,  
            resize_algorithm='fast_bilinear'  
        )
        
        trimmed_video = video.subclip(start_time, end_time)
        
        trimmed_video.write_videofile(
            output_file,
            codec='libx264',
            preset='ultrafast', 
            threads=4, 
            fps=30,
            bitrate=None, 
            audio=False,
            verbose=False
        )
        
        video.close()
        trimmed_video.close()
        
        return f"Video trimmed successfully and saved as {output_file}"
        
    except Exception as e:
        return f"Error occurred: {str(e)}"
    finally:
        try:
            video.close()
            trimmed_video.close()
        except:
            pass


def trim_video(input_file: str, output_file: str, end_time: float, start_time: int = 0):
    try:    
        print('END TIME:', end_time)
        command = [
            'ffmpeg',
            '-i', input_file,
            '-ss', str(start_time),
            '-t', str(end_time),
            '-avoid_negative_ts', '1', 
            '-y',  
            output_file
        ]
        
        result = subprocess.run(
            command,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr.decode()}")
        
        print(f"Video trimmed successfully and saved as {output_file}")
        
    except Exception as e:
        return f"Error occurred: {str(e)}"
    

def download_video(url, end_time, uuid, orientation, output_filename):
    try:
        headers = {
            'Authorization': os.environ['PEXELS_API_KEY'],
            'User-Agent': 'Mozilla/5.0'  
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        with open(f'videos/{output_filename}', 'wb') as f:
            f.write(response.content)
        
        print(f"Video successfully downloaded as '{output_filename}'")

        trim_video_optimized(orientation, f'videos/{output_filename}', f'videos/t_{output_filename}', end_time)

        os.remove(f'videos/{output_filename}')
        print(f'Trimmed video and deleted the previous one: {output_filename}\n')
        t_video = VideoFileClip(f'videos/t_{output_filename}')
        dur = t_video.duration
        t_video.close()
        print('TRIMMED:', dur)
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the video: {e}")
    except IOError as e:
        print(f"Error saving the file: {e}")

def download_stock_videos(segments, uuid, orientation):
    groq = Groq(max_retries = 3)
    video_files = []
    
    counter = 0

    for ind, segment in enumerate(segments):
        text = segment['text']

        if ind == 0:
            video_length = segment['end'] - segment['start']
        else:
            video_length = segments[ind]['end'] - segments[ind - 1]['end']

        completion = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "As a language model, your task is to extract the main action or subject from each sentence given.\nFocus on capturing the central element or event that best summarizes what is happening, using concise phrases.\nIgnore specific details like dates, proper nouns, and additional descriptors unless they are essential to understanding the action or subject.\nUse simplified language that reflects the core theme, object, or action.\nAvoid using quotation marks in both the input and output.\nHere are some examples:\n\n- Input: In 2154, the once-blue skies turned a hazy gray.\n - Output: hazy gray sky\n\n- Input: Cities floated on water, a desperate attempt to escape the rising tides.\n - Output: high tides\n\n- Input: Robots worked tirelessly, harvesting the last of the world's resources.\n - Output: Robots working\n\n- Input: A lone astronaut, drifting through space, gazed back at the dying planet.\n - Output: astronaut in space\n\nFollow this format for each new sentence provided."
                },
                {
                    "role": "user",
                    "content": "Given sentence: " + text
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        search_word_for_stock_vid = completion.choices[0].message.content
        print('word to be search:', search_word_for_stock_vid, '\n\n')

        url = "http://localhost:8000/api/pexels"

        payload = json.dumps({ "query": search_word_for_stock_vid, "orientation": orientation })
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        videos = response.json()['videos']
        download_url = ''
        size = len(videos) - 1

        safety_counter = 0
        while True:
            print('trying')
            try:
                random_index = random.randint(0, size - 3)
                temp_videos = videos[random_index]['video_files']
                for video in temp_videos:
                    if orientation == 'portrait' and video['width'] == 540 and video['height'] == 960:
                        download_url = video['link']
                        break

                    if orientation == 'landscape' and video['width'] == 960 and video['height'] == 540:
                        download_url = video['link']
                        break

                    if orientation == 'square' and video['width'] == 540 and video['height'] == 540:
                        download_url = video['link']
                        break

                    if safety_counter > 10:
                        download_url = video['link']
                        break

                if download_url != '':
                    break
            except Exception as e:
                print(e)
                continue
            finally: safety_counter += 1
        
        print('download url: ', download_url)        

        download_video(download_url, video_length, uuid, orientation, f'{uuid}_{counter}.mp4')

        video_files.append(f't_{uuid}_{counter}.mp4')

        counter += 1
    return video_files



    