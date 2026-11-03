# AGENTS.md

## 프로젝트
- 언어: Python 3.10 이상. 외부 패키지는 쓰지 않는다.
- 실행: python3 app.py (Windows: py -3 app.py)
- 기본 검사: python3 ../checks/check.py (Windows: py -3 ../checks/check.py)

## 작업 전에 읽을 문서
- 디렉터리와 함수 계약: docs/structure.md
- 코딩 규칙: docs/conventions.md
- 과거 실수: docs/mistakes.md

## 절대 금지
- ../checks/를 고치지 않는다.
- 실제 비밀 값을 코드에 쓰지 않는다.

## 완료 보고
- 전체 검사: python3 ../checks/check.py --full (Windows: py -3 ../checks/check.py --full)
- 전체 검사를 실행해 통과해야 완료를 보고한다. 미실행은 미실행으로 보고한다.
- 수정은 검사 실패 뒤 재수정 최대 2회다. 넘으면 멈추고 시도와 실패 원인을 보고한다.
- 새 대화에서도 docs/mistakes.md의 규칙을 적용한다.
