import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict

def get_paragraph_formatting(paragraph):
    """
    Retrieve the formatting of a given paragraph.

    Parameters
    ----------
    paragraph : docx.text.paragraph.Paragraph
        The paragraph to analyze.

    Returns
    -------
    dict
        A dictionary containing formatting details of the paragraph.
    """
    formatting = {}

    if paragraph.runs:
        run = paragraph.runs[0]

        formatting['font_name'] = run.font.name
        formatting['font_size'] = run.font.size.pt if run.font.size else None
        formatting['bold'] = run.font.bold
        formatting['italic'] = run.font.italic
        formatting['underline'] = run.font.underline

    formatting['alignment'] = paragraph.alignment
    if formatting['alignment'] == WD_ALIGN_PARAGRAPH.LEFT:
        formatting['alignment'] = 'LEFT'
    elif formatting['alignment'] == WD_ALIGN_PARAGRAPH.CENTER:
        formatting['alignment'] = 'CENTER'
    elif formatting['alignment'] == WD_ALIGN_PARAGRAPH.RIGHT:
        formatting['alignment'] = 'RIGHT'
    elif formatting['alignment'] == WD_ALIGN_PARAGRAPH.JUSTIFY:
        formatting['alignment'] = 'JUSTIFY'
    else:
        formatting['alignment'] = 'NONE'

    formatting['style'] = paragraph.style.name

    return formatting


def analyze_docx(file_path):
    """
    Analyze the DOCX document and print formatting settings for each paragraph.

    Parameters
    ----------
    file_path : str
        The path to the DOCX file.
    """
    doc = docx.Document(file_path)

    for i, paragraph in enumerate(doc.paragraphs):
        formatting = get_paragraph_formatting(paragraph)
        print(f"Paragraph {i + 1}:")
        for key, value in formatting.items():
            print(f"  {key}: {value}")
        print("\n")

analyze_docx("C:\\Users\\Przemyslaw_Tutur\\PycharmProjects\\dataAnalysis\\PT.docx")
