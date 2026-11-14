#!/usr/bin/env python3
"""Validate the UTF-8 corpus with the Python standard library. No network needed."""
import collections
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_jsonl(path):
    text = path.read_text(encoding="utf-8")
    require(text.endswith("\n"), f"Missing final newline: {path.name}")
    return [json.loads(line) for line in text.splitlines()]


def normalized(text):
    return "".join(
        char for char in unicodedata.normalize("NFKC", text or "")
        if char.isalnum() or char == "_"
    )


def main():
    report = json.loads((ROOT / "validation_report.json").read_text(encoding="utf-8"))
    records = read_jsonl(ROOT / "all.jsonl")
    require(len(records) == report["final_questions"], "Combined count mismatch")
    require(len({q["id"] for q in records}) == len(records), "Duplicate IDs")
    required = {"id", "year", "section", "passage", "stem", "options", "answer",
                "answer_candidates", "answer_status", "notes"}
    signatures = set()
    for q in records:
        label = q["id"]
        require(set(q) == required, f"Unexpected fields: {label}")
        require(re.fullmatch(r"GKYY-20(1[6-9]|2[0-5])-\d{3}", label), f"Bad ID: {label}")
        require(int(label.split("-")[1]) == q["year"], f"Year mismatch: {label}")
        require(q["section"] == "言语理解与表达", f"Wrong section: {label}")
        require(isinstance(q["stem"], str) and q["stem"].strip(), f"Empty stem: {label}")
        require(q["passage"] is None or isinstance(q["passage"], str) and q["passage"].strip(),
                f"Empty passage: {label}")
        require(set(q["options"]) == set("ABCD"), f"Missing options: {label}")
        require(all(isinstance(v, str) and v.strip() for v in q["options"].values()),
                f"Empty option: {label}")
        candidates = q["answer_candidates"]
        require(candidates and candidates == sorted(set(candidates)), f"Bad candidates: {label}")
        require(set(candidates) <= set("ABCD"), f"Invalid answer letter: {label}")
        if q["answer_status"] == "single":
            require(candidates == [q["answer"]], f"Single-answer mismatch: {label}")
        else:
            require(q["answer_status"] == "disputed" and q["answer"] is None
                    and len(candidates) >= 2, f"Dispute mismatch: {label}")
        text = "\n".join([q["stem"], q["passage"] or "", *q["options"].values()])
        require(not re.search(r"!\[|<img|data:image|\ufffd|【文段出处】|认准淘宝店铺|第\d+页[，,]?共\d+页", text),
                f"Image, replacement glyph, or page noise: {label}")
        signature = (q["year"], normalized(q["stem"]), normalized(q["passage"]),
                     tuple(sorted(normalized(v) for v in q["options"].values())))
        require(signature not in signatures, f"Duplicate question in same year: {label}")
        signatures.add(signature)
    combined = []
    counts = collections.Counter(q["year"] for q in records)
    for year in range(2016, 2026):
        subset = read_jsonl(ROOT / f"{year}.jsonl")
        expected = [q for q in records if q["year"] == year]
        require(subset == expected, f"Year JSONL differs: {year}")
        require(len(subset) == report["questions_by_year"][str(year)], f"Year count mismatch: {year}")
        require([q["id"] for q in subset] == [f"GKYY-{year}-{n:03d}" for n in range(1, len(subset) + 1)],
                f"Non-contiguous year IDs: {year}")
        markdown = (ROOT / f"{year}.md").read_text(encoding="utf-8")
        sections = re.split(r"(?m)^## (GKYY-\d{4}-\d{3})\s*$", markdown)
        require(len(sections) == 1 + 2 * len(subset), f"Markdown question count: {year}")
        for i, q in enumerate(subset):
            require(sections[2 * i + 1] == q["id"], f"Markdown ID mismatch: {q['id']}")
            body = sections[2 * i + 2]
            flat = re.sub(r"\s+", "", body)
            for text in [q["stem"], q["passage"] or "", *q["notes"]]:
                require(re.sub(r"\s+", "", text) in flat, f"Markdown text mismatch: {q['id']}")
            for letter, text in q["options"].items():
                require(re.sub(r"\s+", "", f"- {letter}. {text}") in flat,
                        f"Markdown option mismatch: {q['id']} {letter}")
            answer_text = f"答案：{q['answer']}" if q["answer"] else "答案存在分歧：" + "/".join(q["answer_candidates"])
            require(answer_text in flat, f"Markdown answer mismatch: {q['id']}")
        combined.extend(subset)
    require(combined == records, "Combined order differs from year files")
    actual_disputes = {q["id"]: q["answer_candidates"] for q in records if q["answer_status"] == "disputed"}
    require(actual_disputes == {q["id"]: q["answer_candidates"] for q in report["disputed_answers"]},
            "Dispute report mismatch")
    require(report["scope"]["raw_question_occurrences"] - report["excluded_occurrences"]
            - report["merged_duplicate_occurrences"] == len(records), "Coverage accounting mismatch")
    checksums = ROOT / "SHA256SUMS.json"
    if checksums.exists():
        for name, expected in json.loads(checksums.read_text(encoding="utf-8")).items():
            actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            require(actual == expected, f"File checksum mismatch: {name}")
    print(json.dumps({"status": "PASS", "questions": len(records), "by_year": dict(sorted(counts.items())),
                      "disputed": len(actual_disputes), "formats_consistent": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
