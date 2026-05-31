from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from nltk.stem import PorterStemmer
    from nltk.tokenize import wordpunct_tokenize

    STEMMER = PorterStemmer()
    NLP_BACKEND = "NLTK wordpunct tokenizer + Porter stemmer"
except ImportError:  # The app still runs in minimal Python environments.
    STEMMER = None
    NLP_BACKEND = "regex tokenizer + built-in cleaner"


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
    "you",
    "your",
}


@dataclass(frozen=True)
class FAQ:
    question: str
    answer: str
    tags: tuple[str, ...]


def load_faqs(path: Path) -> list[FAQ]:
    with path.open("r", encoding="utf-8") as file:
        raw_faqs = json.load(file)

    return [
        FAQ(
            question=item["question"],
            answer=item["answer"],
            tags=tuple(item.get("tags", [])),
        )
        for item in raw_faqs
    ]


def tokenize_and_clean(text: str) -> list[str]:
    """Tokenize, lowercase, remove stop words, and stem when NLTK is available."""
    if STEMMER is not None:
        raw_tokens = wordpunct_tokenize(text.lower())
    else:
        raw_tokens = re.findall(r"[a-z0-9']+", text.lower())

    clean_tokens = []
    for token in raw_tokens:
        token = token.strip("'")
        if len(token) < 2 or not re.search(r"[a-z0-9]", token):
            continue
        if token in STOP_WORDS:
            continue
        clean_tokens.append(STEMMER.stem(token) if STEMMER is not None else token)
    return clean_tokens


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    shared_terms = left.keys() & right.keys()
    numerator = sum(left[term] * right[term] for term in shared_terms)
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class FAQChatbot:
    def __init__(self, faqs: Iterable[FAQ]) -> None:
        self.faqs = list(faqs)
        self.documents = [
            " ".join([faq.question, *faq.tags])
            for faq in self.faqs
        ]
        self.document_tokens = [tokenize_and_clean(document) for document in self.documents]
        self.idf = self._build_idf(self.document_tokens)
        self.document_vectors = [
            self._vectorize(tokens)
            for tokens in self.document_tokens
        ]

    def _build_idf(self, tokenized_documents: list[list[str]]) -> dict[str, float]:
        document_count = len(tokenized_documents)
        document_frequency = Counter(
            token
            for tokens in tokenized_documents
            for token in set(tokens)
        )

        return {
            token: math.log((document_count + 1) / (frequency + 1)) + 1
            for token, frequency in document_frequency.items()
        }

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        total_terms = sum(counts.values())
        if total_terms == 0:
            return {}

        return {
            token: (count / total_terms) * self.idf.get(token, 1.0)
            for token, count in counts.items()
        }

    def ask(self, question: str, threshold: float = 0.12) -> dict[str, object]:
        query_tokens = tokenize_and_clean(question)
        query_vector = self._vectorize(query_tokens)
        scores = [
            cosine_similarity(query_vector, faq_vector)
            for faq_vector in self.document_vectors
        ]

        best_index = max(range(len(scores)), key=scores.__getitem__)
        best_score = scores[best_index]
        matched_faq = self.faqs[best_index]

        if best_score < threshold:
            return {
                "answer": "I could not find a close FAQ match. Please try asking about accounts, courses, payment, certificates, support, or subscriptions.",
                "matched_question": None,
                "score": round(best_score, 3),
                "tokens": query_tokens,
                "backend": NLP_BACKEND,
            }

        return {
            "answer": matched_faq.answer,
            "matched_question": matched_faq.question,
            "score": round(best_score, 3),
            "tokens": query_tokens,
            "backend": NLP_BACKEND,
        }


def build_default_chatbot() -> FAQChatbot:
    faq_path = Path(__file__).resolve().parent / "data" / "faqs.json"
    return FAQChatbot(load_faqs(faq_path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the LearnMate FAQ chatbot a question.")
    parser.add_argument("question", nargs="*", help="Question to ask the chatbot")
    args = parser.parse_args()

    chatbot = build_default_chatbot()
    question = " ".join(args.question).strip()

    if question:
        result = chatbot.ask(question)
        print(f"Question: {question}")
        print(f"Matched FAQ: {result['matched_question'] or 'No close match'}")
        print(f"Similarity: {result['score']}")
        print(f"Answer: {result['answer']}")
        print(f"NLP backend: {result['backend']}")
        return

    print("LearnMate FAQ Chatbot. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Bot: Goodbye.")
            break
        if not question:
            continue
        result = chatbot.ask(question)
        print(f"Bot: {result['answer']}")
        if result["matched_question"]:
            print(f"Matched: {result['matched_question']} ({result['score']})")


if __name__ == "__main__":
    main()
