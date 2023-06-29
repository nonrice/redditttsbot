# Eric's Reddit TTS Bot

[https://www.youtube.com/results?search_query=reddit+text-to-speech+shorts](Reddit Text-To-Speech videos) are a popular form of low-effort yet mildly engaging content which is common throughout many short-form video platforms. The goal of this project is to fully automate the production of such videos.

### Basic Usage
Install [https://ffmpeg.org/](FFMPEG), [https://imagemagick.org/index.php](ImageMagick), and the necessary Python dependencies (`requirements.txt`). Using a virtual environment is recommended. 

Run `main.py` to produce a video. There are many flags you may add for increased customization, but the below command includes the bare minimum:
```
python main.py --background /path/to/background/video
```

I may make another page documenting the rest of the flags soon, but at the moment you can simply look in the source code and infer the meaning of each flag.

### Caveats
At the moment, the background footage must be a 1080p vertical video, since the dimensions of other elements (e.g. subtitles) are hardcoded in. I will probably change this later.

Text to speech generation only works on OS X, at the moment. If you are not a Mac user you should modify the text to speech commands (`os.system("say...`) to use the appropriate TTS utility for your platform. If other people actually use this project I might upgrade this part to be more cross-platform. 