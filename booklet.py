import math
import sys

from pypdf import PdfWriter, PdfReader, PageObject
from pypdf.errors import PdfStreamError


def get_sheet_side_indexes(
        base_index,
        side_index,
        sheets_per_signature,
        total_pages
):
    even_modifier = sheets_per_signature * 4 - side_index - 1
    odd_modifier = side_index
    left_page = (base_index + (even_modifier if side_index % 2 == 0 else odd_modifier))
    right_page = (base_index + (odd_modifier if side_index % 2 == 0 else even_modifier))
    if left_page >= total_pages:
        left_page = None
    if right_page >= total_pages:
        right_page = None
    return [left_page, right_page]


def get_signature_indexes(
        signature_index,
        sheets_per_signature,
        pages_per_signature,
        total_pages
):
    signature_indexes = []
    base_index = signature_index * pages_per_signature
    for side_index in range(sheets_per_signature * 2):
        signature_indexes += get_sheet_side_indexes(
            base_index,
            side_index,
            sheets_per_signature,
            total_pages
        )
    return signature_indexes


def get_ordered_indexes(
        total_pages,
        sheets_per_signature=1
):
    indexes = []
    pages_per_signature = sheets_per_signature * 4
    number_of_signatures = math.ceil(total_pages / pages_per_signature)
    for signature_index in range(number_of_signatures):
        indexes += get_signature_indexes(
            signature_index,
            sheets_per_signature,
            pages_per_signature,
            total_pages
        )
    return indexes


def create_ordered_pdf(
        reference_pdf,
        ordered_pages,
        page_size,
        page_layout,
        total_pages
):
    generated_pdf = PdfWriter()
    for i in range(0, len(ordered_pages), 2):
        new_page = PageObject.create_blank_page(
            width=page_size[0],
            height=page_size[1]
        )
        for delta_index, coords in enumerate(page_layout):
            index = i + delta_index

            out_of_range_index = index >= len(ordered_pages)
            blank_page = not out_of_range_index and ordered_pages[index] is None
            out_of_range_page = not blank_page and ordered_pages[index] >= total_pages

            if out_of_range_page or blank_page or out_of_range_index:
                continue

            new_page.merge_translated_page(
                reference_pdf.pages[ordered_pages[index]],
                coords[0],
                coords[1]
            )

        generated_pdf.add_page(new_page)
    return generated_pdf


def calculate_extra_blank_pages(total_pages, sheets_per_signature):
    pages_per_signature = sheets_per_signature * 4
    number_of_signatures = math.ceil(total_pages / pages_per_signature)
    real_pages = number_of_signatures * sheets_per_signature * 4
    return number_of_signatures, real_pages - total_pages


def check_blank_page_addition(total_pages):
    print("Arrangements")
    res = {}
    sheets_per_signature = 1

    while sheets_per_signature < total_pages:
        number_of_signatures, blank_pages = calculate_extra_blank_pages(total_pages, sheets_per_signature)
        if number_of_signatures in res:
            if res[number_of_signatures][1] >= blank_pages:
                res[number_of_signatures] = [sheets_per_signature, blank_pages]
        else:
            res[number_of_signatures] = [sheets_per_signature, blank_pages]
        if number_of_signatures == 1:
            break
        sheets_per_signature += 1
    for entry in res:
        print(f"{res[entry][0]} sheets per signature\t{4 * res[entry][0]} pages per signature"
              f"\t {entry} total signatures"
              f"\t{res[entry][1]} extra blank pages")


def make_booklet(
        input_file,
        sheets_per_signature=1
):
    try:
        with open(input_file, 'rb') as readfile:
            try:
                input_pdf = PdfReader(readfile)
            except PdfStreamError:
                print("Invalid Input File")
                sys.exit()

            page_width = input_pdf.pages[0].mediabox.width
            page_height = input_pdf.pages[0].mediabox.height
            page_layout = [
                [
                    0,
                    0
                ],
                [
                    page_width,
                    0
                ]
            ]

            total_pages = len(input_pdf.pages)

            ordered_pages = get_ordered_indexes(
                total_pages,
                sheets_per_signature
            )

            output_pdf = create_ordered_pdf(
                input_pdf,
                ordered_pages,
                [
                    page_width * 2,
                    page_height
                ],
                page_layout,
                total_pages
            )

            output_file = input_file.replace(".pdf", "_print.pdf")

            with open(output_file, "wb") as writefile:
                output_pdf.write(writefile)

    except FileNotFoundError:
        print(f"File '{input_file}' not found")


def test_booklet(input_file):
    try:
        with open(input_file, 'rb') as readfile:
            try:
                input_pdf = PdfReader(readfile)
            except PdfStreamError:
                print("Invalid Input File")
                sys.exit()

            total_pages = len(input_pdf.pages)

            check_blank_page_addition(total_pages)

    except FileNotFoundError:
        print(f"File '{input_file}' not found")
