"""
Usage:
    CLI app for Azure AI Search.
    -
    python main-langsvc.py <func>
    python main-langsvc.py explore
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

def explore():
    ta_client = build_client() 
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

def random_rows(rows, count):
    max_idx = len(rows) - 1
    random_rows = list()
    while len(random_rows) < count:
        idx = random.randint(0, max_idx)
        random_rows.append(rows[idx])
    return random_rows


def build_client():
    url = os.getenv("AZURE_LANGSERVICE_URL", None)
    key = os.getenv("AZURE_LANGSERVICE_KEY", None)
    print("build_client url: {}".format(url))
    print("build_client key: {}".format(key))
    return TextAnalyticsClient(
        endpoint=url, credential=AzureKeyCredential(key))



if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            print("=== CLI function: {}".format(func))

            if func == "explore":
                explore()
            elif func == "explore2":
                explore()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
