# coding=utf-8

import sys
import commands
import os
import string
import shutil
import struct
import csv
import hashlib
import glob

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

d = datetime.now()
TODAY_DATE = str(d.strftime('%Y%m%d'))
TODAY_TIME = str(d.strftime('%H%M%S'))
CONVERTED_FILE = './converted.csv'
CONTENT_FILE = './list.csv'

EXTENSION_MP3 = 'mp3'
EXTENSION_AIFF = 'aiff'

##

def convertToVoice(filename, full_content):
    # 커맨드를 실행해 파일로 만든다.
    cmd = 'say -o ./\'' + filename + '\' \'' + full_content + '\''
    result = commands.getstatusoutput(cmd)
    if result[0] == 0:
        print 'Converted as ' + filename
    else:
        print 'Error to converting. Code: ' + str(result[0])
        print 'Message: ' + str(result[1])
        print 'Command: ' + cmd


def renameVoice(title):
    # 파일 이름을 내가 쓰는 규칙대로 바꾼다.
    aiff_filename = TODAY_DATE + ' ' + \
        escape_characters(title) + '.' + EXTENSION_AIFF
    os.rename(filename, aiff_filename)
    print 'Renamed as ' + aiff_filename


def getFfmpegBaseCommand(title, aiff_filename):
    # mp3 형식으로 컨버팅하는 ffmpeg 커맨드를 준비한다.
    mp3_filename = TODAY_DATE + ' ' + title + '.' + EXTENSION_MP3
    cmd = './ffmpeg -y -i \'' + aiff_filename + \
        '\' -f mp3 -acodec libmp3lame -ab 48000 -ar 22050'
    return cmd


def getFfmpegMetaCommand(title, album, artist, genre, mp3_filename):
    # 메타데이터를 입력하는 ffmpeg 커맨드를 준비한다.
    # http://jonhall.info/how_to/create_id3_tags_using_ffmpeg
    cmd = ''
    cmd = cmd + ' -metadata artist=\'\''
    cmd = cmd + ' -metadata title=\'' + escape_characters(title) + '\''
    cmd = cmd + ' -metadata album=\'' + album + '\''
    cmd = cmd + ' -metadata artist=\'' + artist + '\''
    cmd = cmd + ' -metadata TIT1=\'' + album + '\'' # itunes groupping
    cmd = cmd + ' -metadata genre=\'' + genre + '\''
    cmd = cmd + ' -metadata TIT3=\'' + mp3_filename + '\''
    return cmd


def runFfmpegCommand(cmd):
    #ffmpeg 커맨드를 실행한다. 부디 같은 디렉토리 안에 있기를 바래요.
    result = commands.getstatusoutput(cmd)
    if result[0] == 0:
        print 'Converted as ' + mp3_filename
    else:
        print 'Error to converting. Code: ' + str(result[0])
        print 'Message: ' + str(result[1])
        print 'Command: ' + cmd


def removeAIFF(aiff_filename):
    try:
        os.remove(aiff_filename)
        print 'Removed: ' + aiff_filename
    except OSError:
        pass

def addVoiceToItunesLibrary(mp3_filename):
    # 파일을 아이튠즈에 추가한다.
    src = './' + mp3_filename
    # dist 경로를 얻어올 방법이 필요해요.
    dist = '/Users/neoocean/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized'
    shutil.move(src, dist)

def moveToResultDirectory(mp3_filename):
    # 완성된 파일을 Result 디렉토리로 옮겨놓는다.
    src = './' + mp3_filename
    dist = './results/' + mp3_filename
    shutil.move(src, dist)

def escape_characters_content_text(s):
    """ 본문에서 csv 파일에 문제를 일으키는 문자를 제거.
    """
    s = string.replace(s, '"', '')
    s = string.replace(s, '\'', '')
    return s

def escape_characters(s):
    s = string.replace(s, ':', '')
    s = string.replace(s, '.', '')
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
    s = string.replace(s, '?', '')
    s = string.replace(s, '^', '')
    s = string.replace(s, '"', '')
    s = string.replace(s, '\'', '')
    return s


def correctWords(full_content):
    # 이제 그 동안 거슬리게 들리던 발음을 마음에 들도록 교정한 다음 음성으로 만듭시다.
    full_content = string.replace(full_content, 'CIA', '씨아이에이')
    return full_content

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def saveConvertedContent(hashed):
    if os.path.isfile(CONVERTED_FILE) == False:
        touch(CONVERTED_FILE)
    with open(CONVERTED_FILE, 'ab') as f:
        r = csv.writer(f, delimiter = ',')
        r.writerow([str(hashed)])


def searchConvertedContent(hashed):
    """ 해시를 받아 converted.csv 파일에서 검색한 결과를 돌려준다.
    """
    if os.path.isfile(CONVERTED_FILE) == False:
        return False
    with open(CONVERTED_FILE, 'rb') as c:
        reader = csv.reader(c)
        for row in reader:
            if str(row[0]) != hashed:
                pass
            else:
                return True
    return False


def cleanupBeforeStart():
    aiff = './*.' + EXTENSION_AIFF
    r = glob.glob(aiff)
    for i in r:
        os.remove(i)

    mp3 = './*.' + EXTENSION_MP3
    r = glob.glob(mp3)
    for i in r:
        os.remove(i)


def getHash(source, title, full_content):
    h = hashlib.new('sha256')
    h.update(source + title + full_content)
    return str(h.hexdigest())


# 제목과 내용을 csv 파일로부터 읽는다.
with open(CONTENT_FILE, 'rb') as c:
    reader = csv.reader(c)
    next(reader, None) # skip Header Row.
    count = 1
    for row in reader:
        if row[0] != '':
            print '\nProcessing Row: ' + str(count)
            cleanupBeforeStart()

            source = row[1]
            title = escape_characters(row[2])
            full_content = title + '......' + \
                           escape_characters_content_text(row[3])

            hashed = getHash(source, title, full_content)

            if searchConvertedContent(hashed) == False:
                mp3_filename = TODAY_DATE + ' ' + title + \
                               '.' + EXTENSION_MP3
                aiff_filename = TODAY_DATE + ' ' + \
                                escape_characters(title) + \
                                '.' + EXTENSION_AIFF

                full_content = correctWords(full_content)
                convertToVoice(TODAY_DATE + '-' + TODAY_TIME + \
                               '.' + EXTENSION_AIFF, full_content) 

                renameVoice(title)
                base_cmd = getFfmpegBaseCommand(title, aiff_filename)
                meta_cmd = getFfmpegMetaCommand(title, album, artist, 
                                                genre, mp3_filename)
                cmd = base_cmd + meta_cmd + ' \'' + mp3_filename + '\''
                runFfmpegCommand(cmd)
                removeAIFF(aiff_filename)
                moveToResultDirectory(mp3_filename)
                addVoiceToItunesLibrary('./results/' + mp3_filename)

                saveConvertedContent(hashed)

                # ~ if searchConvertedContent
            else:
                print 'Already converted Content: Skipped'
            
            count = count + 1

