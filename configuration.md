# redditttsbot Configuration

### Usage
**python main.py** --background _BACKGROUND_ ...

### Additional Flags
* **-h**, **--help**  
  Show help message
* **--background** _BACKGROUND_  
  Required flag, sets the video to be used for the background
* **--subreddit** _SUBREDDIT_  
  Select subreddit to scrape from. Default is `askreddit`.
* **--min-len** _MIN\_LEN_  
  Select minimum length for content, in characters. Default is `600`.
* **--len-range** _LEN\_RANGE_  
    Number of characters creater than _MIN\_LEN_ the content may be, in characters. Default is `300`.
* **--use-post**  
    Enabling this flag uses the post for content, instead of a random comment.
* **--subtitle-wrap-width** _SUBTITLE\_WRAP\_WIDTH_  
    Choose the number of characters the subtitles will wrap at. Default is `30`.
* **--subtitle-font** _SUBTITLE\_FONT_  
    Choose the font of the subtitles. Default is `"Arial"`
* **--subtitle-font-size** _SUBTITLE\_FONT\_SIZE_  
    Choose the font size of the subtitles. Default is `60`.
* **--subtitle-length** _SUBTITLE\_SPLIT\_LENGTH_  
    Decide the length at which to split to the next subtitle. Default is `80`.
* **--post-pool-size** _POST\_POOL\_SIZE_  
    Set the number of top posts from which the final post is chosen. Default is `20`.
* **--comment-pool-size** _COMMENT\_POOL\_SIZE_  
    Set the number of top comments from which the top comment is chosen. Default is `40`.
* **--post-time-span** _POST\_TIME\_SPAN_
    Set the time span from which the top _POST\_POOL\_SIZE_ posts are chosen. Default is `"week"`.
* **--firefox-profile** _FIREFOX\_PROFILE_  
    Select a Firefox profile to use instead of the default one.
* **--subtitle-outline-size** _SUBTITLE\_OUTLINE\_SIZE_  
    Set the outline size of the subtitles. Default is `14`.
* **--random-cutout**  
    Enabling this flag takes a random portion of the background footage, rather than beginning at the start and truncating anything past the content.
* **--headless**  
    Enable this to hide browser GUI when taking the post screenshot.
* **--subtitle-color** _SUBTITLE\_COLOR_  
    Color for subtitles. Default is `"white"`.
* **--subtitle-outline-color** _SUBTITLE\_OUTLINE\_COLOR_  
    Set the outline color for subtitles. Default is `"black"`.
* **--post-width** _POST\_WIDTH_  
    Set the width in pixels for the post image. Default is `1000`.
* **--post-content-max-width** _POST\_CONTENT\_MAX\_WIDTH_  
    Set the max width of the post, in CSS `ch` units. Default is `60`.
* **--post-content-padding** _POST\_CONTENT\_PADDING_  
    Set the padding of the post, in CSS `ch` units. Default is `3`.
* **--only-video**  
    Only generate a video, do not upload it to YouTube.
* **--video-tags** _VIDEO\_TAGS_
    Space separated list of tags (without the hashtag)
* **--title-before** _TITLE\_BEFORE_  
    Text to prepend before the video title
* **--title-after** _TITLE\_AFTER_
    Text to append after the video title
