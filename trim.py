import re
from pathlib import Path
from urllib.parse import urljoin
import logging

import yaml
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Tags that never hold job data. Cheaper to delete than to send to the LLM.
DROP = ["script", "style", "noscript", "svg", "head", "nav", "footer"]


def trim(html: str, base_url: str):
    name = html.split('/')[-1].split('.')[0]
    soup = BeautifulSoup(Path(html).read_text(encoding="utf-8"), "html.parser")
    for tag in soup(DROP):
        tag.decompose()

    # Put the absolute URL right after the link text: "Data Engineer [https://...]"
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        a.append(f" [{urljoin(base_url, href)}]")

    text = soup.get_text(separator="\n")
    lines = (re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines())
    text = "\n".join(line for line in lines if line)
    (Path("probe_out") / f"{name}.txt").write_text(text, encoding="utf-8")


# if __name__ == "__main__":
#     companies = yaml.safe_load(Path("companies.yaml").read_text(encoding="utf-8"))
#     for c in companies:
#         slug = re.sub(r"\W+", "_", c["name"]).lower()
#         src = Path("probe_out") / f"{slug}.html"
#         html = src.read_text(encoding="utf-8")
#         text = trim(html, c["url"])
#         
#         links = text.count(" [http")
#         print(f"{c['name']:<22} html {len(html):>8} -> text {len(text):>7} chars "
#               f"(~{len(text)//4} tokens), {links} links")