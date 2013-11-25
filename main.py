# coding=utf-8

# import csv
import sys
import commands
import os
import string
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf-8')


d = datetime.now()
filename = str(d.strftime('%Y%m%d-%H%M%S')) + '.aiff'



# 제목과 내용을 묻는다.
# title = raw_input('Title: ')
# content = raw_input('Content: ')
title = '제목:::::!'
content = '내용'

def escape_characters(s):
    s = string.replace(s, ':', '')
    s = string.replace(s, '\\', '')
    s = string.replace(s, '!', '')
    s = string.replace(s, '/', '')
    s = string.replace(s, '#', '')
    s = string.replace(s, '&', '')
    s = string.replace(s, '*', '')
    s = string.replace(s, '(', '')
    s = string.replace(s, ')', '')
    s = string.replace(s, '{', '')
    s = string.replace(s, '}', '')
    s = string.replace(s, '@', '')
    s = string.replace(s, '$', '')
    s = string.replace(s, '^', '')
    s = string.replace(s, ' ', '')
    return s

title = escape_characters(title)
full_content = title + '.....' + content


# 커맨드를 실행해 파일로 만든다.
result = commands.getstatusoutput('say -o ./' + filename + ' ' + full_content)
if result[0] == 0:
    print 'Converted as ' + filename
else:
    print 'Error to converting. Code: ' + str(result[0])
    print 'Message: ' + str(result[1])

# 파일 이름을 내가 쓰는 규칙대로 바꾼다.
new_filename = str(d.strftime('%Y%m%d')) + ' ' + title + '.aiff'
os.rename(filename, new_filename)
print 'Renamed as ' + new_filename

# mp3 형식으로 컨버팅한다.
m4a_filename = str(d.strftime('%Y%m%d')) + ' ' + title + '.mp3'
result = commands.getstatusoutput('./ffmpeg -i \'' + new_filename + \
    '\' -f mp3 -acodec libmp3lame -ab 48000 -ar 22050 \'' + m4a_filename + '\'')
if result[0] == 0:
    print 'Converted as ' + filename
else:
    print 'Error to converting. Code: ' + str(result[0])
    print 'Message: ' + str(result[1])

# 메타데이터를 입력한다.


# aiff 파일을 삭제한다.


# 파일을 내가 쓰는 디렉토리로 옮긴다.
# .. 이건 아직.

# 지정된 아이튠즈 라이브러리에 등록한다. (오토메이터를 조금 사용해야 할까?)
