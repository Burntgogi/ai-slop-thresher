"""Build a traceable article-editing example from a frozen draft and its edit."""

import argparse
from collections import Counter
from difflib import SequenceMatcher, unified_diff
import hashlib
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "reports" / "article-demo"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def article(path):
    text = path.read_text(encoding="utf-8").strip()
    blocks = text.split("\n\n")
    assert blocks[0].startswith("# "), "An article title is required"
    return text, blocks[0][2:], blocks[1:]


def changes(before, after):
    a = re.findall(r"\s+|\S+", before)
    b = re.findall(r"\s+|\S+", after)
    matcher = SequenceMatcher(None, a, b, autojunk=False)
    chunks = []
    for op, i, j, k, l in matcher.get_opcodes():
        old, new = "".join(a[i:j]), "".join(b[k:l])
        if op == "equal":
            chunks.append({"kind": "equal", "before": old, "after": new})
        else:
            chunks.append({"kind": op, "before": old, "after": new})
    assert "".join(c["before"] for c in chunks) == before
    assert "".join(c["after"] for c in chunks) == after
    before_markup, after_markup = [], []
    for chunk in chunks:
        if chunk["kind"] == "equal":
            before_markup.append(html.escape(chunk["before"]))
            after_markup.append(html.escape(chunk["after"]))
        else:
            if chunk["before"]:
                before_markup.append("<del>" + html.escape(chunk["before"]) + "</del>")
            if chunk["after"]:
                after_markup.append("<ins>" + html.escape(chunk["after"]) + "</ins>")
    return chunks, "".join(before_markup), "".join(after_markup)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visual-output", type=Path)
    args = parser.parse_args()
    first_pass = read_json(DEMO / "first-pass.json")
    review = read_json(DEMO / "review.json")
    assert sha256(DEMO / "01-before.md") == first_pass["sha256"], "Frozen draft changed"
    skill_path = ROOT / "skills" / "ai-slop-thresher" / "SKILL.md"
    assert sha256(skill_path) == review["skill_sha256"], "Skill version changed"
    before_text, before_title, before = article(DEMO / "01-before.md")
    after_text, after_title, after = article(DEMO / "02-after.md")
    assert before_title == after_title, "Title changed"
    assert len(before) == len(after) == len(review["paragraphs"]) == 9

    protected = ["Burntgogi", "2026년 9월 12일", "AI Slop 탈곡기: 이 글은 흥미롭지 않습니다.",
                 "ai-slop-thresher", "thresh", "$thresh", "$ai-slop-thresher", "Codex", "Python",
                 "5회", "12개", "8개", "7개", "2개", "v1.1.0", "Apache-2.0",
                 "LICENSE", "NOTICE", "ATTRIBUTIONS.md", "'흥미로운 점은'"]
    protected_counts = []
    for value in protected:
        old_count, new_count = before_text.count(value), after_text.count(value)
        assert old_count > 0 and old_count == new_count, (value, old_count, new_count)
        protected_counts.append({"text": value, "before": old_count, "after": new_count})
    numbers = r"\d+(?:\.\d+)*"
    assert Counter(re.findall(numbers, before_text)) == Counter(re.findall(numbers, after_text))
    assert Counter(re.findall(r"'[^']+'", before_text)) == Counter(re.findall(r"'[^']+'", after_text))

    short_reasons = [
        "공개 주체·날짜·용도가 분명해 유지",
        "중복 설명을 묶고 편집 행동을 직접 서술",
        "반복 결론 삭제, 기능을 가진 표기의 예외 유지",
        "평가성 도입을 빼고 설치 절차부터 안내",
        "선택지를 바로 설명하고 가능성 유지",
        "서로 다른 제작 사실과 수치를 모두 유지",
        "반복을 줄이고 평가의 한계와 재확인 필요성 보존",
        "버전·라이선스·영어 안내 범위를 유지",
        "반복된 목적 설명 삭제, 예문 확인 안내 유지",
    ]
    rows = []
    for old, new, note, short in zip(before, after, review["paragraphs"], short_reasons):
        chunks, before_markup, after_markup = changes(old, new)
        rows.append({**note, "before": old, "after": new, "changed": old != new,
                     "before_chars": len(old), "after_chars": len(new),
                     "short_reason": short, "chunks": chunks,
                     "before_html": before_markup, "after_html": after_markup})
    old_body, new_body = "".join(before), "".join(after)
    sentence_pattern = r"[.!?](?:['\"’”])?(?=\s|$)"
    metrics = {
        "character_basis": "본문만 계산. 공백 포함, 제목과 줄바꿈 제외. Unicode 문자 수.",
        "before_chars": len(old_body), "after_chars": len(new_body),
        "removed_net_chars": len(old_body) - len(new_body),
        "reduction_percent": round((1 - len(new_body) / len(old_body)) * 100, 1),
        "before_sentences": sum(len(re.findall(sentence_pattern, p)) for p in before),
        "after_sentences": sum(len(re.findall(sentence_pattern, p)) for p in after),
        "before_commas": old_body.count(","), "after_commas": new_body.count(","),
        "paragraphs": len(rows), "changed_paragraphs": sum(r["changed"] for r in rows),
        "unchanged_paragraphs": [r["id"] for r in rows if not r["changed"]],
        "frozen_draft_unchanged": True, "title_unchanged": True,
        "protected_string_counts": protected_counts,
        "number_occurrences_preserved": True, "quoted_text_preserved": True,
        "diff_reconstruction_checked": True,
        "before_sha256": sha256(DEMO / "01-before.md"),
        "after_sha256": sha256(DEMO / "02-after.md"),
        "skill_sha256": review["skill_sha256"],
        "semantic_review": "Same-agent review recorded in review.json; not an independent evaluation.",
    }
    write(DEMO / "metrics.json", json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    write(DEMO / "changes.json", json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    patch = "".join(unified_diff((before_text + "\n").splitlines(keepends=True), (after_text + "\n").splitlines(keepends=True),
                                 fromfile="01-before.md", tofile="02-after.md"))
    write(DEMO / "article.diff", patch + ("" if patch.endswith("\n") else "\n"))

    report = [
        "# AI Slop 탈곡기 소개 기사: 스킬 적용 전후 비교",
        "2026년 9월 12일 작성. 적용 스킬: [ai-slop-thresher 1.1.0](https://github.com/Burntgogi/ai-slop-thresher/blob/v1.1.0/skills/ai-slop-thresher/SKILL.md).",
        "같은 초안을 고정한 뒤 편집했다. 이 사례에서는 반복 설명과 우회적인 서술을 줄였고, 이미 분명한 문단과 필요한 조건은 유지했다.",
        "[한 장 비교 보고서 이미지](one-page-comparison.png) · [이미지 제작 프롬프트](image-report-prompt.txt)",
        "## 비교 방법",
        "기사 형식의 초안을 한 번 작성해 저장한 뒤 스킬 지침을 읽고 그 원고만 윤문했다. 수정 결과를 본 뒤 초안을 바꾸지 않았으며 SHA-256으로 이를 확인했다. 새 취재, 인터뷰나 사용 성과를 추가하지 않았다. 두 글 모두 공개 프로젝트 문서에 바탕을 둔 예시 기사다.",
        "여기서 미적용은 이번 초안에 명시적인 스킬 편집 단계를 거치지 않았다는 뜻이다. 같은 에이전트가 초안·윤문·검토를 맡았고 앞선 대화에서 이미 스킬 지침을 접했다. 따라서 독립적인 무스킬 대조 실험이나 스킬의 일반적인 성능을 입증하는 자료로 볼 수 없다.",
        "[미적용 원문](01-before.md) · [스킬 적용문](02-after.md) · [전체 변경 기록](article.diff) · [초안 고정 기록](first-pass.json)",
        "## 관찰한 변화",
        "| 항목 | 적용 전 | 적용 후 |\n| --- | ---: | ---: |\n"
        f"| 본문 글자 수 | {metrics['before_chars']:,} | {metrics['after_chars']:,} |\n"
        f"| 문장 수 | {metrics['before_sentences']} | {metrics['after_sentences']} |\n"
        f"| 본문 문단 수 | {metrics['paragraphs']} | {metrics['paragraphs']} |\n"
        f"| 쉼표 수 | {metrics['before_commas']} | {metrics['after_commas']} |",
        f"본문은 {metrics['removed_net_chars']:,}자 줄었다({metrics['reduction_percent']}%). 공백은 포함하고 제목과 줄바꿈은 제외했다. 문장 수는 문장 끝의 마침표·물음표·느낌표를 셌으며 버전이나 파일명의 마침표는 제외했다. 수치는 실제 텍스트의 변화량이며 인간다움이나 글의 품질을 점수화한 값이 아니다.",
        f"{len(rows)}개 문단 중 {metrics['changed_paragraphs']}개를 고쳤다. 제목과 {', '.join(metrics['unchanged_paragraphs'])} 문단은 그대로 뒀다. [집계와 보존 검사](metrics.json)에서 계산 기준과 파일 해시를 확인할 수 있다.",
        "## 적용 전 기사 전문", before_text.replace("# ", "### ", 1),
        "## 적용 후 기사 전문", after_text.replace("# ", "### ", 1),
        "## 문단별 수정 이유",
    ]
    report.append("| 문단 | 처리 | 바꾼 이유 | 남긴 내용 |\n| --- | --- | --- | --- |\n" +
                  "\n".join(f"| {r['id']} · {r['label']} | {r['change']} | {r['reason']} | {r['preserved']} |" for r in rows))
    report += [
        "## 대표적인 변경 구간",
        "### 설명의 반복과 우회 표현",
        "> 이 스킬은 문장에 담긴 정보는 유지하면서 표현을 자연스럽게 다듬는 데 초점을 맞췄다. 단순히 글의 길이를 줄이는 것이 아니라, 원문의 사실과 조건, 수치, 인용, 저자의 말투를 보존하는 방식으로 편집이 이루어지도록 구성됐다.",
        "> 스킬 지침은 글을 단순히 줄이기보다 원문의 사실과 조건, 수치, 인용, 저자의 말투를 보존하며 표현을 다듬도록 한다.",
        "정보 보존과 표현 수정이라는 겹치는 설명을 묶었다. 사실·조건·수치·인용·말투라는 서로 다른 항목은 모두 남겼다.",
        "### 독자의 행동에 앞선 평가성 문장",
        "> 사용 방법은 비교적 간단하다.",
        "이 문장을 삭제하고 실제 설치 절차부터 시작했다. 독자가 무엇을 해야 하는지 설명하는 두 폴더, 같은 디렉터리와 호출명은 유지했다.",
        "### 이미 말한 목적을 반복하는 결말",
        "> AI Slop 탈곡기는 AI 문장을 무조건 짧게 만드는 대신 원문을 읽고 불필요한 표현을 덜어내는 편집을 지향한다.",
        "P02에 이미 있는 목적 설명이어서 결말에서는 덜었다. 이어지는 예문 확인과 적용 안내는 남겼다.",
        "## 일부러 고치지 않은 부분",
        "'흥미로운 점은'은 이 기사에서 독자를 끌어들이는 도입이 아니라 검토 대상 표현을 인용한 것이다. 제품명을 감싼 따옴표와 함께 그대로 뒀다. 해당 단어가 있다는 이유만으로 지우지 않았다.",
        "P03의 다만은 코드·URL·날짜·숫자의 예외를, P07의 다만은 평가 자료의 한계를 잇는다. 실제 관계가 있는 접속사라 유지했다. 열거에 필요한 쉼표와 제품명·호출명·라이선스의 하이픈도 남겼다.",
        "초안에는 장식용 em dash·en dash, 굵은 강조나 잘못된 역접의 과잉 사용이 없었다. 따라서 이번 사례에서는 해당 문제를 줄였다고 주장하지 않는다. 수정 효과를 보이기 위해 그 표현을 초안에 나중에 넣지도 않았다.",
        "## 의미 보존 대조",
        "다음은 같은 작성 에이전트가 원문과 수정문을 읽고 대조한 기록이다. 문자열 검사는 해시, 수치·인용문·보호 문자열과 변경 기록의 복원을 확인하며, 모든 의미의 보존을 자동으로 판정하지는 않는다.",
        "| 대조 항목 | 위치 | 검토 결과 |\n| --- | --- | --- |\n" +
        "\n".join(f"| {c['item']} | {', '.join(c['paragraphs'])} | {c['finding']} |" for c in review["meaning_checks"]),
        "## 검토 결과",
        review["interpretation"],
        "기사체, 공개 주체와 날짜, 사용 절차와 제약은 유지됐다. 이 한 편의 변화를 근거로 모든 글이 좋아진다고 일반화할 수는 없다. 다음 비교에서는 새 대화에서 독립적으로 초안을 만들고, 원문과 수정문의 순서를 가린 채 독자가 의미 보존과 읽기 편한 정도를 각각 판단하면 구분이 더 분명해진다.",
        "## 기사에 사용한 자료",
        "자료 기준은 문서 업데이트 커밋 `1ce5dddaff01c4353a71bbaf2abcb03f66dd4965`다. 릴리즈 날짜와 버전은 v1.1.0의 공개 기록을 사용했다.",
        "| 자료 | 기사에 사용한 내용 |\n| --- | --- |\n"
        "| [한국어 README](https://github.com/Burntgogi/ai-slop-thresher/blob/1ce5dddaff01c4353a71bbaf2abcb03f66dd4965/README.md) | 용도, 설치와 호출, 선택 출력, 편집 기준과 검증 범위 |\n"
        "| [영어 README](https://github.com/Burntgogi/ai-slop-thresher/blob/1ce5dddaff01c4353a71bbaf2abcb03f66dd4965/README.en.md) | 영어 문서의 존재와 한국어 윤문 범위 |\n"
        "| [v1.1.0 릴리즈](https://github.com/Burntgogi/ai-slop-thresher/releases/tag/v1.1.0) | 공개 주체·날짜·버전과 배포 파일 |\n"
        "| [참고 자료](https://github.com/Burntgogi/ai-slop-thresher/blob/1ce5dddaff01c4353a71bbaf2abcb03f66dd4965/ATTRIBUTIONS.md) | 휴머나이저 7개와 화면·문서 참고 2개 |",
        "## 다시 확인하기",
        "저장소 루트에서 `python evaluation/build_article_demo.py`를 실행하면 원문 고정 여부와 보호 문자열을 확인한 뒤 이 보고서, 집계와 변경 기록을 다시 만든다. 이 명령은 새 기사나 윤문을 생성하지 않는다. [편집 지시와 검토 기록](review.json)에 이번 편집 요청과 문단별 판단을 보관했다.",
    ]
    write(DEMO / "README.md", "\n\n".join(report) + "\n")

    if args.visual_output:
        template = (ROOT / "evaluation" / "article-demo-view.html").read_text(encoding="utf-8")
        data = json.dumps({"rows": rows, "metrics": metrics}, ensure_ascii=False).replace("</", "<\\/")
        initial = rows[1]
        options = "\n".join(f'<option value="{i}"{" selected" if i == 1 else ""}>{r["id"]} · {html.escape(r["label"])}</option>' for i, r in enumerate(rows))
        substitutions = {"__DATA__": data, "__OPTIONS__": options,
                         "__BEFORE__": html.escape(initial["before"]), "__AFTER__": html.escape(initial["after"]),
                         "__BEFORE_MARKED__": initial["before_html"], "__AFTER_MARKED__": initial["after_html"],
                         "__REASON__": html.escape(initial["short_reason"]),
                         "__METRICS__": f'본문 {metrics["before_chars"]:,}자 → {metrics["after_chars"]:,}자 · 문단 {metrics["changed_paragraphs"]}/{len(rows)}개 수정'}
        for key, value in substitutions.items():
            template = template.replace(key, value)
        assert len(template.encode("utf-8")) < 1_000_000
        assert "<!doctype" not in template.lower() and "<html" not in template.lower()
        write(args.visual_output, template)
    print(json.dumps({key:metrics[key] for key in ("before_chars", "after_chars", "reduction_percent", "before_sentences", "after_sentences", "before_commas", "after_commas", "changed_paragraphs", "unchanged_paragraphs", "frozen_draft_unchanged")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
