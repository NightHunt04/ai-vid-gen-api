import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from utils.generate_script import generate_script
from utils.generate_speech import tts_neets
from utils.transcribe import transcribe
from utils.download_stock_videos import download_stock_videos
from utils.merge_videos import merge_videos_optimized
from utils.merge_audio import merge_audio
from utils.add_subtitles import add_subtitles_ffmpeg
from utils.generate_link import generate_link
import json

app = Flask(__name__)
CORS(app)

@app.route('/api/status')
def status():
    return 'Hey there'

@app.route('/api/generate_video', methods=['POST'])
def generate():
    data = request.get_json()
    query = data['query']
    uuid = data['uuid']
    orientation = data['orientation']  #landscape, portrait, square

    def generate_stream():
        # generating script
        data = {
            'progress': 1,
            'msg': f'Generating script on : {query}',
            'done': False
        }
        yield json.dumps(data) + '\n'

        script = generate_script(query)

        # generating speech
        data = {
                'progress': 2,
                'msg': f'Generating speech from the text on : {query}',
                'done': False
        }
        yield json.dumps(data) + '\n'

        speech_response = tts_neets(uuid, script)

        # failed to generate speech
        if not speech_response['success']:
            data = {
                'progress': 3,
                'msg': f'Failed to generate speech, cannot complete the progress ahead.\nReason: {speech_response["msg"]}',
                'done': True
            }
            yield json.dumps(data) + '\n'

            return Response(
                generate_stream(),
                mimetype='application/x-ndjson', 
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            )

        # transcribing for time slots
        data = {
            'progress': 3,
            'msg': f'Separating time slots for clips to be fit in',
            'done': False
        }
        yield json.dumps(data) + '\n'

        transcribe_response = transcribe(uuid)
        if not transcribe_response['done']:
            data = {
                'progress': 4,
                'msg': f'Failed to transcribe, cannot complete the progress ahead.\nReason: {transcribe_response["msg"]}',
                'done': True
            }
            yield json.dumps(data) + '\n'

            return Response(
                generate_stream(),
                mimetype='application/x-ndjson', 
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            )
        
        segments = transcribe_response['transcripton'].segments

        data = {
            'progress': 4,
            'msg': f'Downloading stock videos',
            'done': False,
            'segments': len(segments)
        }
        yield json.dumps(data) + '\n'
        
        video_files = download_stock_videos(segments, uuid, orientation)

        # merge download stock videos
        data = {
            'progress': 5,
            'msg': f'Merging all the downloaded stock videos',
            'done': False,
            'segments': len(segments)
        }
        yield json.dumps(data) + '\n'

        merge_videos_optimized(video_files, f'videos/{uuid}_merged_videos.mp4')

        # merging audio with video
        data = {
            'progress': 6,
            'msg': f'Merging audio script with the video',
            'done': False,
        }
        yield json.dumps(data) + '\n'

        merge_audio(f'videos/{uuid}_merged_videos.mp4', f'scripts/{uuid}_script.mp3', f'videos/{uuid}_audio_video_merged.mp4')
        os.remove(f'videos/{uuid}_merged_videos.mp4')

        # adding subtitles
        # data = {
        #     'progress': 7,
        #     'msg': f'Adding subtitles in the video',
        #     'done': False,
        # }
        # yield json.dumps(data) + '\n'

        data = {
            'progress': 7,
            'msg': f'Generating link of the video',
            'done': False,
        }
        yield json.dumps(data) + '\n'

        # add_subtitles_ffmpeg(f'videos/{uuid}_audio_video_merged.mp4', segments, f'videos/{uuid}_final.mp4', uuid)

        # data = {
        #     'progress': 8,
        #     'msg': f'Everything is done, generating final link of the video',
        #     'done': False,
        # }
        # yield json.dumps(data) + '\n'

        link = generate_link(f'videos/{uuid}_audio_video_merged.mp4')
        print('\n\nLINK:', link)
        # os.remove(f'videos/{uuid}_final.mp4')
        os.remove(f'videos/{uuid}_audio_video_merged.mp4')
        os.remove(f'scripts/{uuid}_script.mp3')

        data = {
            'progress': 8,
            'msg': f'Successfully generated video',
            'link': link,
            'done': True,
        }
        yield json.dumps(data) + '\n'

    return Response(
        generate_stream(),
        mimetype='application/x-ndjson', 
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )

if __name__ == '__main__':
    app.run(debug=True)