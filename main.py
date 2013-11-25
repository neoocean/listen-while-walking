# coding=utf-8

# import csv
import sys
import commands
import os
import string
import shutil
import struct

from datetime import datetime
from Foundation import *
from ScriptingBridge import *


reload(sys)
sys.setdefaultencoding('utf-8')

#setting
album = '걸어다니며 듣기'
artist = '걸어다니며 듣기'
genre = 'Voice'
iTunesPlayList = '걸어다니며 듣기'


##



d = datetime.now()
filename = str(d.strftime('%Y%m%d-%H%M%S')) + '.aiff'



# 제목과 내용을 묻는다.
# title = raw_input('Title: ')
# content = raw_input('Content: ')
title = '새로운 제목:::::!'
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
    return s

title = escape_characters(title)
full_content = title + '.....' + content


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

# 일단 'iTunesPlayList'가 있는지 확인한다. 있으면 이걸 사용, 없으면 만들기.
iTunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")
playListFound = False
for playlist in iTunes.sources()[0].playlists():
    if playlist.name() == iTunesPlayList:
        playListFound = True
        targetPlayList = playlist
        print playlist.name() + ' found.'
        break
    else:
        pass
# 플레이리스트를 못 찾았으면 새로 만든다.
if playListFound == False:
    p = {'name':iTunesPlayList}
    playlist = iTunes.classForScriptingClass_("playlist").alloc().initWithProperties_(p)
    iTunes.sources()[0].playlists().insertObject_atIndex_(playlist, 0)

# 플레이리스트에 트랙을 추가한다.
# ?: 플레이리스트에 트랙을 추가하는 방법을 모르겠다.
#    http://stackoverflow.com/questions/12971306/how-to-add-a-track-to-an-itunes-playlist-using-python-and-scripting-bridge
#    여기를 보면 'iTunes.add_to_(track[1],newPlaylist)' 이렇게 추가하고 있는데, 
#    여기서 'track[1]' 이 어떻게 생긴 건지 모르겠다. 이걸 알면 재생목록에 바로 추가할 수 있을텐데.
# if playListFound == True:
#    l = {'name': mp3_filename}
#    track = iTunes.classForScriptingClass_("track").alloc().initWithProperties_(l)
#    iTunes.add_to_(track, targetPlayList)



