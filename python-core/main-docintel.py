"""
Usage:
  python main-docintel.py <func>
  python main-docintel.py azure_sample
  python main-docintel.py explore
  python main-docintel.py explore_async_local_file
  python main-docintel.py model_pricing_html_page
"""

import asyncio
import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

import os
from azure.core.credentials import AzureKeyCredential
from azure.core.rest import HttpRequest
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient as DocumentIntelligenceAsyncClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

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
    nc_driver_handbook ="https://www.ncdot.gov/dmv/license-id/driver-licenses/new-drivers/Documents/driver-handbook.pdf"
    
    di_client : DocumentIntelligenceClient = build_docintel_client()
    poller = di_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=sample_url))

    result: AnalyzeResult = poller.result()
    print("got result, type: ".format(str(type(result))))
    print(result.content)

async def explore_async_local_file():
    di_client : build_async_docintel_client = build_async_docintel_client()
    sos_lyrics = "../data/docs/dire-straits-sultans-of-swing-lyrics.pdf"
    constitution = "../data/docs/us-constitution.pdf"
    infile = constitution
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
        FS.write_json(result.as_dict(), "tmp/result.json")


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
            elif func == "explore_async_local_file":
                asyncio.run(explore_async_local_file())
            elif func == "model_pricing_html_page":
                model_pricing_html_page()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())



# SDK snippets below:

# class AnalyzeResult(_model_base.Model):
#     """Document analysis result.
#     :ivar api_version: API version used to produce this result. Required.
#     :vartype api_version: str
#     :ivar model_id: Document model ID used to produce this result. Required.
#     :vartype model_id: str
#     :ivar string_index_type: Method used to compute string offset and length. Required. Known
#      values are: "textElements", "unicodeCodePoint", and "utf16CodeUnit".
#     :vartype string_index_type: str or ~azure.ai.documentintelligence.models.StringIndexType
#     :ivar content_format: Format of the analyze result top-level content. Known values are: "text"
#      and "markdown".
#     :vartype content_format: str or ~azure.ai.documentintelligence.models.DocumentContentFormat
#     :ivar content: Concatenate string representation of all textual and visual elements in reading
#      order. Required.
#     :vartype content: str
#     :ivar pages: Analyzed pages. Required.
#     :vartype pages: list[~azure.ai.documentintelligence.models.DocumentPage]
#     :ivar paragraphs: Extracted paragraphs.
#     :vartype paragraphs: list[~azure.ai.documentintelligence.models.DocumentParagraph]
#     :ivar tables: Extracted tables.
#     :vartype tables: list[~azure.ai.documentintelligence.models.DocumentTable]
#     :ivar figures: Extracted figures.
#     :vartype figures: list[~azure.ai.documentintelligence.models.DocumentFigure]
#     :ivar sections: Extracted sections.
#     :vartype sections: list[~azure.ai.documentintelligence.models.DocumentSection]
#     :ivar key_value_pairs: Extracted key-value pairs.
#     :vartype key_value_pairs: list[~azure.ai.documentintelligence.models.DocumentKeyValuePair]
#     :ivar styles: Extracted font styles.
#     :vartype styles: list[~azure.ai.documentintelligence.models.DocumentStyle]
#     :ivar languages: Detected languages.
#     :vartype languages: list[~azure.ai.documentintelligence.models.DocumentLanguage]
#     :ivar documents: Extracted documents.
#     :vartype documents: list[~azure.ai.documentintelligence.models.AnalyzedDocument]
#     :ivar warnings: List of warnings encountered.
#     :vartype warnings: list[~azure.ai.documentintelligence.models.DocumentIntelligenceWarning]
#     """

#     api_version: str = rest_field(name="apiVersion")
#     """API version used to produce this result. Required."""
#     model_id: str = rest_field(name="modelId")
#     """Document model ID used to produce this result. Required."""
#     string_index_type: Union[str, "_models.StringIndexType"] = rest_field(name="stringIndexType")
#     """Method used to compute string offset and length. Required. Known values are: \"textElements\",
#      \"unicodeCodePoint\", and \"utf16CodeUnit\"."""
#     content_format: Optional[Union[str, "_models.DocumentContentFormat"]] = rest_field(name="contentFormat")
#     """Format of the analyze result top-level content. Known values are: \"text\" and \"markdown\"."""
#     content: str = rest_field()
#     """Concatenate string representation of all textual and visual elements in reading
#      order. Required."""
#     pages: List["_models.DocumentPage"] = rest_field()
#     """Analyzed pages. Required."""
#     paragraphs: Optional[List["_models.DocumentParagraph"]] = rest_field()
#     """Extracted paragraphs."""
#     tables: Optional[List["_models.DocumentTable"]] = rest_field()
#     """Extracted tables."""
#     figures: Optional[List["_models.DocumentFigure"]] = rest_field()
#     """Extracted figures."""
#     sections: Optional[List["_models.DocumentSection"]] = rest_field()
#     """Extracted sections."""
#     key_value_pairs: Optional[List["_models.DocumentKeyValuePair"]] = rest_field(name="keyValuePairs")
#     """Extracted key-value pairs."""
#     styles: Optional[List["_models.DocumentStyle"]] = rest_field()
#     """Extracted font styles."""
#     languages: Optional[List["_models.DocumentLanguage"]] = rest_field()
#     """Detected languages."""
#     documents: Optional[List["_models.AnalyzedDocument"]] = rest_field()
#     """Extracted documents."""
#     warnings: Optional[List["_models.DocumentIntelligenceWarning"]] = rest_field()
#     """List of warnings encountered."""
