# coding=utf-8

# import csv
import sys
import commands
import os
import string
import shutil
import struct
import csv

from datetime import datetime
# from Foundation import *
# from ScriptingBridge import *

reload(sys)
sys.setdefaultencoding('utf-8')

#setting
album = '걸어다니며 듣기'
artist = '걸어다니며 듣기'
genre = 'Voice'
iTunesPlayList = '걸어다니며 듣기'


##


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
    s = string.replace(s, '"', '')
    s = string.replace(s, '\'', '')
    return s



d = datetime.now()
filename = str(d.strftime('%Y%m%d-%H%M%S')) + '.aiff'


# 제목과 내용을 csv 파일로부터 읽는다.
with open('list.csv', 'rb') as c:
    reader = csv.reader(c)
    next(reader, None)
    for row in reader:
        if row[0] != '':
            title = escape_characters(row[2])
            full_content = title + '......' + row[3]
            print title
            print full_content


# 어 잠깐. csv 읽기 전에 반복할 수 있게 만들어 놨어야지;
sys.exit()



# 커맨드를 실행해 파일로 만든다.
cmd = 'say -o ./\'' + filename + '\' \'' + full_content + '\''
result = commands.getstatusoutput(cmd)
if result[0] == 0:
    print 'Converted as ' + filename
else:
    print 'Error to converting. Code: ' + str(result[0])
    print 'Message: ' + str(result[1])
    print 'Command: ' + cmd

# 파일 이름을 내가 쓰는 규칙대로 바꾼다.
aiff_filename = str(d.strftime('%Y%m%d')) + ' ' + \
    escape_characters(title) + '.aiff'
os.rename(filename, aiff_filename)
print 'Renamed as ' + aiff_filename


# mp3 형식으로 컨버팅하는 ffmpeg 커맨드를 준비한다.
mp3_filename = str(d.strftime('%Y%m%d')) + ' ' + title + '.mp3'
cmd = './ffmpeg -y -i \'' + aiff_filename + \
    '\' -f mp3 -acodec libmp3lame -ab 48000 -ar 22050'

# 메타데이터를 입력하는 ffmpeg 커맨드를 준비한다.
# http://jonhall.info/how_to/create_id3_tags_using_ffmpeg
cmd = cmd + ' -metadata artist=\'\''
cmd = cmd + ' -metadata title=\'' + escape_characters(title) + '\''
cmd = cmd + ' -metadata album=\'' + album + '\''
cmd = cmd + ' -metadata artist=\'' + artist + '\''
cmd = cmd + ' -metadata TIT1=\'' + album + '\'' # itunes groupping
cmd = cmd + ' -metadata genre=\'' + genre + '\''
cmd = cmd + ' -metadata TIT3=\'' + mp3_filename + '\''


# 커맨드 끝에 출력 파일 이름을 붙인다.
cmd = cmd + ' \'' + mp3_filename + '\''

result = commands.getstatusoutput(cmd)
if result[0] == 0:
    print 'Converted as ' + mp3_filename
else:
    print 'Error to converting. Code: ' + str(result[0])
    print 'Message: ' + str(result[1])
    print 'Command: ' + cmd

# aiff 파일을 삭제한다.
try:
    os.remove(aiff_filename)
except OSError:
    pass

# 파일을 아이튠즈에 추가한다.
src = './' + mp3_filename
dst = '/Users/neoocean/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized'
shutil.move(src, dst)



# 끝?

