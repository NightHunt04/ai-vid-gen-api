from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

def merge_videos_optimized(video_files, output_file):
    temp_clips = []
    clips = []
    
    try:
        for video in video_files:
            print(video)
            clip = VideoFileClip(f'videos/{video}', audio = False)
            clips.append(clip)

        final_concat = concatenate_videoclips(clips, method='compose')
        
        print("Writing final video...")
        final_concat.write_videofile(
            output_file,
            codec='libx264',
            preset='ultrafast',
            threads=4,
            fps=30,
            bitrate='3000k',
            audio=False,
            verbose=False,
        )
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        for clip in temp_clips:
            try:
                clip.close()
            except:
                pass
        
        for video in video_files:
            os.remove(f'videos/{video}')