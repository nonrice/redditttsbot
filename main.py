import random, argparse, os, textwrap
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import whisper
from whisper.utils import get_writer
from wand.image import Image
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

#TODO Implement use post flag, use relpaths for background video

parser = argparse.ArgumentParser()
parser.add_argument("--subreddit", action="store", default="askreddit")
parser.add_argument("--min-len", action="store", default=600, type=int)
parser.add_argument("--len-range", action="store", default=300, type=int)
parser.add_argument("--use-post", action="store_true")
parser.add_argument("--subtitle-wrap-width", action="store", default=30, type=int)
parser.add_argument("--subtitle-font", action="store", default="Arial")
parser.add_argument("--subtitle-font-size", action="store", default=60, type=int)
parser.add_argument("--post-pool-size", action="store", default=20, type=int)
parser.add_argument("--comment-pool-size", action="store", default=40, type=int)
parser.add_argument("--post-time-span", action="store", default="day")
parser.add_argument("--firefox-profile", action="store")
parser.add_argument("--subtitle-outline-size", action="store", default=14, type=int)
parser.add_argument("--background", action="store")
parser.add_argument("--random-cutout", action="store_true")
parser.add_argument("--headless", action="store_true")
args = parser.parse_args()

# Scrape video content (post and comment)
header = { "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0" }  
posts = requests.get(f"https://www.reddit.com/r/{args.subreddit}/top/.json?count={args.post_pool_size}&t={args.post_time_span}", headers=header).json()["data"]["children"]
random.shuffle(posts)
selected_comment = ""
selected_post = ""
for post in posts:
    post_id = post["data"]["id"]
    comments = requests.get(f"https://www.reddit.com/r/{args.subreddit}/comments/{post_id}.json?depth=1&limit={args.comment_pool_size}&sort=top", headers=header).json()
    random.shuffle(comments)
    found_comment = False
    for comment in comments[1]["data"]["children"][1:-1]:
        if args.min_len <= len(comment["data"]["body"]) <= args.min_len + args.len_range:
            selected_comment = comment["data"]["body"]
            selected_post = post["data"]["title"]
            found_comment = True
            break
    if found_comment: break
selected_comment = selected_comment.replace("'", "'\\''")
selected_post = selected_post.replace("'", "'\\''")

# Get a good photo of the post
firefox_args = Options()
if args.firefox_profile is not None:
    firefox_args.add_argument("-profile")
    firefox_args.add_argument(args.firefox_profile);
if args.headless:
    firefox_args.add_argument("-headless")
driver = webdriver.Firefox(options = firefox_args)
driver.get(f"https://sh.reddit.com/r/AskReddit/comments/{post_id}/")
driver.execute_script(f"document.getElementById(\"t3_{post_id}\").style.maxWidth=\"60ch\"")
driver.execute_script(f"document.getElementById(\"t3_{post_id}\").style.padding=\"3ch\"")
element = driver.find_element(By.ID, f"t3_{post_id}")
element.screenshot("intro.png")
driver.quit()
intro = Image(filename = "intro.png")
intro.resize(1000, int((intro.height/intro.width) * 1000))
intro.crop(1, 2, intro.width-2, intro.height-2)
intro.save(filename = "intro.png")

# Generate TTS and subtitles
os.system(f"say '{selected_post} [[slnc 300]]' --voice daniel --rate 195 -o voice1.aiff")
os.system(f"say '{selected_comment} [[slnc 500]]' --voice daniel --rate 195 -o voice2.aiff")
model = whisper.load_model("medium")
result = model.transcribe("voice2.aiff")
srt = [((segment["start"], segment["end"]), segment["text"]) for segment in result["segments"]]

# Load video assets
img = ImageClip("intro.png")
voice1 = AudioFileClip("voice1.aiff")
voice2 = AudioFileClip("voice2.aiff")
video = VideoFileClip(args.background)
srt = list(map(lambda t : ((t[0][0]+voice1.duration, t[0][1]+voice1.duration), textwrap.fill(t[1], width=args.subtitle_wrap_width)), srt))
generator = lambda txt: TextClip(txt, font=args.subtitle_font, fontsize=args.subtitle_font_size, size=(video.w-100, video.h), color="white", method="label")
subtitles = SubtitlesClip(srt, generator)
generator_stroked = lambda txt: TextClip(txt, font=args.subtitle_font, fontsize=args.subtitle_font_size, size=(video.w-100, video.h), stroke_color="black", stroke_width=args.subtitle_outline_size, color="white", method="label")
subtitles_stroked = SubtitlesClip(srt, generator_stroked)

# Composite video assets
voice_concat = concatenate_audioclips([voice1, voice2]) 
final_video = None 
if not args.random_cutout:
    final_video = video.subclip(0, voice_concat.duration).set_audio(voice_concat)
else:
    offset = random.randint(0, int(video.duration-voice_concat.duration-1))
    final_video = video.subclip(0 + offset, voice_concat.duration + offset).set_audio(voice_concat)
output = CompositeVideoClip([final_video, subtitles_stroked.set_pos(("center", "center")), subtitles.set_pos(("center","center")), img.set_duration(voice1.duration).set_pos(("center", "center"))])
output.write_videofile("output.mp4", fps=video.fps, codec="libx264", audio_codec="aac")
