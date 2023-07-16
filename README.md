# Eric's Reddit TTS Bot
Reddit text-to-speech videos are a popular form of low-effort yet mildly engaging content which is common throughout many short-form video platforms. The goal of this project is to fully automate the production of such videos.
### Basic Usage
Install FFMPEG, ImageMagick, Firefox, and the necessary Python dependencies (`requirements.txt`). Using a virtual environment is recommended. 

Run `main.py` to produce a video. There are many flags you may add for increased customization, but the below command includes the bare minimum:
```
python main.py --background /path/to/background/video
```
Look at [configuration.md](configuration.md) for documentation on additional configuration flags.

### Caveats (Please read!)
1. When scraping the screenshot of NSFW posts, the age confirmation dialog will blur and block the content. To work around this, first visit any NSFW post and press the confirmation button. Then, open your local storage and modify the date inside `xpromo-consolidation` to sometime very far into the future, because otherwise, the dialog will begin appearing again after a few days. Note that if you clear your cookies, you will have to perform this again, which is why using a separate browser profile for scraping is highly recommended. 
2. [TTSMAKER](https://ttsmaker.com) has replaced the usage of the OS X voice synthesizer. TTSMaker is kind enough to offer a free, albeit limited API. If their free token quota is used up you must either wait for it to reset (weekly), or contact them for a personal token, which you can supply with the argument `--ttsmaker-token TTSMAKER_TOKEN`.
- Note that the demo token also does not process text that is longer than ~1000 characters. 