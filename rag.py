import os
import requests
from bs4 import BeautifulSoup
import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

URLS = [
    "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
    "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/",
    "https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/",
    "https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning-fall-2020/",
    "https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/",
    "https://ocw.mit.edu/courses/6-005-software-construction-spring-2016/",
    "https://ocw.mit.edu/courses/6-033-computer-system-engineering-spring-2018/",
    "https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/",
    "https://ocw.mit.edu/courses/6-830-database-systems-fall-2010/",
    "https://ocw.mit.edu/courses/6-858-computer-systems-security-fall-2014/",
    "https://ocw.mit.edu/courses/6-867-machine-learning-fall-2006/",
    "https://ocw.mit.edu/courses/6-864-advanced-natural-language-processing-fall-2005/",
    "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/",
    "https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/",
    "https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/",
    "https://ocw.mit.edu/courses/6-001-structure-and-interpretation-of-computer-programs-spring-2005/",
    "https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/",
    "https://ocw.mit.edu/courses/6-045j-automata-computability-and-complexity-spring-2011/",
    "https://ocw.mit.edu/courses/6-854j-advanced-algorithms-fall-2008/",
    "https://ocw.mit.edu/courses/6-837-computer-graphics-fall-2012/",
]

def scrape(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for t in soup(["script","style","nav","footer","header"]):
            t.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text if len(text) > 200 else None
    except:
        return None

def chunk(text, size=600, overlap=100):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+size]))
        i += size - overlap
    return chunks

def build_index():
    print("Scraping pages...")
    all_chunks, all_sources = [], []
    for url in URLS:
        text = scrape(url)
        if text:
            for c in chunk(text):
                all_chunks.append(c)
                all_sources.append(url)
            print(f"  ✓ {url}")
        else:
            print(f"  ✗ {url}")

    print(f"\nEmbedding {len(all_chunks)} chunks...")
    embeddings = MODEL.encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "index.faiss")
    with open("chunks.json", "w") as f:
        json.dump({"chunks": all_chunks, "sources": all_sources}, f)
    print("Done! index.faiss and chunks.json saved.")

def load_index():
    index = faiss.read_index("index.faiss")
    with open("chunks.json") as f:
        data = json.load(f)
    return index, data["chunks"], data["sources"]

def search(query, index, chunks, sources, k=6):
    emb = MODEL.encode([query]).astype("float32")
    faiss.normalize_L2(emb)
    _, ids = index.search(emb, k)
    results = []
    for i in ids[0]:
        results.append({"chunk": chunks[i], "source": sources[i]})
    return results

def ask(question, index, chunks, sources):
    results = search(question, index, chunks, sources)
    context = "\n\n".join([f"[Source: {r['source']}]\n{r['chunk']}" for r in results])
    unique_sources = list(set([r["source"] for r in results]))

    prompt = f"""You are a strict academic course planning assistant. Answer ONLY using the context below.

RULES:
- Every claim must cite [Source: URL]
- If not in context, say: "I don't have that information in the catalog."
- Structure your answer as:

**Answer / Plan:**
**Why (prereqs satisfied):**
**Citations:**
**Clarifying Questions (if needed):**
**Assumptions / Not in Catalog:**

Context:
{context}

Question: {question}"""

    response = CLIENT.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content, unique_sources

if __name__ == "__main__":
    build_index()