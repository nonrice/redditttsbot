import random, argparse, os, textwrap, logging, urllib, time, re
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from ttsmaker_query import ttsmaker_query
from subsai import SubsAI
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from opplast import Upload

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
parser.add_argument("--background", action="store", required=True)
parser.add_argument("--random-cutout", action="store_true")
parser.add_argument("--headless", action="store_true")
parser.add_argument("--subtitle-color", action="store", default="white")
parser.add_argument("--subtitle-outline-color", action="store", default="black")
parser.add_argument("--post-width", action="store", default=1000, type=int)
parser.add_argument("--post-content-max-width", action="store", default=60, type=int)
parser.add_argument("--only-video", action="store_true")
parser.add_argument("--video-tags", action="store", default="")
parser.add_argument("--title-before", action="store", default="")
parser.add_argument("--title-after", action="store", default="")
parser.add_argument("--force-creation", action="store_true")
parser.add_argument("--ttsmaker-token", action="store", default="ttsmaker_demo_token")
parser.add_argument("--custom-video", action="store_true")
parser.add_argument("--custom-video-selected-post", action="store")
parser.add_argument("--custom-video-selected-post-id", action="store")
parser.add_argument("--custom-video-selected-comment-file", action="store")

args = parser.parse_args()

# Scrape video content (post and comment)
selected_comment = ""
selected_post = ""
post_id = ""
if not args.custom_video:
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0"
    }
    posts = requests.get(
        f"https://www.reddit.com/r/{args.subreddit}/top/.json?count={args.post_pool_size}&t={args.post_time_span}",
        headers=header,
    ).json()["data"]["children"]
    random.shuffle(posts)
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
            comments[1]["data"]["children"] = random.sample(
                comments[1]["data"]["children"][1:-1],
                len(comments[1]["data"]["children"][1:-1]),
            )
            for comment in comments[1]["data"]["children"]:
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
    selected_comment = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)", r"\1", selected_comment
    ).replace("&amp;", "&")
else:
    selected_post = args.custom_video_selected_post
    post_id = args.custom_video_selected_post_id
    with open(os.path.abspath(args.custom_video_selected_comment_file), "r") as content:
        selected_comment = content.read()

if selected_comment == "":
    raise Exception("Couldn't find a suitable comment! Quitting.")

# Get a good photo of the post
driver = None
firefox_args = Options()
firefox_args.add_argument("-width")
firefox_args.add_argument("1920")
firefox_args.add_argument("-height")
firefox_args.add_argument("1080")
try:
    if args.firefox_profile is not None:
        firefox_args.add_argument("-profile")
        firefox_args.add_argument(args.firefox_profile)
    if args.headless:
        firefox_args.add_argument("-headless")
    firefox_args.add_argument("-start-maximized")
    driver = webdriver.Firefox(options=firefox_args)
    driver.get(f"https://www.reddit.com/r/{args.subreddit}/comments/{post_id}/")
    time.sleep(5)
    driver.execute_script(
        f'document.getElementById("t3_{post_id}").style.maxWidth="{args.post_content_max_width}ch"'
    )
    driver.execute_script(
        f'document.getElementById("t3_{post_id}").parentElement.style.padding="3ch"'
    )
    if args.use_post:
        driver.execute_script(
            'for (const ele of document.getElementsByTagName("p")){\nele.style.display="none";\n}'
        )
    time.sleep(5)
    element = driver.find_element(By.ID, f"t3_{post_id}")
    element.screenshot("intro.png")
    driver.quit()
except:
    driver.quit()
    raise Exception("Selenium error! Quitting.")
intro = Image(filename="intro.png")
intro.resize(args.post_width, int((intro.height / intro.width) * args.post_width))
intro.crop(1, 2, intro.width - 2, intro.height - 2)

with Image(width=intro.width,
            height=intro.height,
            background=Color("transparent")) as mask:

    with Drawing() as ctx:
        ctx.fill_color = Color("white")
        ctx.rectangle(left=0,
                        top=0,
                        width=mask.width,
                        height=mask.height,
                        radius=mask.width*0.01)  # 10% rounding?
        ctx(mask)
    intro.composite_channel("alpha", mask, "dst_in")

