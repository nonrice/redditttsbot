# Eric's Reddit TTS Bot
Reddit text-to-speech videos are a popular form of low-effort yet mildly engaging content which is common throughout many short-form video platforms. The goal of this project is to fully automate the production of such videos.
### Basic Usage
Install FFMPEG, ImageMagick, Firefox, and the necessary Python dependencies (`requirements.txt`). Using a virtual environment is recommended. 

Run `main.py` to produce a video. There are many flags you may add for increased customization, but the below command includes the bare minimum:
```
python main.py --background /path/to/background/video
```
Look at [configuration.md](configuration.md) for documentation on additional configuration flags.

### Caveats
Text to speech generation only works on OS X, at the moment. If you are not a Mac user you should modify the text to speech commands (`os.system("say...`) to use the appropriate TTS utility for your platform. If other people actually use this project I might upgrade this part to be more cross-platform. 
