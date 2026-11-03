from src.auth import signup, login

def main():
    action = input('1: 회원가입 / 2: 로그인 / q: 종료 > ')
    if action == 'q':
        return
    if action not in ('1', '2'):
        print('1 또는 2를 입력하세요.')
        return
    email = input('합성 이메일 > ')
    password = input('합성 비밀번호 > ')
    result = (signup if action == '1' else login)(email, password)
    print('성공' if result else '거부')

if __name__ == '__main__':
    main()