intro.save(filename="intro.png")

# Generate TTS and subtitles
ttsmaker_query(
    selected_post, "voice1.mp3", token=args.ttsmaker_token, voice_id=147, speed=1.2, volume=1.3
)
ttsmaker_query(
    selected_comment,
    "voice2.mp3",
    token=args.ttsmaker_token,
    voice_id=147,
    speed=1.2,
    volume=1.3
)
subs_ai = SubsAI()
model = subs_ai.create_model("linto-ai/whisper-timestamped", {"segment_type": "word"})
subs = subs_ai.transcribe("voice2.mp3", model)
srt = [
    [(float(sub.start) / 1000, float(sub.end) / 1000), sub.text] for sub in subs.events
]

# Load video assets
img = ImageClip("intro.png")
voice1 = AudioFileClip("voice1.mp3")
voice2 = AudioFileClip("voice2.mp3")
video = VideoFileClip(args.background)
for i in range(1, len(srt)):
    srt[i - 1][0] = (srt[i - 1][0][0], srt[i][0][0])
merged_srt = []
for i in range(0, len(srt), 3):
    merged_srt.append([(srt[i][0][0], srt[min(i + 2, len(srt) - 1)][0][1]), ""])
    for j in range(i, min(len(srt), i + 3)):
        merged_srt[-1][1] += " " + srt[j][1]
srt = merged_srt
srt = list(
    map(
        lambda t: [
            (t[0][0] + voice1.duration, t[0][1] + voice1.duration),
            textwrap.fill(t[1], width=args.subtitle_wrap_width),
        ],
        srt,
    )
)

subtitles = [
    TextClip(
        sub[1],
        font=args.subtitle_font,
        fontsize=args.subtitle_font_size,
        size=(video.w, video.h),
        color=args.subtitle_color,
        method="label",
    )
    .set_pos(("center", "center"))
    .set_start(sub[0][0])
    .set_end(sub[0][1])
    .resize(lambda t: max(0.5, min(1, 200 * (t - 0.075)**3 + 1)))
    for sub in srt
]

subtitles_stroked = [
    TextClip(
        sub[1],
        font=args.subtitle_font,
        fontsize=args.subtitle_font_size,
        size=(video.w, video.h),
        stroke_color=args.subtitle_outline_color,
        stroke_width=args.subtitle_outline_size,
        color=args.subtitle_color,
        method="label",
    )
    .set_pos(("center", "center"))
    .set_start(sub[0][0])
    .set_end(sub[0][1])
    .resize(lambda t: max(0.5, min(1, 200 * (t - 0.075)**3 + 1)))
    for sub in srt
]

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
if final_video.duration > 60 and not args.force_creation:
    raise Exception(
        "Quitting because video duration detected longer than 60 seconds! Use --force-creation to override this behavior."
    )

output = CompositeVideoClip(
    [
        final_video,
        img.set_duration(voice1.duration)
        .resize(lambda t: min(1, 200 * (t - 0.1)**3  + 1))
        .set_pos(("center", "center")),
    ]
    + subtitles_stroked
    + subtitles
)
output.write_videofile("output.mp4", fps=video.fps, codec="libx264", audio_codec="aac")

# Upload the video
if not args.only_video:
    upload = None
    firefox_args_2 = Options()
    firefox_args_2.add_argument("-width")
    firefox_args_2.add_argument("1920")
    firefox_args_2.add_argument("-height")
    firefox_args_2.add_argument("1080")
    if args.headless:
        firefox_args_2.add_argument("--headless")
    if args.firefox_profile is not None:
        upload = Upload(
            args.firefox_profile,
            headless=args.headless,
            timeout=10,
            options=firefox_args_2,
        )
    else:
        raise ValueError("Firefox profile is required for uploading!")
    was_uploaded, video_id = upload.upload(
        os.path.abspath("output.mp4"),
        title=args.title_before
        + selected_post[
            : min(
                len(selected_post), 100 - len(args.title_after) - len(args.title_before)
            )
        ]
        + args.title_after,
        tags=args.video_tags.split(),
        only_upload=False,
    )
    print(f"{video_id} has been uploaded to YouTube")
    upload.close()
