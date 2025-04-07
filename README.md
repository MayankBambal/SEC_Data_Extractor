# 10K Data Extractor
This project is designed to download, preprocess, and extract financial data from SEC filings (10-K forms) using a combination of Python modules and Google Generative AI (Gemini). The project downloads SEC filings, cleans the text content, and uses a generative AI model to extract structured financial data from the filings.

## Project Overview
### SEC Filings Downloader:
Uses the sec-edgar-downloader library to fetch company tickers and download 10-K filings from the SEC website.

### Preprocessor:
The DataCleaner class reads filing files, detects HTML content, and cleans them by removing unwanted tags and formatting to return plain text.

### Financial Data Extractor:
Utilizes Google Generative AI (Gemini) to process the cleaned text and extract key financial information in a structured JSON format. The extracted data can be further flattened into a pandas DataFrame for analysis.

### Main Script:
A sample main.py demonstrates how to combine these modules to download a filing, extract data, and convert it into a usable format.
