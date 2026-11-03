"""읽을 책 목록. 하네스 없는 개인용 예시."""
import json
from pathlib import Path
STORE=Path('books.json')

def main():
    books=json.loads(STORE.read_text(encoding='utf-8')) if STORE.exists() else []
    title=input('추가할 책 제목 > ')
    books.append(title)
    STORE.write_text(json.dumps(books,ensure_ascii=False),encoding='utf-8')
    print('저장된 책:',len(books))

if __name__=='__main__':
    main()
