# Description
- a website to review my youtube videos to learn how to improve

# Models
## StarRating
### Description
simple review for stars

### Variables
int stars;
const out_of_stars = 10

## Review
### Description
reviews

### Variables
- Str filming_review
- StarRating filming_rating
- const filming_description

- Str storytelling_review
- StarRating storytelling_rating
- const storytelling_description

- Str hook_review
- StarRating hook_rating
- const hook_description

- Str theme_review
- StarRating theme_rating
- const theme_description

- Str pacing_review
- StarRating pacing_rating
- const pacing_description

## yt_video
### Description
- each youtube video

### Variables
- StarRating star_review
- Str video_id
- Review review


# plan
## Step 1
read main.py and look how to use googleapiclient and the youtube api

## Step 2
- grab 10 videos using the CHANNEL_ID constant put them on a website as cards and when you click on them you go to the page and it displays the video

## Step 3
- make this save unique videos video_id and keep those videos up and use the api to go through a channel 50 videos at a time to enumerate videos and stop when you hit old videos

## Step 4 
now can you add analytics like likes views etc and seperate shorts and horizontal videos