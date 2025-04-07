from downloader import Config, SECDataLoader
from preprocessor import DataCleaner
from extractor import FinancialDataExtractor
import os
import pandas as pd

def main():
    # Initialize configuration and SECDataLoader
    config = Config()
    sec_loader = SECDataLoader(config)
    
    # Download 10-K filings for AAPL
    form_type = "10-K"
    ticker = "AMZN"
    cutoff = 9
    download_dir = sec_loader.download_sec_filing(form_type, ticker)
    print(f"Filings downloaded to: {download_dir}")

    # Create a DataFrame from the folder names and save it.
    downloaded_forms_df = sec_loader.get_downloaded_forms_df()
    final_dir = os.path.join("data", "final")
    os.makedirs(final_dir, exist_ok=True)
    forms_csv_path = os.path.join(final_dir, "downloaded_forms.csv")
    downloaded_forms_df.to_csv(forms_csv_path, index=False)
    print(f"Downloaded forms information saved to: {forms_csv_path}")
    
    sec_loader.rename_and_copy_filings()
    
    # List downloaded filings (looking for full-submission.txt files)
    filing_files = sec_loader.list_downloaded_filings(ticker,form_type,cutoff)
    if not filing_files:
        print("No filings found in the downloaded directory.")
        return
    
    print(filing_files)

    
    # Initialize a list to collect DataFrames from each filing.
    final_dataframes = []

    # Instantiate the extractor once (if the API key/configuration is constant).
    extractor = FinancialDataExtractor()

    # Loop over each filing file in the list.
    for file_path in filing_files:
        # Derive a base file name (expected format: <TICKER>-10k-<year>.txt).
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"Processing filing: {file_path}")

        # Use DataCleaner to clean the filing file.
        cleaner = DataCleaner(file_path)
        clean_text = cleaner.get_clean_text()

        # Define a path to save the cleaned text.
        processed_dir = os.path.join("data", "processed")
        os.makedirs(processed_dir, exist_ok=True)
        cleaned_file_path = os.path.join(processed_dir, f"{file_name}.txt")
        with open(cleaned_file_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        print(f"Cleaned text saved to: {cleaned_file_path}")

        # Set the query.
        query = "Consolidated Balance Sheets"

        # Extract financial data from the cleaned file.
        json_response = extractor.extract_from_file(cleaned_file_path, query)
        if json_response:
            print("Generated JSON Response Successfully")
        else:
            print("No JSON response generated; skipping file.")
            continue

        # Process the JSON response into a flattened DataFrame.
        try:
            df = extractor.process_and_flatten(json_response)
            # Reset index to make "Statement", "Year", and "Item" available as columns.
            df = df.reset_index()
            print("\nFlattened DataFrame:")
            print(df.head())

            # Extract ticker and file year from the file name.
            # Expected file name format: <TICKER>-10k-<year>.txt
            parts = file_name.split('-')
            if len(parts) >= 3:
                ticker = parts[0]
                file_year = parts[2]
            else:
                ticker = ""
                file_year = ""

            # Add the ticker and file_year as new columns.
            df['ticker'] = ticker
            df['file_year'] = file_year

            # Append this DataFrame to our list.
            final_dataframes.append(df)
        except Exception as e:
            print("Error processing JSON response:", e)

    # Combine all processed DataFrames into one and save as a single CSV file.
    if final_dataframes:
        final_df = pd.concat(final_dataframes, ignore_index=True)
        final_dir = os.path.join("data", "final")
        os.makedirs(final_dir, exist_ok=True)
        final_csv_path = os.path.join(final_dir, f"{ticker}extracted.csv")
        final_df.to_csv(final_csv_path, index=False)
        print("\nSaved Combined Flattened DataFrame to:", final_csv_path)
    else:
        print("No data frames were processed.")

if __name__ == "__main__":
    main()
