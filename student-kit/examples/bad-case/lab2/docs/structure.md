# 디렉터리와 함수 계약

- 실행 입구는 app.py다. 사용자 입력과 결과 출력은 여기서 맡는다.
- src/auth.py에 signup(email, password)와 login(email, password)을 둔다.
- 두 함수는 문자열 두 개를 받아 성공하면 True 실패하면 False를 반환한다.
- 회원은 data/users.json에 저장한다. 파일 형식은 구현이 정한다.
- data/users.json은 실행 폴더 기준이나 프로젝트 루트 기준 모두 가능하다.
- src/에서는 사용자 입력을 받지 않는다. app.py를 import해도 입력을 받지 않는다.
- checks/check.py는 기본 검사다. 작업 폴더에서 실행한다.
- 전체 검사가 있는 시작본에서는 python3 checks/check.py --full을 쓴다.
- Windows는 python3 대신 py -3을 쓴다.
