"""지원하는 단순 YAML과 한 줄 dotenv의 키·추적 상태를 검사한다. 값은 출력하지 않는다."""
import argparse
import json
from pathlib import Path
import re
import subprocess

SECRET=re.compile(r'password|secret|token|api[_.-]?key',re.I)
DIRECT_SECRET=re.compile(r'''["']?([\w.-]*(?:PASSWORD|SECRET|TOKEN|API_KEY)[\w.-]*)["']?\s*[:=]\s*["']?([^"'\s,;]+)''',re.I)


def dotenv(path):
    result={}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        line=line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line=line[7:].lstrip()
        if '=' not in line:
            raise ValueError('KEY=value 형식 필요')
        key,value=line.split('=',1)
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',key):
            raise ValueError('변수 이름 형식 확인 필요')
        if key in result:
            raise ValueError('중복 키 '+key)
        value=value.strip()
        if value.startswith(('"',"'")):
            quote=value[0]
            end=value.find(quote,1)
            if end<0 or (value[end+1:].strip() and not value[end+1:].lstrip().startswith('#')):
                raise ValueError('한 줄 따옴표 형식 확인 필요')
            value=value[1:end]
        else:
            value=value.split('#',1)[0].rstrip()
        result[key]=value
    return result


def yaml_flat(path):
    # 예시 범위: 공백 들여쓰기 + key: value. 앵커·배열·복수 문서는 거부한다.
    result={}; stack=[]
    lines=[raw for raw in path.read_text(encoding='utf-8-sig').splitlines() if raw.strip() and not raw.lstrip().startswith('#')]
    for index,raw in enumerate(lines):
        if '\t' in raw or raw.strip()=='---':
            raise ValueError('단순 YAML 범위 밖')
        match=re.fullmatch(r'( *)([A-Za-z0-9_-]+):\s*(.*)',raw)
        if not match:
            raise ValueError('지원하지 않는 YAML 문법')
        indent=len(match[1]); key=match[2]; value=match[3].strip()
        if value.startswith(('"',"'")):
            quote=value[0]; end=value.find(quote,1)
            if end<0 or (value[end+1:].strip() and not value[end+1:].lstrip().startswith('#')):
                raise ValueError('한 줄 YAML 따옴표 확인 필요')
            value=value[1:end]
        else:
            value=value.split('#',1)[0].rstrip()
        while stack and stack[-1][0]>=indent:
            stack.pop()
        full='.'.join([s[1] for s in stack]+[key])
        if not value:
            next_indent=(len(lines[index+1])-len(lines[index+1].lstrip(' '))) if index+1<len(lines) else -1
            if next_indent>indent:
                stack.append((indent,key))
            else:
                if full in result:
                    raise ValueError('중복 키 '+full)
                result[full]=''
            continue
        if value.startswith(('[','{','&','*','|','>')) and not value.startswith('${'):
            raise ValueError('단순 YAML 범위 밖')
        if full in result:
            raise ValueError('중복 키 '+full)
        result[full]=value
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('kind',choices=['spring','node'])
    ap.add_argument('--root',type=Path,help='복사한 프로젝트 설정 폴더')
    args=ap.parse_args()
    base=Path(__file__).resolve().parent
    root=(args.root or base/args.kind).resolve()
    errors=[]
    try:
        schema=json.loads((base/'schema.json').read_text(encoding='utf-8-sig'))[args.kind]
        if not isinstance(schema,list) or not all(isinstance(key,str) for key in schema):
            raise ValueError('키 목록 형식')
        if len(schema)!=len(set(schema)):
            raise ValueError('중복 키')
        expected=set(schema)
    except (OSError,ValueError,KeyError,TypeError):
        print('실패 | schema.json을 읽을 수 없거나 키 목록 형식이 잘못됐습니다.')
        print('고치는 방법 | schema.json의 환경별 키 목록을 확인하세요.')
        return 1

    def inspect(path,allow_fake=False,merge=None,compare=True):
        if not path.is_file():
            errors.append(path.name+': 파일 누락'); return {}
        try:
            values=(yaml_flat if path.suffix=='.yml' else dotenv)(path)
            effective={**(merge or {}),**values}
            if compare and set(effective)!=expected:
                errors.append(path.name+': 키 누락 '+','.join(sorted(expected-set(effective)))+' / 초과 '+','.join(sorted(set(effective)-expected)))
            for key,value in values.items():
                if SECRET.search(key):
                    ref=bool(re.fullmatch(r'\$\{[A-Z_][A-Z0-9_]*\}',value))
                    if not ref and not (allow_fake and value=='CHANGE_ME'):
                        errors.append(path.name+': 직접 적힌 비밀값 의심 키 '+key)
            return values
        except (OSError,ValueError,UnicodeError) as exc:
            errors.append(path.name+': 형식 확인 필요 ('+type(exc).__name__+')'); return {}

    if args.kind=='spring':
        common=inspect(root/'application.yml',compare=False)
        for env in ('local','dev','prod'):
            inspect(root/f'application-{env}.yml',merge=common)
    else:
        inspect(root/'.env.example',allow_fake=True)
        for env in ('local','dev','prod'):
            inspect(root/f'.env.{env}.example',allow_fake=True)
        for env in ('local','dev'):
            path=root/f'.env.{env}'
            if path.exists():
                try:
                    keys=set(dotenv(path))
                    if keys!=expected:
                        errors.append(path.name+': 실제 값 파일 키 누락 또는 초과')
                except (OSError,ValueError,UnicodeError):
                    errors.append(path.name+': 실제 값 파일 형식 확인 필요')
        print('미실행 | 실제 prod 값 파일은 읽지 않았습니다. 운영 키는 사람이 예시와 대조하세요.')

    def scan_text(path_label,content):
        for line in content.splitlines():
            match=DIRECT_SECRET.search(line)
            if match and not match[2].startswith(('${','process.env.')) and match[2]!='CHANGE_ME':
                errors.append(path_label+': 직접 적힌 비밀값 의심 키 '+match[1])

    git_available=True
    try:
        git=subprocess.run(['git','-C',str(root),'rev-parse','--show-toplevel'],capture_output=True,text=True)
    except FileNotFoundError:
        git_available=False
    if not git_available or git.returncode:
        print('미실행 | Git 또는 Git 저장소가 없어 실제 값 파일의 커밋 여부는 확인하지 않았습니다.')
    else:
        top=Path(git.stdout.strip())
        proc=subprocess.run(['git','-C',str(top),'ls-files','-z','--',str(root)],capture_output=True)
        if proc.returncode:
            errors.append('Git 추적 파일 목록 확인 실패')
        for item in proc.stdout.decode('utf-8',errors='replace').split('\0'):
            if not item:
                continue
            path=top/item
            if path.name.startswith('.env') and path.name!='.env.example' and not path.name.endswith('.example'):
                errors.append(path.name+': 실제 값 파일이 Git 추적 중. 추적에서 제거하세요.')
                continue  # 실제 값 파일은 내용을 읽지 않는다.
            if path.suffix in ('.yml','.yaml','.properties','.json','.js','.ts') or path.name.endswith('.example'):
                try:
                    if path.is_file():
                        scan_text(path.name+' (작업 파일)',path.read_text(encoding='utf-8-sig'))
                    staged=subprocess.run(['git','-C',str(top),'show',':'+item],capture_output=True)
                    if staged.returncode:
                        errors.append(path.name+': Git 인덱스를 확인하지 못했습니다.')
                    else:
                        scan_text(path.name+' (Git 인덱스)',staged.stdout.decode('utf-8-sig'))
                except (OSError,UnicodeError):
                    errors.append(path.name+': 설정 파일을 읽을 수 없습니다.')
    for error in dict.fromkeys(errors):
        print('실패 | '+error)
    print('고치는 방법 | 파일 형식과 schema.json을 맞추고 비밀값은 환경 변수로 옮기세요. Git 인덱스도 갱신하세요.' if errors else '통과 | 검사한 키와 설정에서 문제 없음')
    print('범위 | 과거 Git 이력과 임의 코드 속 비밀값과 실제 운영 값은 보장하지 않습니다.')
    return 1 if errors else 0

if __name__=='__main__':
    raise SystemExit(main())
