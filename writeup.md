# RAG Course Planning Assistant — Write-Up
**Purple Merit Technologies | AI/ML Engineer Intern Assessment | March 2026**
**Submitted by: Uday Yadav**

---

## Chosen Institution & Sources
**MIT OpenCourseWare** (ocw.mit.edu) — accessed March 29, 2026

19 course pages covering: Algorithms (6.006, 6.046J, 6.854J), AI/ML (6.034, 6.036, 6.867, 6.864), Systems (6.828, 6.830, 6.858), Mathematics (18.06, 18.065, 18.650), and foundational CS (6.001, 6.004, 6.005, 6.042J, 6.045J, 6.837).

---

## Architecture Overview
```
User Question
     ↓
Sentence Transformer (all-MiniLM-L6-v2)
     ↓
FAISS Index (cosine similarity, top-6 chunks)
     ↓
Prompt Builder (context + student profile + rules)
     ↓
Groq Llama-3.3-70b-versatile
     ↓
Structured Response (Answer / Citations / Clarifying Qs)
```

---

## Chunking & Retrieval Choices

- **Chunk size:** 600 words with 100-word overlap
  - Large enough to capture full prerequisite descriptions
  - Overlap prevents splitting mid-sentence prereq rules
- **Embeddings:** all-MiniLM-L6-v2 (local, fast, no API cost)
- **Vector store:** FAISS IndexFlatIP with L2-normalized vectors = cosine similarity
- **k=6 chunks** retrieved per query — enough context without exceeding LLM context window

---

## Prompting Strategy

Single-turn prompt with strict rules injected in system context:
- Every claim must cite `[Source: URL]`
- Hard refusal phrase for out-of-catalog queries
- Mandatory structured output format enforced in prompt

---

## Evaluation Summary

| Metric | Score |
|---|---|
| Citation coverage | 25/25 (100%) |
| Prereq correctness | 5/10 (50%) |
| Abstention accuracy | 5/5 (100%) |

**Key failure modes:**
- Prereq correctness at 50%: MIT OCW pages don't explicitly list formal prerequisites — they describe course content, not enrollment requirements. The model sometimes infers eligibility instead of citing hard rules.
- Chunking produced only 19 chunks (pages were content-light). More granular catalog sources would improve retrieval.

**Next improvements:**
1. Add formal university catalog PDFs with explicit prereq listings
2. Implement multi-hop retrieval for prerequisite chains
3. Add a verifier pass to check citations before returning answer

---

## Repo
https://github.com/udayyadav-ds/rag-course-planner