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
2. Text to speech generation only works on OS X, at the moment. If you are not a Mac user you should modify the text to speech commands (`os.system("say...`, there are two in total) to use the appropriate TTS utility for your platform. If other people actually use this project I might upgrade this part to be more cross-platform.
    -  Speaking of which, in order to change the voice, just change the system voice. It seems that Siri voices are higher quality than the other builtin voices, and this is the only way to synthesize the Siri voices. 
