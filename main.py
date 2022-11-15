from fuzzywuzzy import process

docx_txt_filename = 'data/docx.txt'
pdf_txt_filename = 'data/pdf.txt'
docx_pdf_txt_filename = 'data/docx_pdf.txt'


def clean_special_chars(lst):
    lst = [s.replace(u"\u202F", " ") for s in lst]
    return lst

def get_paragraph_starts(docx_text, pdf_text):
    index = 0
    p_starts = set()
    for dl in docx_text:
        if len(dl) < 3:
            continue
        i = min(70, len(dl))
        prefix = dl[:i]
        pls = process.extract(prefix, pdf_text[index:], limit=1)
        pl = pls[0][0]
        index = pdf_text.index(pl)
        p_starts.add(index)
    return sorted(p_starts)


def format_paragraphs(docx_text, pdf_text):
    docx_text = clean_special_chars(docx_text)
    pdf_text = clean_special_chars(pdf_text)

    p_starts = get_paragraph_starts(docx_text, pdf_text)

    paragraphs = list()
    current_paragraph = ''
    for i, pl in enumerate(pdf_text):
        if i in p_starts:
            if current_paragraph:
                paragraphs.append(current_paragraph)
            current_paragraph = pl
        else:
            current_paragraph = current_paragraph.replace("\n", " ")
            current_paragraph += pl
    return "".join(paragraphs)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open(docx_txt_filename) as f:
        docx_text = f.readlines()
    with open(pdf_txt_filename) as f:
        pdf_text = f.readlines()

    paragraphs_text = format_paragraphs(docx_text, pdf_text)
    with open(docx_pdf_txt_filename, "w") as f:
        f.write(paragraphs_text)
    a = 1

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
