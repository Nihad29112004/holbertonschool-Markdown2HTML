#!/usr/bin/python3
"""
Markdown to HTML converter
"""
import sys
import os
import re
import hashlib


def parse_inline(text):
    """Handle inline formatting: bold, em, [[md5]], ((remove c))"""
    # Bold **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Emphasis __text__
    text = re.sub(r"__(.+?)__", r"<em>\1</em>", text)
    # [[text]] -> md5
    text = re.sub(r"\[\[(.+?)\]\]",
                  lambda m: hashlib.md5(m.group(1).encode()).hexdigest(),
                  text)
    # ((text)) -> remove c/C
    text = re.sub(r"\(\((.+?)\)\)",
                  lambda m: m.group(1).replace("c", "").replace("C", ""),
                  text)
    return text


def convert_markdown(lines):
    """Convert Markdown lines to HTML lines"""
    html = []
    in_ul = False
    in_ol = False
    in_p = False

    for line in lines:
        line = line.rstrip("\n")

        # Başlıqlar
        if line.startswith("#"):
            level = len(line.split(" ")[0])
            if 1 <= level <= 6:
                if in_p:
                    html.append("</p>")
                    in_p = False
                html.append(
                    f"<h{level}>{parse_inline(line[level:].strip())}</h{level}>")
                continue

        # Unordered list (- )
        if line.startswith("- "):
            if in_p:
                html.append("</p>")
                in_p = False
            if not in_ul:
                html.append("<ul>")
                in_ul = True
            html.append(f"<li>{parse_inline(line[2:].strip())}</li>")
            continue
        else:
            if in_ul:
                html.append("</ul>")
                in_ul = False

        # Ordered list (* )
        if line.startswith("* "):
            if in_p:
                html.append("</p>")
                in_p = False
            if not in_ol:
                html.append("<ol>")
                in_ol = True
            html.append(f"<li>{parse_inline(line[2:].strip())}</li>")
            continue
        else:
            if in_ol:
                html.append("</ol>")
                in_ol = False

        # Boş sətir -> paraqraf bağla
        if line.strip() == "":
            if in_p:
                html.append("</p>")
                in_p = False
            continue

        # Paraqraf
        if not in_p:
            html.append("<p>")
            html.append(parse_inline(line))
            in_p = True
        else:
            html.append("<br/>")
            html.append(parse_inline(line))

    # Açıq tag-ları bağla
    if in_ul:
        html.append("</ul>")
    if in_ol:
        html.append("</ol>")
    if in_p:
        html.append("</p>")

    return html


def main():
    """Main entry point"""
    if len(sys.argv) != 3:
        print("Usage: ./markdown2html.py README.md README.html",
              file=sys.stderr)
        sys.exit(1)

    infile, outfile = sys.argv[1], sys.argv[2]

    if not os.path.isfile(infile):
        print(f"Missing {infile}", file=sys.stderr)
        sys.exit(1)

    with open(infile, "r", encoding="utf-8") as f:
        lines = f.readlines()

    html_lines = convert_markdown(lines)

    with open(outfile, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    sys.exit(0)


if __name__ == "__main__":
    main()
