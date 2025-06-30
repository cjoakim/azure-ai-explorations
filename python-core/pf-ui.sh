#!/bin/bash

source venv/bin/activate

pf --version

pf flow test --flow flows/chat_flow1_personal.prompty --inputs question="Who was the 39th president of the United States?" --ui
