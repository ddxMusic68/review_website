from flask import Blueprint, redirect, render_template, request, url_for

from .db import get_all_videos, get_saved_videos, get_video, save_video
from .models import OUT_OF_STARS, Review, StarRating, YtVideo
from .youtube_api import parse_duration, refresh_stats, sync_videos

views = Blueprint("views", __name__)

SORT_KEYS = {"views", "likes", "comments", "duration", "uploaded"}


def sort_key(video, sort):
    if sort == "duration":
        return parse_duration(video.get("duration") or "")
    if sort == "uploaded":
        return video.get("published_at") or ""
    return video.get(sort) or 0


@views.route("/")
def home():
    sync_videos()
    refresh_stats()
    sort = request.args.get("sort", "uploaded")
    if sort not in SORT_KEYS:
        sort = "uploaded"
    direction = request.args.get("dir", "desc")
    if direction not in ("asc", "desc"):
        direction = "desc"
    reverse = direction == "desc"

    videos = get_saved_videos()
    saved_ratings = dict(get_all_videos())
    for video in videos:
        video["stars"] = saved_ratings.get(video["video_id"])
        video["is_short"] = bool(video["is_short"])
    horizontal = [v for v in videos if not v["is_short"]]
    shorts = [v for v in videos if v["is_short"]]
    horizontal.sort(key=lambda v: sort_key(v, sort), reverse=reverse)
    shorts.sort(key=lambda v: sort_key(v, sort), reverse=reverse)
    return render_template(
        "home.html",
        videos=horizontal,
        shorts=shorts,
        sort=sort,
        direction=direction,
    )


@views.route("/video/<video_id>")
def video(video_id):
    existing = get_video(video_id) or YtVideo(video_id=video_id)
    return render_template(
        "video.html",
        video=existing,
        out_of_stars=OUT_OF_STARS,
    )


@views.route("/video/<video_id>/submit", methods=["POST"])
def submit_review(video_id):
    video = YtVideo(
        video_id=video_id,
        star_review=StarRating(stars=int(request.form["overall_stars"])),
        review=Review.default(),
    )
    for category in video.review.categories.values():
        category.review = request.form[f"{category.name}_review"]
        category.rating = StarRating(
            stars=int(request.form[f"{category.name}_stars"])
        )
    save_video(video)
    return redirect(url_for("views.video", video_id=video_id))