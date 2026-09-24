# OCR utilities for scanned/image-based PDFs
# Handles preprocessing, OCR extraction, line grouping, block grouping,
# header detection, and section grouping.

import cv2
import numpy as np
import pytesseract


def preprocessing(image):
    """Apply basic preprocessing before OCR."""
    image_array = image.copy()

    image_array = cv2.detailEnhance(
        image_array,
        sigma_s=10,
        sigma_r=0.10
    )

    image_array = cv2.resize(
        image_array,
        None,
        fx=1.5,
        fy=1.5,
        interpolation=cv2.INTER_LANCZOS4
    )

    gray_image = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2GRAY
    )

    return gray_image


def get_text(image) -> str:
    """Extract OCR text from a preprocessed image."""
    processed_image = preprocessing(image)
    return pytesseract.image_to_string(processed_image)


def get_data(image) -> list:
    """
    Run the full OCR structure pipeline.

    Returns:
        list: Structured sections built from OCR word data.
    """
    processed_image = preprocessing(image)
    data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)

    words = []

    # Extract valid word-level OCR entries
    for i in range(len(data["level"])):
        if (
            data["level"][i] == 5
            and int(data["conf"][i]) > 0
            and data["text"][i].strip()
        ):
            words.append({
                "text": data["text"][i].strip(),
                "x": data["left"][i],
                "y": data["top"][i],
                "width": data["width"][i],
                "height": data["height"][i],
                "conf": int(data["conf"][i]),
            })

    # Pipeline: words -> lines -> blocks -> labeled blocks -> sections
    lines = group_words_into_lines(words)
    blocks = group_lines_into_blocks(lines)
    blocks = label_blocks_with_headers(blocks)
    sections = group_blocks_into_sections(blocks)

    return sections


def build_line(words_in_line: list) -> dict:
    """Build a line object from grouped OCR words."""
    words_in_line = sorted(words_in_line, key=lambda word: word["x"])
    text = " ".join(word["text"] for word in words_in_line)

    min_x = min(word["x"] for word in words_in_line)
    min_y = min(word["y"] for word in words_in_line)
    max_x = max(word["x"] + word["width"] for word in words_in_line)
    max_y = max(word["y"] + word["height"] for word in words_in_line)

    return {
        "text": text,
        "words": words_in_line,
        "x": min_x,
        "y": min_y,
        "width": max_x - min_x,
        "height": max_y - min_y,
    }


def group_words_into_lines(words: list, threshold: int = 12) -> list:
    """Group OCR words into lines using vertical proximity."""
    if not words:
        return []

    # Sort top-to-bottom, then left-to-right
    words = sorted(words, key=lambda word: (word["y"], word["x"]))

    lines = []
    current_line = [words[0]]
    current_y = words[0]["y"]

    for word in words[1:]:
        # Same line if vertical distance is small enough
        if abs(word["y"] - current_y) <= threshold:
            current_line.append(word)
        else:
            lines.append(build_line(current_line))
            current_line = [word]
            current_y = word["y"]

    lines.append(build_line(current_line))
    return lines


def build_block(lines_in_block: list) -> dict:
    """Build a block object from grouped lines."""
    block_text = "\n".join(line["text"] for line in lines_in_block)

    min_x = min(line["x"] for line in lines_in_block)
    min_y = min(line["y"] for line in lines_in_block)
    max_x = max(line["x"] + line["width"] for line in lines_in_block)
    max_y = max(line["y"] + line["height"] for line in lines_in_block)

    return {
        "text": block_text,
        "lines": lines_in_block,
        "x": min_x,
        "y": min_y,
        "width": max_x - min_x,
        "height": max_y - min_y,
    }


