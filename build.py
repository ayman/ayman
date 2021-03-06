# A GitHub About Page Builder remixed from
# https://github.com/simonw/simonw

import pathlib
import re
import feedparser
from datetime import datetime


def fetch_feed_entries(url):
    entries = feedparser.parse(url)["entries"]
    outputs = []
    for entry in entries:
        output = {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"]
        }

        if "media_thumbnail" in entry:
            output["thumbnail"] = entry["media_thumbnail"][0]["url"]
        outputs.append(output)
    return outputs


def make_md_from_feed(feed, date_format="", thumbnail=False):
    mds = []
    template = "%s %s" % ("<p><sub>{published}</sub> <br />",
                          "<a href='{url}'>{title}</a> </p>")
    template_img = "%s %s %s %s %s" % (
        "<div style='clear: both;'>",
        "<p><img alt='thumbnail' src='{thumbnail}' ",
        "width='72' align='left' />",
        "<sub>{published}</sub><br />",
        "<a href='{url}'>{title}</a></p></div>")
    for post in feed:
        if date_format != "":
            post['published'] = datetime.strptime(post['published'],
                                                  date_format)
        if thumbnail:
            mds.append(template_img.format(**post))
        else:
            mds.append(template.format(**post))
    return "\n".join(mds)


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {marker} starts \-\->.*<!\-\- {marker} ends \-\->".format(
            marker=marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    template_chunk = "<!-- {marker} starts -->{chunk}<!-- {marker} ends -->"
    chunk = template_chunk.format(marker=marker, chunk=chunk)
    return r.sub(chunk, content)


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()
    readme = root / "README.md"
    medium_feed = "https://medium.com/feed/@ayman"
    youtube_feed = "https://www.youtube.com/feeds/videos.xml?channel_id=UCLwPj90ORTlgIo4Qrnt5N1w"

    medium_md = make_md_from_feed(fetch_feed_entries(medium_feed)[:4],
                                  "%a, %d %b %Y %H:%M:%S %Z")
    youtube_md = make_md_from_feed(fetch_feed_entries(youtube_feed)[:3],
                                   "%Y-%m-%dT%H:%M:%S+00:00",
                                   True)
    readme_new = readme.open().read()
    readme_new = replace_chunk(readme_new, "medium", medium_md)
    readme_new = replace_chunk(readme_new, "youtube", youtube_md)

    readme.open("w").write(readme_new)
