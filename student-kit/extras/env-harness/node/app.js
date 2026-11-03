// 예시: 환경 이름 분기 없이 변수만 읽습니다. 비밀값은 출력하지 않습니다.
const port = Number(process.env.APP_PORT);
if (!Number.isInteger(port) || !process.env.DB_URL || !process.env.DB_PASSWORD) {
  throw new Error('필수 환경 변수 누락');
}
console.log(`설정 확인: port=${port}`);
