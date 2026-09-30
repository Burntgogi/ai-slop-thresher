# 익명 출력 쌍 판정

source/request에 대해 left와 right의 실제 출력만 판단한다. 어느 것이 새 버전인지 추측하지 않는다. 문장이 다르다는 이유만으로 승패를 만들지 않는다.

각 출력의 semantic_pass는 행위자·사실·수치·시점·인과·명제 강도·부정·정정·책임·피해·조건·배타 범위·의무·불확실성·저자 평가·직접 인용을 보존했는지 나타낸다. 원문에 없는 사실이나 안심을 추가하거나 모호한 고유 명제를 삭제하면 실패다. 이미 뒤에서 온전히 전달한 반복 수사만 덜어내는 것은 실패가 아니다. 의미 차이가 의심되면 source와 output의 실제 구간을 근거로 쓴다.

request_pass는 본문만/진단만/비교, 말투와 지정 Markdown·번호·코드 등 형식 요청을 지켰는지 나타낸다. 진단/비교 요청에서는 source의 모든 명제를 다시 작성할 의무가 없으므로 semantic_pass는 해당 응답에 사실 왜곡·추가가 없는지를 검사한다. 꾸밈 없는 원문을 그대로 반환해도 요청과 의미에 맞으면 통과다.

style_winner는 두 출력 모두 semantic_pass와 request_pass가 true일 때만 left/right/tie로 판단한다. 자연스러운 한국어, 군더더기 제거, 불필요한 부정·재정의 또는 문제 축소 수사를 덜었는지가 기준이다. 실제 정정·책임·조건·유보나 저자 평가의 부정을 남긴 것을 불필요한 수사로 벌점 주지 않는다. 두 출력이 같거나 우열 근거가 부족하면 tie, 어느 한쪽이 의미/요청에 실패하면 not_comparable이다. 길이가 짧다는 이유만으로 우세를 부여하지 않는다.

출력 스키마는 JSON 배열이며 각 항목은 다음과 같다.

```json
{"pair_id":"P1-01","case_id":"N01","left":{"semantic_pass":true,"request_pass":true,"issues":[],"evidence":"source/output의 관련 구간과 짧은 판단"},"right":{"semantic_pass":true,"request_pass":true,"issues":[],"evidence":"관련 구간과 짧은 판단"},"style_winner":"tie","style_reason":"실제 비교 근거"}
```

스킬 지침이나 다른 평가자의 판단을 읽지 않는다. 상투어를 출력했는지와 의미를 바꿨는지를 구별한다. 실행하지 않은 검사와 성능 수치는 만들지 않는다.