def group_lines_into_blocks(lines: list, gap_multiplier: float = 0.3) -> list:
    """
    Group lines into blocks using vertical spacing.

    A new block starts when:
    - the next line looks like a header, or
    - the vertical gap is too large
    """
    if not lines:
        return []

    lines = sorted(lines, key=lambda line: line["y"])

    blocks = []
    current_block = [lines[0]]

    for line in lines[1:]:
        previous_line = current_block[-1]
        gap = line["y"] - (previous_line["y"] + previous_line["height"])

        # Force a new block if the line looks like a header
        if is_header_line(line, previous_line=previous_line, is_first_in_block=True):
            blocks.append(build_block(current_block))
            current_block = [line]

        # Keep grouping when spacing is small
        elif gap <= previous_line["height"] * gap_multiplier:
            current_block.append(line)

        # Otherwise start a new block
        else:
            blocks.append(build_block(current_block))
            current_block = [line]

    blocks.append(build_block(current_block))
    return blocks


def is_header_line(line: dict, previous_line=None, is_first_in_block: bool = False) -> bool:
    """
    Score whether a line looks like a section header.

    Signals used:
    - short text
    - uppercase letters
    - punctuation
    - spacing above
    - first line in block
    """
    text = line["text"].strip()
    letters = [char for char in text if char.isalpha()]
    words = text.split()
    word_count = len(words)
    score = 0

    # Detect title-case patterns like names or short phrases
    is_title_case = all(word[0].isupper() for word in words if word)

    # Short lines are more likely to be headers
    if word_count == 2 and is_title_case:
        score -= 1
    elif word_count <= 3:
        score += 1
    else:
        score -= 1

    # Commas often indicate content, not headers
    if "," in text:
        score -= 1

    # Very short OCR fragments are unlikely to be real headers
    if len(text) < 5:
        score -= 2

    # Long text is less likely to be a header
    if len(text) > 40:
        score -= 1

    # All-uppercase alphabetic text is a strong header signal
    if letters and all(char.isupper() for char in letters):
        score += 2

    # Headers are less likely to end like sentences
    if not text.endswith((",", ";", ".")):
        score += 1
    elif text.endswith("."):
        score -= 1

    # A larger gap above can indicate a new section
    if previous_line is not None:
        gap = line["y"] - (previous_line["y"] + previous_line["height"])
        if gap > previous_line["height"] * 0.8:
            score += 1

    # First line in a block is more likely to be a header
    if is_first_in_block:
        score += 1

    return score >= 3


def label_blocks_with_headers(blocks: list) -> list:
    """Attach header metadata to each block based on its first line."""
    for i, block in enumerate(blocks):
        first_line = block["lines"][0]
        previous_line = None

        if i > 0:
            previous_line = blocks[i - 1]["lines"][-1]

        is_header = is_header_line(
            first_line,
            previous_line=previous_line,
            is_first_in_block=True,
        )

        block["is_header"] = is_header
        block["header_text"] = first_line["text"] if is_header else None

    return blocks


def group_blocks_into_sections(blocks: list) -> list:
    """Group blocks into sections using header blocks as section starts."""
    sections = []
    current_section = None

    for block in blocks:
        if block["is_header"]:
            if current_section is not None:
                section_text = "\n".join(
                    block["text"] for block in current_section["blocks"]
                )
                current_section["text"] = section_text
                sections.append(current_section)

            current_section = {
                "header": block["header_text"],
                "blocks": [block],
            }

        else:
            if current_section is None:
                current_section = {
                    "header": "UNLABELED",
                    "blocks": [block],
                }
            else:
                current_section["blocks"].append(block)

    if current_section is not None:
        section_text = "\n".join(
            block["text"] for block in current_section["blocks"]
        )
        current_section["text"] = section_text
        sections.append(current_section)

    return sections


def print_blocks(blocks: list) -> None:
    """Debug helper: print block previews."""
    for block in blocks:
        print("BLOCK:")
        print(block["text"][:100])
        print("-" * 20)


def print_sections(sections: list) -> None:
    """Debug helper: print section text."""
    for section in sections:
        print("SECTION:", section["header"])
        print(section["text"])
        print("-" * 40)