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


def check_blank_page_addition(total_pages, sheets_per_signature, sheets_limit=None):
    print("Arrangements")
    max_sheets_per_signature = sheets_limit or math.ceil(total_pages / 8)
    for i in range(1, max_sheets_per_signature):
        number_of_signatures, blank_pages = calculate_extra_blank_pages(total_pages, i)
        print(f"[{'*' if i == sheets_per_signature else ' '}] {i} sheets per signature\t{4 * i} pages per signature"
              f"\t {number_of_signatures} total signatures"
              f"\t{blank_pages} extra blank pages")
    if sheets_per_signature >= max_sheets_per_signature:
        number_of_signatures, blank_pages = calculate_extra_blank_pages(total_pages, sheets_per_signature)
        print(f"[*] {sheets_per_signature} sheets per signature\t{4 * sheets_per_signature} pages per signature"
              f"\t {number_of_signatures} total signatures"
              f"\t{blank_pages} extra blank pages")


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

            check_blank_page_addition(total_pages, 0, int(total_pages / 2))

    except FileNotFoundError:
        print(f"File '{input_file}' not found")


def decode_args(args):
    res = {}
    for key, value in [arg.split("=") for arg in args]:
        res[key] = value
    return res


def handle_args(args):
    try:
        mode = args["-mode"]
        if mode not in ["make", "test", "help"]:
            raise ValueError
    except ValueError:
        mode = "help"
        print("Available modes: make, test or help\n")
    except KeyError:
        mode = "help"

    try:
        input_file = args["-file"]
    except KeyError:
        print("Missing file name argument\n")
        input_file = ""
        mode = "help"

    try:
        input_sheets_per_signature = int(args["-s"])
        sheets_per_signature = max(input_sheets_per_signature, 1)
    except KeyError:
        sheets_per_signature = 1
    except ValueError:
        print("Number of sheets per signature should be a number\n")
        mode = "help"

    return input_file, mode, sheets_per_signature


if __name__ == "__main__":
    args = decode_args(sys.argv[1:])

    input_file, mode, sheets_per_signature = handle_args(args)

    if mode == "make":
        make_booklet(
            input_file,
            sheets_per_signature
        )
    elif mode == "test":
        test_booklet(
            input_file
        )
    elif mode == "help":
        print(f"-mode=<'make'|'test'>\n"
              f"  make: produce booklet\n"
              f"  test: check number of signatures based on sheets per signature\n"
              f"\n"
              f"-file=<path>\n"
              f"  path to the file\n"
              f"\n"
              f"-s=<number>\n"
              f"  number of sheets per signature")

