import requests, json, argparse, os, uuid, time

def ttsmaker_query(text, output_file, token="ttsmaker_demo_token", voice_id=147, audio_format="mp3", speed=1.00, volume=1, paragraph_pause=0):
    if "\n" in text:
        concat_command = "sox "
        for text_frag in text.split("\n"):
            if len(text_frag):
                frag = str(uuid.uuid4()) + "." + audio_format
                ttsmaker_query(text_frag, frag, token, voice_id, audio_format, speed, volume, paragraph_pause)
                concat_command += frag + " "
        concat_command += "-C 0 " + output_file + " silence -l 1 0.1 1% -1 0.55 1%"
        os.system(concat_command)
        return output_file

    url = 'https://api.ttsmaker.com/v1/create-tts-order'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    params = {
        'token': token,
        'text': text,
        'voice_id': voice_id,
        'audio_format': audio_format,
        'audio_speed': 1.0,
        'audio_volume': volume,
        'text_paragraph_pause_time': paragraph_pause
    }
    response = requests.post(url, headers=headers, data=json.dumps(params)).json()
    time.sleep(1)

    with open(os.path.abspath(output_file), "wb+") as out:
        content = requests.get(response["audio_file_url"], stream=True).content
        out.write(content)
    
    os.system("sox " + " -v " + str(volume) + " " + output_file + " -C 0 TMP" + output_file + " silence -l 1 0.1 1% -1 0.55 1% tempo " + str(speed))
    os.system("mv TMP" + output_file + " " + output_file)
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--token", default="ttsmaker_demo_token")
    parser.add_argument("--voice-id", type=int, default=147)
    parser.add_argument("--format", default="mp3")
    parser.add_argument("--speed", type=float, default=1.00)
    parser.add_argument("--volume", type=float, default=1)
    parser.add_argument("--paragraph-pause", type=int, default=0)
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()

    ttsmaker_query(args.text, args.output_file, args.token, args.voice_id, args.format, args.speed, args.volume, args.paragraph_pause)



