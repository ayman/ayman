# A GitHub About Page Builder remixed from
# https://github.com/simonw/simonw

import pathlib
import re
import feedparser


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


def make_md_from_feed(feed, thumbnail=False):
    mds = []
    template = "* [{title}]({url}) <br /> "
    template = template + "<span style='font-size:x-small;'>{published}</span>"
    template_img = "* <div style='padding: 2px; clear: both;'>"
    template_img = template_img + "<img alt='thumbnail' src='{thumbnail}' "
    template_img = template_img + "width='128' align='left' />"
    template_img = template_img + template[1:] + "</div>"
    for post in feed:
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
    twitter_feed = "https://rss.app/feeds/DnnmfppORazecplN.xml"
    youtube_feed = "https://www.youtube.com/feeds/videos.xml?channel_id=UCLwPj90ORTlgIo4Qrnt5N1w"

    medium_md = make_md_from_feed(fetch_feed_entries(medium_feed)[:5])
    twitter_md = make_md_from_feed(fetch_feed_entries(twitter_feed)[:5])
    youtube_md = make_md_from_feed(fetch_feed_entries(youtube_feed)[:3], True)
    readme_new = readme.open().read()
    readme_new = replace_chunk(readme_new, "medium", medium_md)
    readme_new = replace_chunk(readme_new, "twitter", twitter_md)
    readme_new = replace_chunk(readme_new, "youtube", youtube_md)

    readme.open("w").write(readme_new)
