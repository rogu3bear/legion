"""
Indexing and retrieval utilities for Legion.
"""
import os

def index_documents(path):
    index = {}
    for root, _, files in os.walk(path):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    index[fname] = f.read()
            except Exception:
                continue
    return index

def search(query, index):
    return [fname for fname, content in index.items() if query in content]
