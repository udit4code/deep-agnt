def paragraphs(text):
    return [paragraph.strip() for paragraph in text.split("\n") if len(paragraph.strip()) > 0]
