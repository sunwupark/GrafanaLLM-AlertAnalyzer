"""
Text Util
"""

import re


def extract_analysis_sections(content):
    sections = {"problem": "", "cause": "", "solution": ""}

    lines = content.split("\n")
    current_section = None

    for line in lines:
        line = line.strip()

        if line.lower().startswith("problem:"):
            current_section = "problem"
            sections["problem"] = line[8:].strip()
        elif line.lower().startswith("cause of problem:"):
            current_section = "cause"
            sections["cause"] = line[16:].strip()
        elif line.lower().startswith("solution:"):
            current_section = "solution"
            sections["solution"] = line[9:].strip()
        elif current_section and line:
            sections[current_section] += " " + line

    return sections


def clean_text(text):
    if text is None:
        return ""
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
