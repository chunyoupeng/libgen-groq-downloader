from libgen_api import LibgenSearch
import datetime, dspy
import logging
from utils import *
import requests, os, magic

class LibgenGroqDownloader:
    def __init__(self, user_input):
        self.logger = logging.getLogger(__name__)
        self.logger.info('LibgenGroqDownloader initialized')
        self.folder = os.path.join("results", datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) 
        self.user_input = user_input
        self.text_result = None
        self.search = LibgenSearch()
        os.makedirs(self.folder, exist_ok=True)

    def _recommend(self):
        with dspy.context(lm=BookRecommenderLLM):
            res = BookAssistantModule(user_input=self.user_input).output
            if res != "FINISH":
                self.user_input = res
            logging.info(f"After recommending, user input: {self.user_input}")

    def _book_assistant(self):
        with dspy.context(lm=BookAssistantLLM):
            res = BookAssistantModule(user_input=self.user_input).output
            self.text_result = res
            logging.info(f"After book assistant, result: {self.text_result}")
    
    def download(self):
        self._recommend()
        self._book_assistant()
        book_list = self.text_result.split("\n")
        for b in book_list:
            if b != "":
                logging.info(f"Downloading book: {b}")
                self._parse_single_book(b)

    def _parse_single_book(self, book_description):
        tool_msg = BookFilterLLM.invoke(book_description)
        args = parse_text(tool_msg)
        args["exact_match"] = False
        logging.info(f"Args are: {args}")
        results = self.search.search_title_filtered(**args)
        logging.info(f"Results are: {results}")
        if not results:
            logging.info(f"No results found for {book_description}. Trying Only search for title...")
            results = self.search.search_title(args['query'])
        result = results[0]
        logging.info(f"Result item is: {result}")
        title = result["Title"]
        author = result["Author"]
        url = self.search.resolve_download_links(result)["GET"]
        file_path = os.path.join(os.getcwd(), self.folder, f"{title} by {author}")
        self._download_book(url, file_path)


    def _download_book(self, url, file_path):
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)

        # Use python-magic to detect the file type
        file_type = magic.from_file(file_path, mime=True)
        logging.info(f"Detected file type for {file_path}: {file_type}")

        if "pdf" in file_type:
            new_file_path = file_path + ".pdf"
        elif "epub" in file_type:
            new_file_path = file_path + ".epub"
        elif "mobi" in file_type:
            new_file_path = file_path + ".mobi"
        elif "azw3" in file_type:
            new_file_path = file_path + ".azw3"
        else:
            new_file_path = file_path + ".bin"  # Unknown type, save as binary

        os.rename(file_path, new_file_path)
        logging.info(f"File saved as: {new_file_path}")