"""
Usage:
    CLI app for Azure AI Search.
    -
    python main-langsvc.py <func>
    python main-langsvc.py explore_text_analytics
    python main-langsvc.py explore_qna
"""

# https://learn.microsoft.com/en-us/training/paths/develop-language-solutions-azure-ai/

import json
import os
import random
import sys
import traceback

from docopt import docopt
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.textanalytics import TextAnalyticsClient


from src.io.fs import FS
from src.os.env import Env


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        if name.startswith("AZURE_AI_SEARCH"):
            print("{}: {}".format(name, os.environ[name]))

def explore_text_analytics():
    ta_client = build_ta_client() 
    print("TTextAnalyticsClient: {}".format(ta_client))
    do_sentiment_analysis(ta_client, 10)

def do_sentiment_analysis(ta_client, num_docs=10):

    # First, gather several random rows for text analysis below.
    # This is a Kaggle dataset of tweets, with sentiment labels.
    infile = "../data/text/kaggle-jp797498e-twitter-entity-sentiment-analysis.csv"
    all_rows = FS.read_csv_as_dicts(infile)   
    test_rows = random_rows(all_rows, num_docs)

    for row in test_rows:
        txt_documents = list()
        txt_documents.append(row["tweet_text"])
        
        # Sentiment Analysis
        results = ta_client.analyze_sentiment(documents=txt_documents)
        for result in results:
            if not result.is_error:
                print(("--- Sentiment Analysis"))
                print("Document text: {}".format(row["tweet_text"]))
                print("Document sentiment: {}".format(result.sentiment))
                print("Positive score:     {}".format(result.confidence_scores.positive))
                print("Neutral score:      {}".format(result.confidence_scores.neutral))
                print("Negative score:     {}".format(result.confidence_scores.negative))
            else:
                print("Error: {}".format(result.error))

        # Key Phrases
        results = ta_client.extract_key_phrases(documents=txt_documents)
        for result in results:
            if not result.is_error:
                print(("--- Key Phrases"))
                print("Document text: {}".format(row["tweet_text"]))
                print("Document key_phrases: {}".format(result.key_phrases))
            else:
                print("Error: {}".format(result.error))

        # Language Detection
        results = ta_client.detect_language(documents=txt_documents)
        for result in results:
            if not result.is_error:
                print(("--- Language Detection"))
                print("Document text: {}".format(row["tweet_text"]))
                print("Language '{}', ISO639-1 name '{}'".format(
                    result.primary_language.name,
                    result.primary_language.iso6391_name))
            else:
                print("Error: {}".format(result.error))

        # Key Phrases
        results = ta_client.extract_key_phrases(documents=txt_documents)
        for result in results:
            if not result.is_error:
                print(("--- Key Phrases"))
                print("Document text: {}".format(row["tweet_text"]))
                print("Key Phrases: {}".format(result.key_phrases))
            else:
                print("Error: {}".format(result.error))

        # Entities
        results = ta_client.recognize_entities(documents=txt_documents)
        for idx, review in enumerate(results):
            for entity in review.entities:
                print(f"Entity '{entity.text}' has category '{entity.category}'")


        # Summary
        poller = ta_client.begin_extract_summary(txt_documents)
        extract_summary_results = poller.result()
        for result in extract_summary_results:
            if result.kind == "ExtractiveSummarization":
                print(("--- ExtractiveSummarization"))
                print("Document text: {}".format(row["tweet_text"]))
                print("Summary extracted: \n{}".format(
                    " ".join([sentence.text for sentence in result.sentences]))
                )
            else:
                print("result.kind is {}".format(result.kind))

def explore_qna():
    qa_client = build_qa_client()
    auth_client = build_authoring_client()
    print("QuestionAnsweringClient: {}".format(qa_client))
    print("AuthoringClient: {}".format(auth_client))
    # cat sdk/cognitivelanguage/azure-ai-language-questionanswering/azure/ai/language/questionanswering/authoring/aio/_operations/_operations.py | grep def  
    # list_qnas

    project_name = "p1a"
    create_project = False

    if create_project:
        print("auth_client creating project: {}".format(project_name))
        project = auth_client.create_project(
            project_name=project_name,
            options={
                "description": "project 1a",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        print("view created project info:")
        print("\tname: {}".format(project["projectName"]))
        print("\tlanguage: {}".format(project["language"]))
        print("\tdescription: {}".format(project["description"]))
    
    if True:
        print("auth_client listing projects...")
        qna_projects = auth_client.list_projects()
        for p in qna_projects:
            if p["projectName"] == project_name:
                print("project: {}".format(p["projectName"]))
                print("\tlanguage: {}".format(p["language"]))
                print("\tdescription: {}".format(p["description"]))

    if True:
        print("list project sources")
        sources = auth_client.list_sources(project_name=project_name)
        for source in sources:
            print("source name: {}".format(source.get("displayName", "N/A")))
            print("\tsource: {}".format(source["source"]))
            print("\tsource Uri: {}".format(source.get("sourceUri", "N/A")))
            print("\tsource kind: {}".format(source["sourceKind"]))

    if True:
        qna_poller = auth_client.begin_update_qnas(
            project_name=project_name,
            qnas=[]
        )
        qnas = qna_poller.result()

        # Zero QnA pairs from the first URL, but multiple for the Cosmos DB FAQ.
        # https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/models-featured
        # https://learn.microsoft.com/en-us/azure/cosmos-db/faq
    if True:    
        for item in qnas:
            print("qna: {}".format(item["id"]))
            print("\tquestions:")
            for question in item["questions"]:
                print("\t\t{}".format(question))
            print("\tanswer: {}".format(item["answer"]))


def random_rows(rows, count):
    max_idx = len(rows) - 1
    random_rows = list()
    while len(random_rows) < count:
        idx = random.randint(0, max_idx)
        random_rows.append(rows[idx])
    return random_rows


def build_ta_client() -> TextAnalyticsClient:
    url = os.getenv("AZURE_LANGSERVICE_URL", None)
    key = os.getenv("AZURE_LANGSERVICE_KEY", None)
    print("build_ta_client url: {}".format(url))
    print("build_ta_client key: {}".format(key))
    return TextAnalyticsClient(
        endpoint=url, credential=AzureKeyCredential(key))


def build_qa_client() -> QuestionAnsweringClient:
    url = os.getenv("AZURE_LANGSERVICE_URL", None)
    key = os.getenv("AZURE_LANGSERVICE_KEY", None)
    print("build_qa_client url: {}".format(url))
    print("build_qa_client key: {}".format(key))
    return QuestionAnsweringClient(
        endpoint=url, credential=AzureKeyCredential(key))

def build_authoring_client() -> AuthoringClient:
    url = os.getenv("AZURE_LANGSERVICE_URL", None)
    key = os.getenv("AZURE_LANGSERVICE_KEY", None)
    print("build_authoring_client url: {}".format(url))
    print("build_authoring_client key: {}".format(key))
    return AuthoringClient(
        endpoint=url, credential=AzureKeyCredential(key))


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            print("=== CLI function: {}".format(func))

            if func == "explore_text_analytics":
                explore_text_analytics()
            elif func == "explore_qna":
                explore_qna()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
