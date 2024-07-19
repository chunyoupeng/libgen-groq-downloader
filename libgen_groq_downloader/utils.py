from typing import Optional
from langchain.pydantic_v1 import BaseModel, Field, constr
from langchain.tools import StructuredTool
from langchain_groq import ChatGroq 
from libgen_api import LibgenSearch
import dspy, os
########
from dotenv import load_dotenv
load_dotenv()
########

def parse_text(text):
    import json
    data = text.additional_kwargs['tool_calls'][0]['function']['arguments']
    args = json.loads(data)
    return args

class BookFilters(BaseModel):
    Year: Optional[constr(min_length=4, max_length=4, regex=r'^\d{4}$')] = Field(description="The year of the book to download. Can be ignored.", default=None)
    Extension: Optional[constr(min_length=3, max_length=4)] = Field(description="The extension of the book to download.Can be ignored", default=None)
    Author: Optional[str] = Field(description="The author of the book to download. which can be ignored. Just one author", default=None)

class Book(BaseModel):
    query: str = Field(..., description="The title of the book to download.")
    filters: Optional[BookFilters] = Field(description="The filters for the book to download. but can be none.")

_book_search = StructuredTool.from_function(
    LibgenSearch().search_title_filtered, name="search_title_filtered", description="Search for books on libgen, return json of function args", args_schema=Book
)

class BookAssistant(dspy.Signature):
    """You are a book assistant and you know many books.Your task is to fix some user requests and return the correct book information. 
    1. Capitalize the title and author name correctly.If any book has multiple authors, just preserve the first one.
    2. Ensure the format is correct, only epub/azw3/mobi/pdf if the user omit, add pdf to such book info. 
    3. Do not include any preamble or explanation, only output the corrected book information, such as title, author name, language, etc."""
    user_input = dspy.InputField(desc="The user's request of book information.")
    output = dspy.OutputField(desc="The corrected book information. Every book per line")
    
class BookRecommender(dspy.Signature):
    """You are a book recommender and you know many books. Your task is to recommend books based on the user's request. If the user already has the desired books, return FINISH without any processing or explanation. Don't have any preamble or explanation"""
    user_input = dspy.InputField(desc="The user's request of book recommendation.")
    output = dspy.OutputField(desc="The recommended book information or just return FINISH if the user already has the desired books.")

BookAssistantModule = dspy.ChainOfThought(BookAssistant)
BookRecommenderModule = dspy.ChainOfThought(BookRecommender)

BookRecommenderLLM = dspy.GROQ(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
BookAssistantLLM = dspy.GROQ(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
_groq_llm = ChatGroq(model="llama3-groq-70b-8192-tool-use-preview")
tools = [_book_search]
BookFilterLLM= _groq_llm.bind_tools(tools, tool_choice="any")