"""Build the requested Korean report from saved sources, outputs, and checks."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path, lines):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def block(text):
    fence = "````" if "```" in text else "```"
    return [fence + "text", text, fence, ""]


def main():
    cases = read_json("evaluation/cases.json")
    transfer = read_json("evaluation/transfer-cases.json")
    final = {row["id"]: row["output"] for row in read_json("evaluation/final-results.json")["outputs"]}
    extra = {row["id"]: row["output"] for row in read_json("evaluation/transfer-results.json")["outputs"]}
    notes = {row["id"]: row for row in read_json("evaluation/semantic-review.json")["cases"]}
    selected = read_json("research/comparison.json")
    checks = read_json("evaluation/checks/round-5.json")
    summary = read_json("evaluation/checks/summary.json")
    before = {key: sum(row["before"][key] for row in checks["cases"]) for key in checks["cases"][0]["before"]}
    after = {key: sum(row["after"][key] for row in checks["cases"]) for key in checks["cases"][0]["after"]}

    comparisons = ["# AI Slop 탈곡기 적용 전후 전문", "", "기준일: 2026년 9월 12일. 평가 지침: humanizer 1.0.0. 현재 이름: ai-slop-thresher 1.1.0.", "", "미적용은 같은 원문을 그대로 둔 대조군이다. 원문과 윤문은 현재 작성 에이전트가 생성한 가상 예문이다. 독립 모델 대조 실험이나 실제 고객 자료가 아니다. 코드 블록은 원문의 기호를 그대로 보여주기 위한 보고서 서식이다.", ""]
    for case in cases + transfer:
        output = final.get(case["id"], extra.get(case["id"]))
        comparisons.extend([f"## {case['id']} · {case['genre']}", "", f"요청: {case['request']}", "", "미적용 원문", "", *block(case["source"]), "스킬 적용 결과" if case.get("mode") != "diagnose" else "스킬 적용 진단", "", *block(output), f"검토: {notes[case['id']]['note']}", "", "보존·요구 항목", ""])
        comparisons.extend(f"{i}. {claim}" for i, claim in enumerate(case["claims"], 1))
        comparisons.append("")
    write("reports/comparisons.md", comparisons)

    report = ["# AI Slop 탈곡기: 이 글은 흥미롭지 않습니다.", "", "제작·비교·개선 보고서. 작성일: 2026년 9월 12일. 현재 버전: ai-slop-thresher 1.1.0.", "", "한국어 초안의 반복 수사와 과잉 설명을 줄이는 스킬을 제작했다. 최근 12개월 이내 생성되고 별 수가 1,000개 이상인 관련 GitHub 저장소 7개를 비교했다. 초기본 이후 다섯 차례 규칙을 개선했으며, 기본 예문 12개와 추가 전이 예문 8개를 검토했다.", "", "스킬은 원문을 짧게 만드는 것만을 목표로 삼지 않는다. 불필요한 예고와 장식을 줄이면서 조건·예외·수치·인용·말투를 유지하도록 설계했다. 이미 자연스러운 문장은 그대로 반환한다.", "", "[스킬 원문](../skills/ai-slop-thresher/SKILL.md) · [전체 적용 전후 20개 사례](comparisons.md) · [평가 방법](../evaluation/protocol.md) · [재현 검사 결과](../evaluation/checks/summary.json)", "", "## 1. 적용 요소와 편집 기준", "", "| 요청 요소 | 적용 방법 | 보존할 예외 |", "| --- | --- | --- |", "| AI slop | 내용 없는 예고, 과장, 반대편을 꾸며내는 대구, 반복 결말을 줄인다. | 저자의 실제 의견과 감정은 유지한다. |", "| TMI | 중복 설명과 요청에 필요 없는 일반론을 덜고 후속 제안을 자동으로 붙이지 않는다. | 조건·근거·절차·요청된 예시는 보존한다. |", "| 독특한 점 반복 언급 | 흥미로운 점 등의 예고를 빼고 사실을 바로 쓴다. 같은 특징을 재차 칭찬하지 않는다. | 인용문과 해당 표현 자체를 분석하는 진단은 유지한다. |", "| 문맥에 맞지 않는 접속사 | 실제 역접·인과·시간 순서인지 확인해 삭제하거나 재구성한다. | 실제 관계를 알려주는 접속사는 남긴다. |", "| 같은 성격의 단어 나열 | 동의어 수식은 하나로 줄인다. | 서로 다른 기능·원인·조건은 전부 남긴다. |", "| 쉼표·작은따옴표 과잉 | 호흡용 쉼표와 단어를 감싸는 강조를 덜어낸다. | 인용·실제 표시 문구·숫자 구분과 필요한 구문 구분은 보존한다. |", "| Markdown·대시·하이픈 강조 | 일반 산문의 장식용 굵게·기울임·대시·하이픈 불릿을 쓰지 않는다. | 날짜·음수·범위·URL·코드·명령어와 요청한 문서 구조는 보존한다. |", "", "em dash와 en dash, hyphen은 문자이며 Markdown 전용 문법은 아니다. 이번 요구는 산문에서 강조 장치로 사용하는 것을 피하라는 뜻으로 적용했다. 직접 인용과 기능 표기의 문자는 손상시키지 않는다.", "", "## 2. GitHub 저장소 선정과 비교", "", "기간은 2025년 9월 12일부터 2026년 9월 12일까지다. 생성 여부는 GitHub REST API의 created_at으로 확인했고 별 수 역시 API 조회 값을 기록했다. 최근 커밋 날짜나 과거 검색 캐시를 생성일·현재 별 수로 사용하지 않았다. 아래 생성일은 UTC 날짜다.", "", "| 저장소 | 생성일 | 조회 별 수 | 비교할 원문 |", "| --- | --- | ---: | --- |"]
    for item in selected:
        m = item["metadata"]
        report.append(f"| [{item['repo']}]({m['url']}) | {m['created_at'][:10]} | {m['stars']:,} | [고정 리비전]({item['source_url']}) · [API 메타데이터](https://api.github.com/repos/{item['repo']}) |")
    report.extend(["", "관련 후보 8개 중 7개를 선정했다. RevoltDevScript/Revolt-Script는 학습 플랫폼 자동화가 중심이어서 비교 범위에서 제외했다. Humanizer-zh는 다른 두 저장소의 영향을 명시하므로 7개를 독립적인 방법 7가지로 보지 않는다. 별 수는 선정 조건이며 품질 순위가 아니다. 검색 범위와 제외 근거는 [선정 기록](../research/selection-notes.md), 조회값은 [메타데이터](../research/repositories.json)에 있다.", "", "| 저장소 | 채택한 내용 | 제외·조정한 내용 |", "| --- | --- | --- |"])
    for item in selected:
        report.append(f"| [{item['repo']}]({item['source_url']}) | {item['adopt']} | {item['omit']} |")
    report.extend(["", "규칙과 예문은 새로 작성했다. 상류 스킬을 모두 실행해 성능을 순위화한 비교는 아니며, 상류의 탐지율·통계 주장을 이 스킬의 성능 근거로 옮기지 않았다. 참조한 파일은 커밋 리비전과 함께 [출처 기록](../research/source-revisions.json)에 고정했다.", "", "## 3. 미적용과 적용 결과", "", "대조군은 별도 모델의 무스킬 응답이 아니라 같은 초안 원문이다. 아래 예문도 실제 제품이나 연구의 사실 자료가 아닌 가상 설정이다.", ""])
    for cid in ("C01", "C05", "C11"):
        case = next(c for c in cases if c["id"] == cid)
        report.extend([f"### {cid} · {case['genre']}", "", "미적용", "", *block(case["source"]), "적용", "", *block(final[cid]), notes[cid]["note"], ""])
    report.extend(["[전체 사례 전문](comparisons.md)에는 기술 문서, 직접 인용, 요금 조건, 초보자 설명, 번호 목록, 모호한 출처와 진단 전용 요청도 포함했다.", "", "## 4. 다섯 차례 재귀개선", "", "각 회차는 기존 버전 적용, 결과 또는 경계 사례 검토, 규칙 수정, 재적용·검사 순서로 진행했다. 관찰한 출력 결함과 지침의 모호함을 구분했다. 2~4차에서는 기존 후보가 이미 보존한 내용을 일부러 망가뜨리지 않고 지침을 명확히 했다. 이전 통과 결과는 바꿀 이유가 없으면 유지했다.", "", "| 회차 | 버전 | 발견 근거 | 반영한 수정 | 누적 문자 검사 |", "| --- | --- | --- | --- | --- |", "| 1 | 0.1.0 → 0.2.0 | C03에 명사형·피동과 비슷한 예정 표현이 남음 | 한국어 동사문과 원래 격식 보존 | 3/3 |", "| 2 | 0.2.0 → 0.3.0 | C04·C05에서 가능성·의무·표본 범위를 판단할 명시적 기준이 부족 | 부정·조건·범위·인과·출처를 보존 목록에 추가 | 5/5 |", "| 3 | 0.3.0 → 0.4.0 | C06~C08에서 장식과 인용·기능 문자를 구별할 기준이 부족 | 인용, 날짜, 코드, URL, 표시 문구의 보존 예외 추가 | 8/8 |", "| 4 | 0.4.0 → 0.5.0 | C09~C11에서 실제 열거·필요한 비유·원래 부사를 지울 위험 | TMI 제거와 요약을 구별하고 보존 기준을 강화 | 11/11 |", "| 5 | 0.5.0 → 1.0.0 | C04의 조사 연결이 어색함. C12와 진단 요청의 출력 계약을 정리할 필요 | 문단 전체 재독, 출력 방식과 입력 경계 명확화 | 12/12 |", "", "검사 수가 늘어난 것은 누적 사례 수가 늘었기 때문이다. 3/3에서 12/12로 바뀐 것을 성능 향상률로 해석하지 않는다. 각 회차의 실제 결과와 관찰 근거는 [rounds 폴더](../evaluation/rounds), 지침 스냅샷은 [versions 폴더](../evaluation/versions)에 있다.", "", "추가 검수에서 T02의 불과하며를 불과해로 바꾼 표현이 인과를 강하게 만들 수 있음을 발견했다. 문자 검사는 이를 통과시켰지만 자체 의미 검토로 불과하고로 복원했다. 이는 1.0.0의 기존 규칙을 적용한 출력 수정이며 여섯 번째 규칙 개선으로 집계하지 않았다. [수정 기록](../evaluation/final-qa.json)", "", "## 5. 측정 결과와 한계", "", "기본 12개 사례의 편집 가능 부분에서 집계했다. 보호 대상으로 지정한 직접 인용·코드·실제 표시 문구는 표면 표현 집계에서 제외했다. 단, 문자 보존 여부는 따로 검사했다.", "", "| 측정 항목 | 미적용 | 적용 | 해석 |", "| --- | ---: | ---: | --- |", f"| 전체 글자 수 | {before['characters']:,} | {after['characters']:,} | 공백·줄바꿈·기호 포함. 짧을수록 좋다는 점수가 아님 |", f"| 지정 예고 표현 | {before['staging_phrases']} | {after['staging_phrases']} | 검사기에 명시한 유한한 표현 목록만 셈 |", f"| 쉼표 문자 | {before['commas_in_editable_text']} | {after['commas_in_editable_text']} | 실제 열거와 금액 구분용 쉼표가 남음 |", f"| 작은따옴표 문자 | {before['single_quote_marks_in_editable_text']} | {after['single_quote_marks_in_editable_text']} | 보호 인용·표시 문구 제외 |", f"| 장식 대시·하이픈 패턴 | {before['dash_marks_in_editable_text']} | {after['dash_marks_in_editable_text']} | en dash·하이픈 추가 사례는 T07에서 별도 확인 |", f"| 굵게 표시 구간 | {before['bold_spans_in_editable_text']} | {after['bold_spans_in_editable_text']} | 보존할 문서 구조와 구별 |", "", f"기본 사례의 숫자 토큰·보존 문자열·기호 검사는 {summary['round_5']['passed']}/{summary['round_5']['evaluated']}, 추가 전이 사례 검사는 {summary['transfer']['passed']}/{summary['transfer']['evaluated']} 통과했다. 금액 변경, 명령어 변조, 인용 변경, 기능 누락을 의도적으로 넣은 네 가지 검사 대조군은 모두 오류로 잡혔다. 이는 검사기가 단순히 모든 문자열을 통과시키지 않는다는 확인이다.", "", "의미와 요청 충족 여부는 [자체 검토 기록](../evaluation/semantic-review.json)에 사례별로 남겼다. 숫자 토큰 검사는 숫자 집합의 누락·추가만 확인하므로 숫자와 대상의 관계가 뒤바뀌는 오류까지 보장하지 않는다. 쉼표나 표현 개수도 문맥을 이해하지 못한다. T02처럼 문자 검사에 잡히지 않는 오류를 따로 읽어야 한다.", "", "원문 작성·윤문·의미 평가는 같은 에이전트가 수행했다. 기본 및 전이 예문 모두 자체 작성이므로 독립적인 사람 평가, 통제된 모델 비교, 홀드아웃 성능 검증으로 볼 수 없다. 이번 작업은 실행 가능한 스킬, 요구별 예시, 실제 수정 이력과 재현 가능한 문자 검사까지 제공한다. 인간 작성 판별이나 AI 탐지 회피율은 평가하지 않았다.", "", "## 6. 사용과 재현", "", "기본 호출", "", "```text", "$thresh 아래 글의 뜻과 말투를 유지하면서 자연스럽게 다듬어 주세요.", "", "여기에 원문을 붙여 넣습니다.", "```", "", "비교가 필요하면 적용 전후와 변경 이유를 함께 요청한다. 진단만 필요하면 고쳐 쓰지 말고 문제 구간만 짚어 달라고 요청한다. 평소에는 윤문 본문만 반환한다. 런타임은 지침 파일만 읽으며 외부 API나 추가 Python 패키지가 필요하지 않다.", "", "평가 문자 검사 재실행은 Python 3 표준 라이브러리만 사용한다. 저장된 결과를 다시 검사하며 새 윤문을 생성하지 않는다.", "", "```powershell", "python evaluation/run_checks.py", "python evaluation/build_report.py", "```", "", "공식 skill-creator의 quick_validate.py로 최종 SKILL.md 형식을 검증했고 UI 메타데이터의 YAML, 설명 길이와 호출명을 확인했다. 이 형식 검증은 자연스러움 검증과 별개다. 배포 파일은 [ai-slop-thresher.zip](../dist/ai-slop-thresher.zip)이며, 배포 ZIP에는 ai-slop-thresher 본 스킬 네 파일과 thresh 단축 스킬 두 파일이 함께 들어 있다."])
    report[4:4] = ["English: AI Slop Thresher: This Text Is Not Interesting.", "", "정식 호출: `$ai-slop-thresher`. 짧은 호출: `$thresh`. 1.1.0은 이름과 호출명 변경이다. 아래 예문과 5회 개선 기록은 편집 지침이 같은 1.0.0 당시 결과다. [변경 기록](../research/rename-notes.md)", ""]
    write("reports/ai-slop-thresher-report.md", report)

    hashes = []
    for folder in ("ai-slop-thresher", "thresh"):
        for p in sorted((ROOT / "skills" / folder).rglob("*")):
            if p.is_file():
                hashes.append({"path": p.relative_to(ROOT / "skills").as_posix(), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    write("research/artifact-manifest.json", [json.dumps({"version": "1.1.0", "skill": "ai-slop-thresher", "shortcut": "thresh", "files": hashes}, ensure_ascii=False, indent=2)])
    print(json.dumps({"report": str(ROOT / "reports/ai-slop-thresher-report.md"), "comparison_cases": len(cases) + len(transfer), "metrics_before": before, "metrics_after": after}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
