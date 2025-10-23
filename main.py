from pypdf import PdfWriter, PdfReader, PageObject

output_pdf = PdfWriter()
input_file = "input.pdf"
output_file = input_file.replace(".pdf", "_print.pdf")


def get_ordered_indexes(total_pages):
    indexes = []
    for page in range(0, total_pages, 4):
        p1 = page + 3
        p2 = page
        p3 = page + 1
        p4 = page + 2
        for page_index in [p1, p2, p3, p4]:
            if page_index < total_pages:
                indexes.append(page_index)
            else:
                indexes.append(None)
    return indexes


with open(input_file, 'rb') as readfile:
    input_pdf = PdfReader(readfile)

    page_width = input_pdf.pages[0].mediabox.width
    page_height = input_pdf.pages[0].mediabox.height
    page_layout = [[0, 0], [page_width, 0]]

    pdf_length = len(input_pdf.pages)
    ordered_indexes = get_ordered_indexes(pdf_length)

    for i in range(0, len(ordered_indexes), 2):
        new_page = PageObject.create_blank_page(width=page_width * 2, height=page_height)
        for delta_index, coords in enumerate(page_layout):
            index = i + delta_index
            if index >= len(ordered_indexes):
                continue
            if ordered_indexes[index] is None:
                continue
            if ordered_indexes[index] >= pdf_length:
                continue

            new_page.merge_translated_page(input_pdf.pages[ordered_indexes[index]], coords[0], coords[1])

        output_pdf.add_page(new_page)

    with open(output_file, "wb") as writefile:
        output_pdf.write(writefile)
