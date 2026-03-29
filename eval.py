import json
from rag import load_index, ask

index, chunks, sources = load_index()

QUERIES = [
    # 10 Prerequisite checks
    {"id": 1, "type": "prereq_check", "question": "Can I take 6.006 Introduction to Algorithms if I have basic programming knowledge?", "expected": "eligible"},
    {"id": 2, "type": "prereq_check", "question": "Can I take 6.046J Design and Analysis of Algorithms without taking 6.006 first?", "expected": "not eligible"},
    {"id": 3, "type": "prereq_check", "question": "Am I ready for 6.034 Artificial Intelligence if I know Python and basic math?", "expected": "eligible"},
    {"id": 4, "type": "prereq_check", "question": "Can I take 6.036 Introduction to Machine Learning without linear algebra?", "expected": "not eligible"},
    {"id": 5, "type": "prereq_check", "question": "Is 18.06 Linear Algebra required before 18.065 Matrix Methods?", "expected": "eligible"},
    {"id": 6, "type": "prereq_check", "question": "Can I take 6.854J Advanced Algorithms without 6.046J?", "expected": "not eligible"},
    {"id": 7, "type": "prereq_check", "question": "Am I eligible for 6.830 Database Systems with knowledge of algorithms and programming?", "expected": "eligible"},
    {"id": 8, "type": "prereq_check", "question": "Can I take 6.858 Computer Systems Security without 6.828?", "expected": "not eligible"},
    {"id": 9, "type": "prereq_check", "question": "Is programming experience enough to take 6.042J Mathematics for Computer Science?", "expected": "eligible"},
    {"id": 10, "type": "prereq_check", "question": "Can I enroll in 6.864 NLP without machine learning background?", "expected": "not eligible"},

    # 5 Prerequisite chain questions
    {"id": 11, "type": "prereq_chain", "question": "What is the full prerequisite chain to take 6.854J Advanced Algorithms?"},
    {"id": 12, "type": "prereq_chain", "question": "What courses do I need before 6.036 Machine Learning, and what do those courses require?"},
    {"id": 13, "type": "prereq_chain", "question": "What is the path from beginner to taking 6.858 Computer Systems Security?"},
    {"id": 14, "type": "prereq_chain", "question": "What do I need step by step to reach 18.065 Matrix Methods in Data Analysis?"},
    {"id": 15, "type": "prereq_chain", "question": "What is the prerequisite chain for 6.864 Advanced Natural Language Processing?"},

    # 5 Program requirement questions
    {"id": 16, "type": "program_req", "question": "What math courses are required for the MIT Computer Science curriculum?"},
    {"id": 17, "type": "program_req", "question": "Which courses cover algorithms and data structures at MIT?"},
    {"id": 18, "type": "program_req", "question": "What AI and ML courses are available at MIT OCW?"},
    {"id": 19, "type": "program_req", "question": "What systems courses should I take for a Computer Science degree?"},
    {"id": 20, "type": "program_req", "question": "Plan a 4-course term for a CS student who has completed 6.006 and 18.06."},

    # 5 Not in docs / trick questions
    {"id": 21, "type": "not_in_docs", "question": "Is 6.006 offered in Spring 2026?", "expected": "abstain"},
    {"id": 22, "type": "not_in_docs", "question": "Who is the professor teaching 6.034 this semester?", "expected": "abstain"},
    {"id": 23, "type": "not_in_docs", "question": "How do I get instructor consent for 6.854J?", "expected": "abstain"},
    {"id": 24, "type": "not_in_docs", "question": "What is the passing grade requirement for 6.006?", "expected": "abstain"},
    {"id": 25, "type": "not_in_docs", "question": "How many seats are available in 6.036 next semester?", "expected": "abstain"},
]

def run_eval():
    results = []
    citation_count = 0
    abstain_correct = 0
    abstain_total = 0
    prereq_correct = 0
    prereq_total = 0

    print("Running evaluation...\n")

    for q in QUERIES:
        print(f"Q{q['id']} [{q['type']}]: {q['question'][:60]}...")
        answer, srcs = ask(q["question"], index, chunks, sources)

        has_citation = "[Source:" in answer
        if has_citation:
            citation_count += 1

        abstained = "I don't have that information" in answer

        if q["type"] == "not_in_docs":
            abstain_total += 1
            if abstained:
                abstain_correct += 1

        if q["type"] == "prereq_check":
            prereq_total += 1
            expected = q.get("expected", "")
            correct = (
                (expected == "eligible" and ("eligible" in answer.lower() or "yes" in answer.lower() or "can take" in answer.lower())) or
                (expected == "not eligible" and ("not eligible" in answer.lower() or "cannot" in answer.lower() or "should not" in answer.lower() or "recommend" in answer.lower()))
            )
            if correct:
                prereq_correct += 1

        results.append({
            "id": q["id"],
            "type": q["type"],
            "question": q["question"],
            "answer": answer,
            "sources": srcs,
            "has_citation": has_citation,
            "abstained": abstained
        })
        print(f"  Citations: {'✓' if has_citation else '✗'} | Abstained: {'✓' if abstained else '✗'}\n")

    # Summary
    total = len(QUERIES)
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Citation coverage:     {citation_count}/{total} ({100*citation_count//total}%)")
    print(f"Prereq correctness:    {prereq_correct}/{prereq_total} ({100*prereq_correct//prereq_total}%)")
    print(f"Abstention accuracy:   {abstain_correct}/{abstain_total} ({100*abstain_correct//abstain_total}%)")

    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull results saved to eval_results.json")

if __name__ == "__main__":
    run_eval()