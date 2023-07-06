import random, argparse, os, textwrap, logging, urllib, time, re
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from wand.image import Image
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from opplast import Upload

parser = argparse.ArgumentParser()
parser.add_argument("--subreddit", action="store", default="askreddit")
parser.add_argument("--min-len", action="store", default=600, type=int)
parser.add_argument("--len-range", action="store", default=300, type=int)
parser.add_argument("--use-post", action="store_true")
parser.add_argument("--subtitle-split-length", action="store", default=30, type=int)
parser.add_argument("--subtitle-font", action="store", default="Arial")
parser.add_argument("--subtitle-font-size", action="store", default=60, type=int)
parser.add_argument("--post-pool-size", action="store", default=20, type=int)
parser.add_argument("--comment-pool-size", action="store", default=40, type=int)
parser.add_argument("--post-time-span", action="store", default="day")
parser.add_argument("--firefox-profile", action="store")
parser.add_argument("--subtitle-outline-size", action="store", default=14, type=int)
parser.add_argument("--background", action="store", required=True)
parser.add_argument("--random-cutout", action="store_true")
parser.add_argument("--headless", action="store_true")
parser.add_argument("--subtitle-color", action="store", default="white")
parser.add_argument("--subtitle-outline-color", action="store", default="black")
parser.add_argument("--subtitle-length", action="store", default=80, type=int)
parser.add_argument("--post-width", action="store", default=1000, type=int)
parser.add_argument("--post-content-max-width", action="store", default=60, type=int)
parser.add_argument("--post-content-padding", action="store", default=3, type=int)
parser.add_argument("--only-video", action="store_true")
parser.add_argument("--video-tags", action="store", default="")
parser.add_argument("--title-before", action="store", default="")
parser.add_argument("--title-after", action="store", default="")
parser.add_argument("--blacklist-words", action="store", default="")
args = parser.parse_args()

# Scrape video content (post and comment)
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0"
}
posts = requests.get(
    f"https://www.reddit.com/r/{args.subreddit}/top/.json?count={args.post_pool_size}&t={args.post_time_span}",
    headers=header,
).json()["data"]["children"]
random.shuffle(posts)
selected_comment = ""
selected_post = ""
for post in posts:
    post_id = post["data"]["id"]
    found_comment = False
    if args.use_post:
        if (
            args.min_len
            <= len(post["data"]["selftext"])
            <= args.min_len + args.len_range
        ):
            selected_comment = post["data"]["selftext"]
            selected_post = post["data"]["title"]
            found_comment = True
    else:
        comments = requests.get(
            f"https://www.reddit.com/r/{args.subreddit}/comments/{post_id}.json?depth=1&limit={args.comment_pool_size}&sort=top",
            headers=header,
        ).json()
        random.shuffle(comments)
        for comment in comments[1]["data"]["children"][1:-1]:
            if (
                args.min_len
                <= len(comment["data"]["body"])
                <= args.min_len + args.len_range
            ):
                selected_comment = comment["data"]["body"]
                selected_post = post["data"]["title"]
                found_comment = True
                break
    if found_comment:
        break
original_selected_comment = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', selected_comment)
selected_comment = original_selected_comment.replace("'", "'\\''")
original_selected_post = selected_post
selected_post = selected_post.replace("'", "'\\''")

# Get a good photo of the post
firefox_args = Options()
if args.firefox_profile is not None:
    firefox_args.add_argument("-profile")
    firefox_args.add_argument(args.firefox_profile)
if args.headless:
    firefox_args.add_argument("-headless")
driver = webdriver.Firefox(options=firefox_args)
driver.get(f"https://sh.reddit.com/r/AskReddit/comments/{post_id}/")
driver.execute_script(
    f'document.getElementById("t3_{post_id}").style.maxWidth="{args.post_content_max_width}ch"'
)
driver.execute_script(
    f'document.getElementById("t3_{post_id}").style.padding="{args.post_content_padding}ch"'
)
if args.use_post:
    driver.execute_script(
        f'document.getElementById("t3_{post_id}-post-rtjson-content").style.display="none"'
    )
