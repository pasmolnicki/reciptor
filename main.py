import typing
from receipt_parser import ReceiptData
from program_options import parse_args, parse_receipt


def save_output(data: ReceiptData, output_format: str, output_file: typing.Optional[str]):
    if output_format == 'json':
        output_data = data.to_json()
    elif output_format == 'csv':
        output_data = data.to_csv()
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_data)
    else:
        import json
        if output_format == 'json':
            print(json.dumps(vars(data), indent=4, ensure_ascii=False))
        else:
            print(output_data)

def main():
    args = parse_args()
    receipt_data = parse_receipt(args)
    save_output(receipt_data, args.output_format, args.output_file)


if __name__ == "__main__":
    main()