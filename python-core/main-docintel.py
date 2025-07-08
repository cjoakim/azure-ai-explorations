"""
Usage:
  python main-docintel.py <func>
  python main-docintel.py azure_sample
  python main-docintel.py explore
  python main-docintel.py explore_async_local_file
  python main-docintel.py model_pricing_html_page
"""

import asyncio
import base64
import sys
import os
import traceback

import httpx

from docopt import docopt
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
#from azure.core.rest import HttpRequest
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.aio import (
    DocumentIntelligenceClient as DocumentIntelligenceAsyncClient,
)
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence.models import DocumentAnalysisFeature

from src.io.fs import FS


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


def build_async_docintel_client() -> DocumentIntelligenceAsyncClient | None:
    try:
        endpoint = os.environ.get("AZURE_DOCINTEL_URL")
        key = os.environ.get("AZURE_DOCINTEL_KEY")
        client = DocumentIntelligenceAsyncClient(
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
    #nc_driver_handbook = "https://www.ncdot.gov/dmv/license-id/driver-licenses/new-drivers/Documents/driver-handbook.pdf"

    di_client: DocumentIntelligenceClient = build_docintel_client()
    poller = di_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=sample_url)
    )

    result: AnalyzeResult = poller.result()
    print("got result, type: {}".format(str(type(result))))
    print(result.content)


async def explore_async_local_file():
    di_client: build_async_docintel_client = build_async_docintel_client()
    # sos_lyrics = "../data/docs/dire-straits-sultans-of-swing-lyrics.pdf"
    # constitution = "../data/docs/us-constitution.pdf"
    # simple_sample = "../data/docs/simple-sample-doc.pdf"
    laws_of_chess = "../data/docs/LawsOfChess.pdf"

    infile = laws_of_chess
    print(f"Analyzing file: {infile} ...")
    async with di_client:
        with open(infile, "rb") as f:
            poller = await di_client.begin_analyze_document(
                "prebuilt-read",
                body=f,
                features=[DocumentAnalysisFeature.STYLE_FONT],
            )
            print(f"poller type: {str(type(poller))}")
            # <class 'azure.ai.documentintelligence.aio._operations._patch.AsyncAnalyzeDocumentLROPoller'>

        result: AnalyzeResult = await poller.result()
        print(f"result type: {str(type(result))}")
        # <class 'azure.ai.documentintelligence.models._models.AnalyzeResult'>

        print(result.content)
        basename = os.path.basename(infile)
        outfile = f"tmp/{basename}.json"
        FS.write_json(result.as_dict(), outfile)

        print(f"page count is {len(result.pages)}")

        for page_idx, page in enumerate(result.pages):
            print(f"---- page idx and number {page_idx} {page.page_number}")
            if page.lines:
                for line_idx, line in enumerate(page.lines):
                    if line.content:
                        print(f"line content: {line.content}")
                    if False:
                        if line.polygon:
                            print(f"line polygon: {line.polygon}")
                        if line.spans:
                            print(f"line spans: {line.spans}")


async def model_pricing_html_page():
    source_url = "https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service"
    html = fetch_html_page(source_url)
    if html is not None:
        # html_bytes = html.encode('utf-8')
        # encoded_bytes = base64.b64encode(html_bytes)
        # encoded_string = encoded_bytes.decode('utf-8')
        html_filename = "tmp/html.txt"
        FS.write(html, html_filename)

        di_client = build_async_docintel_client()

        async with di_client:
            with open(html_filename, "rb") as f:
                poller = await di_client.begin_analyze_document(
                    "prebuilt-read",
                    body=f,
                    features=[]
                )
                result: AnalyzeResult = await poller.result()
                print("got result, type: {}".format(str(type(result))))
                print(result["content"])
                FS.write_json(result.as_dict(), "tmp/html_result.json")

                for page_idx, page in enumerate(result.pages):
                    print("page_idx: {},".format(page_idx))
                    if page.lines:
                        print("page_idx: {} has {} lines".format(page_idx, len(page.lines)))
                        for line_idx, line in enumerate(page.lines):
                            print("line {}: {}".format(line_idx, line))
                    else:
                        print("page_idx: {} has no lines".format(page_idx))
           

def fetch_html_page(url: str) -> str | None:
    try:
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


def azure_sample():
    # https://pypi.org/project/azure-ai-documentintelligence/
    # https://github.com/Azure/azure-sdk-for-python/tree/main/sdk
    # https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?view=doc-intel-4.0.0&pivots=programming-language-python

    sample_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"

    docintel_client = build_docintel_client()
    poller = docintel_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=sample_url)
    )

    result: AnalyzeResult = poller.result()
    print("got result, type: {}".format(str(type(result))))

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
            elif func == "explore_async_local_file":
                asyncio.run(explore_async_local_file())
            elif func == "model_pricing_html_page":
                asyncio.run(model_pricing_html_page())
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())

