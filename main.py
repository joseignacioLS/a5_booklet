import math

from pypdf import PdfWriter, PdfReader, PageObject


def get_ordered_indexes(total_pages, sheets_per_signature=1):
    indexes = []
    pages_per_signature = sheets_per_signature * 4
    number_of_signatures = math.ceil(total_pages / pages_per_signature)
    for signature_index in range(number_of_signatures):
        for side_index in range(sheets_per_signature * 2):
            base_index = signature_index * pages_per_signature
            even_modifier = sheets_per_signature * 4 - side_index - 1
            odd_modifier = side_index
            left_page = (base_index + (even_modifier if side_index % 2 == 0 else odd_modifier))
            right_page = (base_index + (odd_modifier if side_index % 2 == 0 else even_modifier))
            if left_page >= total_pages:
                left_page = None
            if right_page >= total_pages:
                right_page = None
            indexes += [
                left_page, right_page
            ]
    return indexes


def create_ordered_pdf(reference_pdf, ordered_indexes, page_size, page_layout, pdf_length):
    generated_pdf = PdfWriter()
    for i in range(0, len(ordered_indexes), 2):
        new_page = PageObject.create_blank_page(width=page_size[0], height=page_size[1])
        for delta_index, coords in enumerate(page_layout):
            index = i + delta_index
            if index >= len(ordered_indexes):
                continue
            if ordered_indexes[index] is None:
                continue
            if ordered_indexes[index] >= pdf_length:
                continue

            new_page.merge_translated_page(reference_pdf.pages[ordered_indexes[index]], coords[0], coords[1])

        generated_pdf.add_page(new_page)
    return generated_pdf


def make_booklet(input_file, sheets_per_signature=1):
    try:
        with open(input_file, 'rb') as readfile:
            input_pdf = PdfReader(readfile)

            page_width = input_pdf.pages[0].mediabox.width
            page_height = input_pdf.pages[0].mediabox.height
            page_layout = [[0, 0], [page_width, 0]]

            pdf_length = len(input_pdf.pages)
            ordered_indexes = get_ordered_indexes(pdf_length, sheets_per_signature)

            output_pdf = create_ordered_pdf(input_pdf, ordered_indexes, [page_width * 2, page_height], page_layout, pdf_length)

            output_file = input_file.replace(".pdf", "_print.pdf")
            with open(output_file, "wb") as writefile:
                output_pdf.write(writefile)
    except FileNotFoundError:
        print(f"File '{input_file}' not found")


if __name__ == "__main__":
    input_file = "input.pdf"
    make_booklet(input_file, 1)
