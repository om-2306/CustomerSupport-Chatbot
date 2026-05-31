# FAQ Chatbot

This project implements a simple FAQ chatbot for the fictional LearnMate online learning platform.

## What It Does

- Collects FAQs in `data/faqs.json`.
- Preprocesses text with tokenization, lowercasing, stop-word removal, and optional stemming through NLTK.
- Converts FAQ questions and user questions into TF-IDF vectors.
- Uses cosine similarity to find the closest FAQ.
- Returns the best matching answer in a CLI or browser chat UI.

## Run From The Terminal

```powershell
python faq_chatbot.py "How do I reset my password?"
```

For an interactive terminal chat:

```powershell
python faq_chatbot.py
```

## Run The Web UI

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Optional NLTK Setup

The project works without external dependencies in this environment. If NLTK is installed, the chatbot automatically uses `wordpunct_tokenize` and `PorterStemmer`.

```powershell
python -m pip install -r requirements.txt
```

## Main Files

- `data/faqs.json`: FAQ questions, answers, and tags.
- `faq_chatbot.py`: NLP preprocessing, TF-IDF vector creation, cosine similarity, and CLI chatbot.
- `app.py`: Standard-library HTTP server and simple chat UI.