driver.execute_script("document.body.style.webkitTransform = 'scale(4.0)'")
element = driver.find_element(By.ID, f"t3_{post_id}")
element.screenshot("intro.png")
driver.quit()
intro = Image(filename="intro.png")
intro.resize(args.post_width, int((intro.height / intro.width) * args.post_width))
intro.crop(1, 2, intro.width - 2, intro.height - 2)
intro.save(filename="intro.png")

# Generate TTS and subtitles
original_selected_comment = textwrap.fill(
    original_selected_comment, width=args.subtitle_length
)
with open("script.txt", "w") as script:
    script.write(original_selected_comment)
os.system(f"say '{selected_post} [[slnc 300]]' --rate 195 -o voice1.aiff")
os.system(f"say '{selected_comment} [[slnc 500]]' --rate 195 -o voice2.aiff")
config_string = "task_language=eng|is_text_type=plain|os_task_file_format=json"
task = Task(config_string=config_string)
task.audio_file_path_absolute = os.path.abspath("voice2.aiff")
task.text_file_path_absolute = os.path.abspath("script.txt")
ExecuteTask(task).execute()
srt = [
    ((float(frag.begin), float(frag.end)), str(frag.text_fragment)[8:])
    for frag in task.sync_map_leaves()[:-1]
]

# Load video assets
img = ImageClip("intro.png")
voice1 = AudioFileClip("voice1.aiff")
voice2 = AudioFileClip("voice2.aiff")
video = VideoFileClip(args.background)
srt = list(
    map(
        lambda t: (
            (t[0][0] + voice1.duration, t[0][1] + voice1.duration),
            textwrap.fill(t[1], width=args.subtitle_split_length),
        ),
        srt,
    )
)
generator = lambda txt: TextClip(
    txt,
    font=args.subtitle_font,
    fontsize=args.subtitle_font_size,
    size=(video.w, video.h),
    color=args.subtitle_color,
    method="label",
)
subtitles = SubtitlesClip(srt, generator)
generator_stroked = lambda txt: TextClip(
    txt,
    font=args.subtitle_font,
    fontsize=args.subtitle_font_size,
    size=(video.w, video.h),
    stroke_color=args.subtitle_outline_color,
    stroke_width=args.subtitle_outline_size,
    color=args.subtitle_color,
    method="label",
)
subtitles_stroked = SubtitlesClip(srt, generator_stroked)

# Composite video assets
voice_concat = concatenate_audioclips([voice1, voice2])
final_video = None
if not args.random_cutout:
    final_video = video.subclip(0, voice_concat.duration).set_audio(voice_concat)
else:
    offset = random.randint(0, int(video.duration - voice_concat.duration - 1))
    final_video = video.subclip(0 + offset, voice_concat.duration + offset).set_audio(
        voice_concat
    )
output = CompositeVideoClip(
    [
        final_video,
        subtitles_stroked.set_pos(("center", "center")),
        subtitles.set_pos(("center", "center")),
        img.set_duration(voice1.duration).set_pos(("center", "center")),
    ]
)
output.write_videofile("output.mp4", fps=video.fps, codec="libx264", audio_codec="aac")

# Upload the video
if not args.only_video:
    upload = None
    if args.firefox_profile is not None:
        upload = Upload(args.firefox_profile, headless=args.headless, timeout=10)
    else:
        raise ValueError("Firefox profile is required for uploading!")
    was_uploaded, video_id = upload.upload(
        os.path.abspath("output.mp4"),
        title=args.title_before + original_selected_post + args.title_after,
        tags=args.video_tags.split(),
        only_upload=False,
    )
    print(f"{video_id} has been uploaded to YouTube")
    upload.close()
