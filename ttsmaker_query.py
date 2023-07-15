import requests, json, argparse, os

def ttsmaker_query(text, output_file, token="ttsmaker_demo_token", voice_id=147, audio_format="wav", speed=1.05, volume=0, paragraph_pause=0):
    url = 'https://api.ttsmaker.com/v1/create-tts-order'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    params = {
        'token': token,
        'text': text,
        'voice_id': voice_id,
        'audio_format': audio_format,
        'audio_speed': speed,
        'audio_volume': volume,
        'text_paragraph_pause_time': paragraph_pause
    }
    response = requests.post(url, headers=headers, data=json.dumps(params)).json()

    with open(os.path.abspath(output_file), "wb+") as out:
        content = requests.get(response["audio_file_url"], stream=True).content
        out.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--token", default="ttsmaker_demo_token")
    parser.add_argument("--voice-id", type=int, default=147)
    parser.add_argument("--format", default="wav")
    parser.add_argument("--speed", type=float, default=1.05)
    parser.add_argument("--volume", type=float, default=0)
    parser.add_argument("--paragraph-pause", type=int, default=0)
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()

    ttsmaker_query(args.text, args.output_file, args.token, args.voice_id, args.audio_format, args.audio_speed, args.audio)


