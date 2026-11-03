## 환경별 변수
- 코드는 환경 이름으로 분기하지 않고 변수만 읽는다.
- 비밀값은 코드와 커밋되는 파일에 쓰지 않는다.
- 변수를 더하면 schema.json과 모든 환경과 예시 파일에 함께 더한다.
- 운영 값을 읽거나 바꾸지 않는다. 운영 값은 사람이 넣는다.
- 완료 보고 전에 python3 check_env.py node 또는 python3 check_env.py spring을 실행한다.
- Windows는 python3 대신 py -3을 쓴다.
