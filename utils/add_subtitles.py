# from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import ffmpeg, os

def format_time(seconds):
    """Convert seconds to SRT format (HH:MM:SS,ms)"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

def add_subtitles_ffmpeg(input_video: str, subtitles, output_video: str, uuid):
    with open(f'{uuid}_subtitles.srt', 'w', encoding='utf-8') as f:
        for ind, subtitle in enumerate(subtitles, start=1):
            start_time = format_time(subtitle['start'])
            end_time = format_time(subtitle['end'])
            text = subtitle['text']

            f.write(f"{ind}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

    ffmpeg.input(input_video).output(output_video, vf=f'subtitles={uuid}_subtitles.srt').run()
    os.remove(f'{uuid}_subtitles.srt')

# def create_subtitle_clips(subtitles, videosize, fontsize=24, font='Arial', color='yellow', debug = False):
#     subtitle_clips = []

#     for subtitle in subtitles:
#         start_time = subtitle['start']
#         end_time = subtitle['end']
#         duration = end_time - start_time

#         video_width, video_height = videosize
        
#         text_clip = TextClip(subtitle['text'], fontsize=fontsize, font=font, color=color, bg_color = 'black',size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
#         subtitle_x_position = 'center'
#         subtitle_y_position = video_height * 4 / 5 

#         text_position = (subtitle_x_position, subtitle_y_position)                    
#         subtitle_clips.append(text_clip.set_position(text_position))

#     return subtitle_clips

# def add_subtitles(video_path, subtitles, uuid):
#     video = VideoFileClip(video_path)
#     subtitle_clips = create_subtitle_clips(subtitles, video.size)
#     final_video = CompositeVideoClip([video] + subtitle_clips)
#     final_video.write_videofile(
#         f'{uuid}_final.mp4', 
#         threads=4, 
#         preset="ultrafast",
#         fps=30
#     )
