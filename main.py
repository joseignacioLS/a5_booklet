from user_input import decode_args, handle_args, handle_modes


if __name__ == "__main__":
    args = decode_args()

    input_file, mode, sheets_per_signature = handle_args(args)

    handle_modes(input_file, mode, sheets_per_signature)
