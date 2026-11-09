def paragraphs(text):
    return [paragraph for paragraph in (line.strip() for line in text.split("\n")) if paragraph]
