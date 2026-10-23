import typing
import pandas as pd
import cv2
import pytesseract
import re
import json
from abc import ABC, abstractmethod

ReceiptDataRow = typing.TypedDict('ReceiptDataRow', {
    "product": str,
    "cost": float,
    "discount": typing.Optional[float],
})


def to_float(value: str | None) -> float | None:
    """
    Converts a string to a float, replacing commas with dots.
    """
    return float(value.replace(',', '.').replace(' ', '')) if value is not None else None


def get_total_sum(receipt_text: str) -> float:
    """
    Extracts the total sum from the receipt text using regex
    """
    TOTAL_SUM_REGEX = r"^Suma\s+PLN\s+(?P<total>[\d,\s]+)$"
    total_sum_pattern = re.compile(TOTAL_SUM_REGEX, re.MULTILINE)
    total_sum_match = total_sum_pattern.search(receipt_text)
    return to_float(total_sum_match.group('total')) if total_sum_match else None


class ReceiptData:
    def __init__(self, products: list[ReceiptDataRow], total: float):
        self.products = products
        self.total = total

    def to_json(self) -> str:
        return json.dumps({
            "products": self.products,
            "total": self.total
        })

    def to_csv(self) -> str:
        return pd.DataFrame(self.products).to_csv(index=False, sep=';', encoding='utf-8-sig')


class ReceiptParser(ABC):
    def __init__(self, img_path: str):
        image = cv2.imread(img_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.text = pytesseract.image_to_string(gray, lang='pol')
        self.regex_pattern = None

    def parse_receipt(self) -> ReceiptData:
        """
        Parses the receipt text by regex to extract product names and all it's additional info        
        """
        products: list[ReceiptDataRow] = []
        if self.regex_pattern is None:
            raise NotImplementedError("Subclasses must define a regex pattern for parsing.")

        print(self.text)

        pattern = re.compile(self.regex_pattern, re.MULTILINE)
        for match in pattern.finditer(self.text):
            products.append(self._parse_regex_group(match.groupdict()))

        return ReceiptData(products=products, total=get_total_sum(self.text))

    @abstractmethod
    def _parse_regex_group(self, data: dict[str, str]) -> ReceiptDataRow:
        pass


class LidlReceiptParser(ReceiptParser):
    def __init__(self, img_path: str):
        super().__init__(img_path)
        self.regex_pattern = r"^(?P<product_name>.+)\n(?P<qty>[\d,]+)([*%kg\sx]+)(?P<unit_price>[\d\.,]+)\s(?P<total_price>[\d\.,]+)\s\S\n(\s?Lidl Plus kupon (?P<discount_coupon>-[\d,\.\s]+))?(\s?Lidl Plus voucher (?P<voucher_discount>-[\d,\s\.]+))?$"

    def _parse_regex_group(self, data: dict[str, str]) -> ReceiptDataRow:
        discount_coupon = to_float(data['discount_coupon']) if data['discount_coupon'] else None
        voucher_discount = to_float(data['voucher_discount']) if data['voucher_discount'] else None
        discount = 0.0

        if discount_coupon is not None:
            discount += discount_coupon
        if voucher_discount is not None:
            discount += voucher_discount

        return ReceiptDataRow({
            "product": data['product_name'],
            "cost": to_float(data['total_price']),
            "discount": discount if discount != 0.0 else None
        })


class BiedronkaReceiptParser(ReceiptParser):
    def __init__(self, pdf_path: str):
        import pdf2image as p2i
        images = p2i.convert_from_path(pdf_path)
        self.text = "\n".join([pytesseract.image_to_string(img, lang='pol') for img in images])
        self.regex_pattern = r"^(?P<name>.+?)\s+(?P<ptu>\S{1,3})\s+(?P<quantity>[\d,]+)x\s+(?P<unit_price>[\d,]+)\s+(?P<total_price>[\d,\s]+)(\nOpust (?P<discount>-[\d,\s]+)\n(?P<price_after_dicount>[\d,\s]+))?$"

    def _parse_regex_group(self, data: dict[str, str]) -> ReceiptDataRow:
        return ReceiptDataRow({
            "product": data['name'],
            "cost": to_float(data['total_price']),
            "discount": to_float(data['discount'])
        })