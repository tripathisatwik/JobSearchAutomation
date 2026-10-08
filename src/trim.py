from bs4 import BeautifulSoup

def trim_html(html: str, url: str = "") -> str:
    """
    Parses HTML content, removes boilerplate tags (scripts, styles, nav, footers),
    and returns a clean, trimmed text representation of the webpage.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Remove irrelevant or non-content elements
    for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form", "iframe"]):
        element.decompose()

    # Extract text with line breaks
    text = soup.get_text(separator="\n")

    # Clean whitespace and strip empty lines
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = []
    blank_count = 0
    for line in lines:
        if line:
            cleaned_lines.append(line)
            blank_count = 0
        elif blank_count < 1:
            cleaned_lines.append("")
            blank_count += 1

    return "\n".join(cleaned_lines).strip()
