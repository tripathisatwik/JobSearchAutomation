import re
from pathlib import Path
from urllib.parse import urljoin

import yaml
from bs4 import BeautifulSoup

# Tags that never hold job data. Cheaper to delete than to send to the LLM.
DROP = ["script", "style", "noscript", "svg", "head", "nav", "footer"]


def trim(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(DROP):
        tag.decompose()  # remove the tag and everything inside it

    # Put the absolute URL right after the link text: "Data Engineer [https://...]"
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        a.append(f" [{urljoin(base_url, href)}]")

    text = soup.get_text(separator="\n")
    lines = (re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)  # drop blank lines


if __name__ == "__main__":
    companies = yaml.safe_load(Path("companies.yaml").read_text(encoding="utf-8"))
    for c in companies:
        slug = re.sub(r"\W+", "_", c["name"]).lower()
        src = Path("probe_out") / f"{slug}.html"
        html = src.read_text(encoding="utf-8")
        text = trim(html, c["url"])
        (Path("probe_out") / f"{slug}.txt").write_text(text, encoding="utf-8")
        links = text.count(" [http")
        print(f"{c['name']:<22} html {len(html):>8} -> text {len(text):>7} chars "
              f"(~{len(text)//4} tokens), {links} links")