# reciptor
Receipt debt calculator


## Requirements

- `tesseract-ocr`: specifically tesseract-ocr-pol

Install on linux:

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-pol
```

## Run

You will need first a receipt, which can be downloaded through the store's app
Biedronka has `.pdf`, while Lidl exports them as `.png` files.

As arguments you have to specify the store, either 'lidl' or 'biedronka',
then pass the receipt file path

For example:

```bash
python3 --store biedronka ./biedronka-receipt.pdf
```

