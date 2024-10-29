from moviepy.editor import VideoFileClip, AudioFileClip
import ffmpeg, os

def merge_audio(video, audio, output):
    video_clip = VideoFileClip(video)
    audio_clip = AudioFileClip(audio)

    video_clip = video_clip.set_audio(audio_clip)

    video_clip.write_videofile(
        output, 
        threads=4,
        preset="ultrafast"  
    )