import re
from bs4 import BeautifulSoup

class DataCleaner:
    """
    A class that loads data from a file and returns clean text.
    If the file contains HTML, it removes CSS, script, and HTML tags
    and returns the cleaned text. Otherwise, it returns the text as is.
    """
    def __init__(self, file_path):
        """
        Initializes the DataCleaner with the file path.
        
        :param file_path: Path to the input file.
        """
        self.file_path = file_path
        self.content = None

    def load_file(self):
        """Loads the content of the file."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.content = file.read()

    def is_html(self):
        """
        Checks whether the loaded file content is HTML.
        
        :return: True if HTML is detected, False otherwise.
        """
        if self.content is None:
            self.load_file()
        lower_content = self.content.lower()
        # Check for typical HTML markers.
        return "<html" in lower_content or "<!doctype html" in lower_content

    def clean_html(self):
        """
        Cleans the HTML content by removing <script> and <style> tags,
        then extracts and returns the plain text.
        
        :return: Cleaned text from the HTML content.
        """
        if self.content is None:
            self.load_file()
        soup = BeautifulSoup(self.content, 'html.parser')
        # Remove script and style elements
        for tag in soup(["script", "style"]):
            tag.decompose()
        # Extract text and remove extra whitespace
        text = soup.get_text(separator=' ', strip=True)
        return re.sub(r'\s+', ' ', text)

    def get_clean_text(self):
        """
        Returns the cleaned text from the file.
        If the file is HTML, it cleans it; otherwise, it returns the text as is.
        
        :return: Clean text data.
        """
        if self.content is None:
            self.load_file()
        if self.is_html():
            return self.clean_html()
        else:
            return self.content
