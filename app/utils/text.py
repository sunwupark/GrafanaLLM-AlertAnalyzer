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

def format_html_text(text):
    """포맷팅된 HTML 텍스트로 변환하되 줄바꿈은 보존합니다."""
    if text is None:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)
    
    # 번호 목록 형식 확인 및 변환
    if re.search(r'\d+\.\s', text):
        # 번호 목록을 HTML 리스트로 변환
        lines = text.split("\n")
        formatted_lines = []
        
        for line in lines:
            # 숫자로 시작하는 줄인지 확인
            if re.match(r'^\d+\.\s', line.strip()):
                formatted_lines.append(f"<li>{line.strip()}</li>")
            else:
                formatted_lines.append(line)
        
        # 리스트 항목들이 있으면 ol 태그로 감싸기
        if any("<li>" in line for line in formatted_lines):
            text = "<ol>" + "".join(formatted_lines) + "</ol>"
        else:
            text = "<p>" + "<br>".join(formatted_lines) + "</p>"
    else:
        # 일반 텍스트는 줄바꿈만 HTML 줄바꿈으로 변환
        text = text.replace("\n", "<br>")
    
    return text.strip()