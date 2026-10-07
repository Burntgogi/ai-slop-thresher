---
name: thresh
description: AI Slop 탈곡기의 짧은 호출 이름. 사용자가 thresh를 직접 불러($thresh, /thresh 등) 한국어 글의 AI 말투·과잉 설명·불필요한 부정과 재정의 표현을 다듬도록 요청할 때만 사용하며 ai-slop-thresher의 지침을 적용한다. 호출 문법은 하네스에 따른다. 이름 없이 윤문을 요청하면 이 스킬 대신 ai-slop-thresher를 사용한다.
metadata:
  version: "1.2.2"
  canonical_skill: "ai-slop-thresher"
argument-hint: "[다듬을 글 또는 파일 경로]"
disable-model-invocation: true
---

# AI Slop 탈곡기 단축 호출

먼저 이 파일을 기준으로 [../ai-slop-thresher/SKILL.md](../ai-slop-thresher/SKILL.md)를 읽고 그 지침을 현재 요청에 적용한다. 본 스킬에서 링크한 참고 파일의 상대 경로는 ai-slop-thresher 폴더를 기준으로 해석한다.

호출명만 짧게 제공한다. 윤문 규칙을 따로 추가하거나 바꾸지 않으며 출력 방식도 본 스킬을 따른다. 단축 호출 안내나 제품 부제를 윤문 결과에 붙이지 않는다.

본 스킬 파일을 읽지 못하면 실행 환경이 이름으로 스킬을 불러올 수 있는 경우에 한해 ai-slop-thresher 스킬을 불러와 적용한다. 그것도 할 수 없으면 본 스킬을 찾지 못한 경로와 함께 ai-slop-thresher와 thresh 두 폴더를 같은 스킬 디렉터리에 설치해야 한다고 짧게 알리고 윤문을 시작하지 않는다. 본 지침 없이 기억에 의존해 윤문 결과를 만들지 않는다.
