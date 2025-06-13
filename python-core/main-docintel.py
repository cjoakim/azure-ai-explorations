"""
Usage:
  TODO  - implement samples with the azure-ai-documentintelligence SDK
  python main-docintel.py <func>
  python main-docintel.py azure_sample
  python main-docintel.py explore
  python main-docintel.py model_pricing_html_page
"""

import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

import os
from azure.core.credentials import AzureKeyCredential
from azure.core.rest import HttpRequest
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from src.io.fs import FS
from src.os.env import Env
from src.os.system import System
from src.util.counter import Counter


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)

# helper functions

def get_words(page, line):
    result = []
    for word in page.words:
        if _in_span(word, line.spans):
            result.append(word)
    return result


def _in_span(word, spans):
    for span in spans:
        if word.span.offset >= span.offset and (
            word.span.offset + word.span.length
        ) <= (span.offset + span.length):
            return True
    return False

def build_docintel_client() -> DocumentIntelligenceClient | None:
    try:
        endpoint = os.environ.get("AZURE_DOCINTEL_URL")
        key = os.environ.get("AZURE_DOCINTEL_KEY")
        client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        return client  # an instance of 'azure.ai.documentintelligence._patch.DocumentIntelligenceClient'
    except Exception as e:
        print("Error building Document Intelligence client:")
        print(str(e))
        print(traceback.format_exc())
        return None

def explore():
    sample_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"
    nc_driver_handbook ="https://www.ncdot.gov/dmv/license-id/driver-licenses/new-drivers/Documents/driver-handbook.pdf"
    
    docintel_client = build_docintel_client()
    poller = docintel_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=sample_url))

    result: AnalyzeResult = poller.result()
    print("got result, type: ".format(str(type(result))))
    print(result.content)


def model_pricing_html_page():
    # HTML doesn't seem to be supported as a source.
    # curl -v ...url... -> Content-Type: text/html; charset=utf-8
    # Code: InvalidRequest
    # Message: Invalid request.
    # Inner error: {
    # "code": "InvalidContent",
    # "message": "Could not download the file from the given URL."
    # }
    #
    # Also, serving files from localhost doesn't work.
    # python -m http.server 8000 
    # source_url = "http://localhost:8000/docs/sample-layout.pdf"
    # "message": "Could not download the file from the given URL."
    source_url = "https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service"
    docintel_client : DocumentIntelligenceClient = build_docintel_client()
    poller = docintel_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=source_url))
    result: AnalyzeResult = poller.result()
    print("got result, type: ".format(str(type(result))))
    print(result)


def azure_sample():
    # https://pypi.org/project/azure-ai-documentintelligence/
    # https://github.com/Azure/azure-sdk-for-python/tree/main/sdk
    # https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?view=doc-intel-4.0.0&pivots=programming-language-python

    sample_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"

    docintel_client = build_docintel_client()
    poller = docintel_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=sample_url))

    result: AnalyzeResult = poller.result()
    print("got result, type: ".format(str(type(result))))

    if result.styles and any([style.is_handwritten for style in result.styles]):
        print("Document contains handwritten content")
    else:
        print("Document does not contain handwritten content")

    for page in result.pages:
        print(f"----Analyzing layout from page #{page.page_number}----")
        print(
            f"Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}"
        )
        if page.lines:
            for line_idx, line in enumerate(page.lines):
                words = get_words(page, line)
                print(
                    f"...Line # {line_idx} has word count {len(words)} and text '{line.content}' "
                    f"within bounding polygon '{line.polygon}'"
                )
                for word in words:
                    print(
                        f"......Word '{word.content}' has a confidence of {word.confidence}"
                    )
        if page.selection_marks:
            for selection_mark in page.selection_marks:
                print(
                    f"Selection mark is '{selection_mark.state}' within bounding polygon "
                    f"'{selection_mark.polygon}' and has a confidence of {selection_mark.confidence}"
                )

    if result.tables:
        for table_idx, table in enumerate(result.tables):
            print(
                f"Table # {table_idx} has {table.row_count} rows and "
                f"{table.column_count} columns"
            )
            if table.bounding_regions:
                for region in table.bounding_regions:
                    print(
                        f"Table # {table_idx} location on page: {region.page_number} is {region.polygon}"
                    )
            for cell in table.cells:
                print(
                    f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'"
                )
                if cell.bounding_regions:
                    for region in cell.bounding_regions:
                        print(
                            f"...content on page {region.page_number} is within bounding polygon '{region.polygon}'"
                        )



if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "azure_sample":
                azure_sample()
            elif func == "explore":
                explore()
            elif func == "model_pricing_html_page":
                model_pricing_html_page()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
