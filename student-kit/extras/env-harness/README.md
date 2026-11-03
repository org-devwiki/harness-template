# 환경별 변수 하네스

수업 뒤 자기 프로젝트에 복사할 부록입니다. Java와 Node는 수업 준비물이 아닙니다.

1. AGENTS-fragment.md의 규칙을 자기 AGENTS.md에 붙입니다. 다른 도구라면 그 도구의 지침 파일에 붙입니다.
2. check_env.py와 schema.json을 프로젝트에 복사합니다. schema.json의 키는 자기 프로젝트에 맞게 수정합니다.
3. Spring은 spring/의 application*.yml을 src/main/resources/에 복사합니다. Node는 node/의 .env*.example과 .gitignore 규칙을 루트에 복사합니다.
4. 검사할 때 아래 --root를 실제 설정 폴더 경로로 바꿉니다.

| 용도 | macOS | Windows |
|---|---|---|
| Spring 검사 | python3 check_env.py spring --root spring | py -3 check_env.py spring --root spring |
| Node 검사 | python3 check_env.py node --root node | py -3 check_env.py node --root node |

Node는 .env.local.example을 .env.local로 복사해 값을 사람이 넣습니다. dev도 같습니다. `.env.<환경>`은 커밋하지 않습니다. 운영 값은 사람이 별도로 넣으며 에이전트는 읽거나 바꾸지 않습니다. Node 20.6 이상에서 `node --env-file=.env.local app.js`로 선택합니다. 기본 예시의 값은 가짜입니다.

Spring은 공통값을 application.yml에 두고 환경값은 application-local.yml처럼 나눕니다. macOS 터미널은 `export SPRING_PROFILES_ACTIVE=local`, Windows PowerShell은 `$env:SPRING_PROFILES_ACTIVE="local"`로 고릅니다. DB_URL과 DB_PASSWORD 등 실제 값은 사람이 환경 변수로 넣고 기존 프로젝트 실행 명령을 씁니다. 코드는 환경 이름으로 분기하지 않습니다.

에이전트 입력:
> AGENTS.md의 환경별 변수 규칙을 읽고 설정만 정리해 줘. 코드는 환경 이름으로 분기하지 마. 운영 값 파일은 읽거나 바꾸지 마. schema.json과 모든 환경 예시의 키를 맞추고 check_env.py를 실행한 결과를 보고해 줘.

지침은 부탁입니다. 운영 접근은 샌드박스와 계정 권한으로 막아야 합니다. 검사기는 키와 현재 Git 추적 상태와 작업 파일·Git 인덱스의 정해진 비밀값 패턴만 봅니다. Git 실행 파일이나 Git 저장소가 없으면 커밋 여부는 미실행으로 표시합니다. Git 전체 이력이나 모든 비밀값을 찾는 도구가 아닙니다.

검사기는 예시의 단순 YAML과 한 줄 dotenv만 지원합니다. Spring에서는 공통값과 프로필 값을 합쳐 키를 비교합니다. Node에서는 공통·환경별 예시와 존재하는 local·dev 실제 파일의 키를 비교합니다. 실제 prod 파일은 읽지 않습니다. 운영 키 점검은 사람이 예시와 대조합니다. 값은 출력하지 않습니다. 실제 값 파일이 Git 추적 중이면 실패합니다.

공식 문서 확인: [Spring 외부 설정](https://docs.spring.io/spring-boot/reference/features/external-config.html), [Spring 프로필](https://docs.spring.io/spring-boot/reference/features/profiles.html), [Node --env-file](https://nodejs.org/api/cli.html#--env-filefile).
