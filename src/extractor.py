import json
import pandas as pd
import google.generativeai as genai

class FinancialDataExtractor:
    def __init__(self):
        # Initialize the generative model (Gemini)
        genai.configure(api_key="")
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    def extract_from_file(self, file_path, query):
        """
        Reads the entire file content from the given file path, 
        builds a prompt with the provided query, and returns the generated answer.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            passage = f.read()
        
        # Convert multiline text to a one-line string for the prompt.
        passage_oneline = passage.replace("\n", " ")
        query_oneline = query.replace("\n", " ")
        
        prompt = f"""
                    You are trying to extract financial information from a document. This PASSAGE contains 10k statements for a company.

                    Extract the financial information related to the QUESTION and provide the output in a specific JSON format following these exact requirements:

                    1. The output must be valid, parseable JSON with no markdown code blocks
                    2. The top-level keys should be financial statement types (e.g., "Balance Sheet", "Income Statement")
                    3. Each statement type should contain year objects (e.g., "2023", "2022")
                    4. Each year should contain line items (e.g., "Revenue", "Net Income")
                    5. Each line item should be an object with the following required keys:
                    - "value": The numeric value (keep as string if it includes special formatting)
                    - "unit": The unit of measurement (e.g., "USD millions", "Billion", etc.)

                    Example structure:
                    {{
                    "Balance Sheet": {{
                        "2023": {{
                        "Total Assets": {{
                            "value": "100,000",
                            "unit": "million USD"
                        }},
                        "Total Liabilities": {{
                            "value": "45,000",
                            "unit": "thousand USD"
                        }}
                        }},
                        "2022": {{
                        "Total Assets": {{
                            "value": "90",
                            "unit": "billion USD"
                        }}
                        }}
                    }}
                    }}

                    Extract ALL relevant financial figures for ALL available years from the passage.
                    Ensure the output is ONLY valid JSON with no explanatory text, no markdown formatting, and no code block indicators.

                    QUESTION: {query_oneline}
                    PASSAGE: {passage_oneline}
                    """
        answer = self.model.generate_content(prompt)
        return answer.text

    def process_and_flatten(self, json_text):
        """
        Cleans the JSON text, converts it into a dictionary, and then
        flattens the nested JSON structure into a pandas DataFrame.
        """
        # Clean the text to ensure it's valid JSON
        lines = json_text.splitlines()
        json_lines = [line for line in lines if not line.startswith("```")]
        cleaned_text = "\n".join(json_lines).strip()

        # Convert the JSON string to a Python dictionary
        data = json.loads(cleaned_text)

        # Flatten the nested JSON structure
        flattened_data = []
        for statement, years in data.items():
            for year, items in years.items():
                for item, values in items.items():
                    row = {
                        'Statement': statement,
                        'Year': year,
                        'Item': item,
                        **values  # Unpacks the "value" and "unit" keys into the row
                    }
                    flattened_data.append(row)

        # Create and return a DataFrame
        df = pd.DataFrame(flattened_data)
        df = df.set_index(['Statement', 'Year', 'Item'])
        return df
