"""교육용 판정 도구. 현재 작업 폴더의 사본을 검사하며 보안 샌드박스는 아니다."""
import argparse
import ast
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile

WORKER = """
import importlib, json, sys
from pathlib import Path
root=Path.cwd()
sys.path[:0]=[str(root), str(root/'src')]
try:
    auth=importlib.import_module('src.auth')
    action,email,password=json.loads(sys.argv[1])
    fn=getattr(auth,action,None)
    if not callable(fn):
        raise ValueError('src/auth.py에 '+action+'(email, password) 함수가 필요합니다')
    result=fn(email,password)
    print('__RESULT__'+json.dumps({'bool':type(result) is bool,'value':result if type(result) is bool else None}))
except Exception as exc:
    print('__ERROR__'+type(exc).__name__+': '+str(exc))
    raise SystemExit(1)
"""


def main():
    parser=argparse.ArgumentParser(description='작업 폴더의 로그인을 판정합니다')
    parser.set_defaults(full=False)
    args=parser.parse_args()
    root=Path.cwd()
    failures=[]
    print('검사 | '+('전체 확인표' if args.full else '기본 확인표'))

    def report(name,ok,help_text):
        print(('통과' if ok else '실패')+' | '+name)
        if not ok:
            failures.append(name)
            print('  고치는 방법: '+help_text)

    missing=[p for p in ('app.py','src/auth.py','data/users.json') if not (root/p).is_file()]
    report('디렉터리와 파일',not missing,
           '작업 폴더를 확인하고 '+', '.join(missing)+'를 docs/structure.md에 맞춰 만드세요.')
    if missing:
        print('판정 중단 | 언어나 구조가 다르면 같은 검사로 비교할 수 없습니다.')
        return 1
    for source in (root/'app.py',root/'src/auth.py'):
        try:
            ast.parse(source.read_text(encoding='utf-8-sig'))
        except (OSError,SyntaxError,UnicodeError) as exc:
            report('Python 문법',False,str(source.relative_to(root))+'의 문법과 UTF-8 저장을 확인하세요. '+type(exc).__name__)
            return 1

    def scenario(name,actions,expected,plain=None):
        try:
            with tempfile.TemporaryDirectory(prefix='login-check-') as tmp:
                target=Path(tmp)/'app'
                shutil.copytree(root,target,ignore=shutil.ignore_patterns('checks','__pycache__','.git'),symlinks=False)
                # 저장 형식은 구현이 정한다. 초기 파일도 그대로 복사하여 사용한다.
                # 계정 충돌은 임의의 합성 계정으로 피하고 원본은 읽기만 한다.
                values=[]
                for action in actions:
                    proc=subprocess.run([sys.executable,'-B','-c',WORKER,json.dumps(action)],cwd=target,
                                        capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=8)
                    lines=[line[10:] for line in proc.stdout.splitlines() if line.startswith('__RESULT__')]
                    if proc.returncode or not lines:
                        errors=[line[9:] for line in proc.stdout.splitlines() if line.startswith('__ERROR__')]
                        raise ValueError('함수 실행 실패: '+(' / '.join(errors) or '함수의 예외와 bool 반환을 확인하세요'))
                    result=json.loads(lines[-1])
                    if not result['bool']:
                        raise ValueError('True 또는 False를 반환해야 합니다')
                    values.append(result['value'])
                ok=values==expected
                if plain:
                    saved=target/'data/users.json'
                    ok=ok and saved.is_file() and plain not in saved.read_text(encoding='utf-8')
            report(name,ok,'src/auth.py에서 이 항목을 처리하세요. 문서를 읽고 같은 검사를 다시 실행하세요.')
        except subprocess.TimeoutExpired:
            report(name,False,'함수 실행 대기 상한을 넘었습니다. src/의 입력 대기나 끝나지 않는 반복을 제거하세요.')
        except Exception as exc:
            report(name,False,str(exc)+'; 파일 경로와 함수 계약을 맞추세요.')

    email='learner-'+secrets.token_hex(8)+'@example.test'
    password='Synthetic-'+secrets.token_hex(12)+'!'
    scenario('새 이메일 가입 후 로그인 · 새 프로세스에서 저장 확인',
             [('signup',email,password),('login',email,password)],[True,True])
    scenario('틀린 비밀번호 거부',[('signup',email,password),('login',email,'Wrong-Pass-883!')],[True,False])
    if args.full:
        scenario('같은 이메일 재가입 거부',[('signup',email,password),('signup',email,'Other-Pass-669!'),('login',email,password)],[True,False,True])
        for field in ('email','password'):
            for action in ('signup','login'):
                for value in ('','   ','\t\n'):
                    e,p=(value,password) if field=='email' else (email,value)
                    actions=[('signup',email,password)] if action=='login' else []
                    scenario('빈 값 거부 · '+action+' · '+field+' '+repr(value),actions+[(action,e,p)],
                             ([True] if action=='login' else [])+[False])
        scenario('저장 파일에 비밀번호 원문 없음',[('signup',email,password)],[True],plain=password)
        try:
            debug=[]
            for source in (root/'src').rglob('*.py'):
                t=ast.parse(source.read_text(encoding='utf-8-sig'))
                if any(isinstance(n,ast.Call) and ((isinstance(n.func,ast.Name) and n.func.id=='print') or
                    (isinstance(n.func,ast.Attribute) and n.func.attr=='print')) for n in ast.walk(t)):
                    debug.append(str(source.relative_to(root)))
            report('코드에 디버그용 print 없음',not debug,'src/의 print를 제거하세요. 사용자 안내 출력은 app.py로 옮기세요. '+', '.join(debug))
        except Exception as exc:
            report('코드에 디버그용 print 없음',False,'src/의 문법을 확인하세요. '+str(exc))
    print('결과 | '+('전 항목 통과' if not failures else str(len(failures))+'항목 실패'))
    print('범위 | 교육용 확인표 판정입니다. 실제 서비스 안전성이나 지침을 읽은 사실은 보장하지 않습니다.')
    return 1 if failures else 0

if __name__=='__main__':
    raise SystemExit(main())
