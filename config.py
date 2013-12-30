# coding=utf-8

# mp3 파일의 엘범, 아티스트, 장르 설정: 
album = u'걸어다니며 듣기'
artist = u'걸어다니며 듣기'
genre = u'Voice'

# 구글 아이디, 패스워드, 스프레드시트 주소 뒷부분: 
configGoogleAccountName = ''
configGoogleAccountPassword = ''
configSpreadsheetKey = ''

# 'help.py'를 실행해서 나온 결과를 추가: 
configCorrectWorksheetKey = ''
configContentsWorksheetKey = ''


# 여기부터는 안 건드려도 됩니다: 
configApplicationName = 'listen-while-walking'

from datetime import datetime
TODAY_DATE = str(datetime.now().strftime('%Y%m%d'))
RESULT_DIR = './results/'

EXTENSION_MP3 = 'mp3'
EXTENSION_AIFF = 'aiff'

COLUMN_NAME_TIMESTAMP = u'타임스탬프'
COLUMN_NAME_SOURCE = u'주소'
COLUMN_NAME_TITLE = u'제목'
COLUMN_NAME_CONTENT = u'내용'
COLUMN_NAME_CORRECT_FROM = u'찾을 단어'
COLUMN_NAME_CORRECT_TO = u'고칠 단어'
COLUMN_NAME_CONVERTED = u'변환됨'

EFFECT_FILE = 'page-flip-10.' + EXTENSION_MP3
TEMP_FILE = 'output.' + EXTENSION_MP3