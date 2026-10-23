import typing
import argparse
from receipt_parser import ReceiptData, LidlReceiptParser, BiedronkaReceiptParser

class ProgramOptions:
    OUTPUT_FORMATS = ('json', 'csv')
    STORES = ('lidl', 'biedronka')
    RECEIPT_PARSER_KINDS = {
        "lidl": LidlReceiptParser,
        "biedronka": BiedronkaReceiptParser
    }

    store: str
    file_path: str
    output_format: str
    output_file: typing.Optional[str] = None


    def __init__(self, store: str, file_path: str, output_format: str, output_file: typing.Optional[str] = None, **kwargs):
        self.store = store
        self.file_path = file_path
        self.output_format = output_format
        self.output_file = output_file
        self._validate()


    def _validate(self):
        if self.store not in self.RECEIPT_PARSER_KINDS:
            raise ValueError(f"Unsupported store: {self.store}. Supported stores are: {list(self.RECEIPT_PARSER_KINDS.keys())}")
        if self.output_format not in self.OUTPUT_FORMATS:
            raise ValueError(f"Unsupported output format: {self.output_format}. Supported formats are: {self.OUTPUT_FORMATS}")
        if self.file_path is None:
            raise ValueError("File path must be provided.")

    @staticmethod
    def build_arg_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Parse receipts from images or PDFs.")
        parser.add_argument('file_path', type=str, help='Path to the receipt image or PDF file.')
        parser.add_argument('--store', '-s', type=str, choices=ProgramOptions.STORES, required=True, help='Store name (lidl or biedronka).')
        parser.add_argument('--output-format', '-f', type=str, choices=ProgramOptions.OUTPUT_FORMATS, default='json', help='Output format (json or csv).')
        parser.add_argument('--output-file', '-o', type=str, default=None, help='Output file path. If omitted, output will be printed to stdout.')
        return parser


def parse_args() -> ProgramOptions:
    parser = ProgramOptions.build_arg_parser()
    args = parser.parse_args()

    if args.store == 'lidl':
        assert args.file_path.lower().endswith('.png'), "Lidl receipts must be in PNG format."
    elif args.store == 'biedronka':
        assert args.file_path.lower().endswith('.pdf'), "Biedronka receipts must be in PDF format."

    return ProgramOptions(**vars(args)) 


def parse_receipt(options: ProgramOptions) -> ReceiptData:
    return ProgramOptions.RECEIPT_PARSER_KINDS[options.store](options.file_path).parse_receipt()