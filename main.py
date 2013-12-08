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
import logging

from datetime import datetime

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
RESULT_DIR = './results/'

EXTENSION_MP3 = 'mp3'
EXTENSION_AIFF = 'aiff'

##

def convertToVoice(filename, full_content):
    cmd = 'say -o ./\'' + filename + '\' \'' + full_content + '\''
    result = commands.getstatusoutput(cmd)
    if result[0] == 0:
        return True
    else:
        return False

def getFFmpegBaseCommand(title, aiff_filename):
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


def runFFmpegCommand(cmd):
    #ffmpeg 커맨드를 실행한다. 부디 같은 디렉토리 안에 있기를 바래요.
    result = commands.getstatusoutput(cmd)
    if result[0] == 0:
        return True
    else:
        return False


def removeAIFF(aiff_filename):
    try:
        os.remove(aiff_filename)
    except OSError:
        return False
    return True

def addVoiceToItunesLibrary(mp3_filename):
    source = './' + mp3_filename
    distnation = '/Users/neoocean/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized'
    shutil.move(source, distnation)
    # 파일이 곧 사라지기 때문에 리턴을 체크하면 안됨. 차라리 직접 아이튠즈 라이브러리를 검색하면?

def moveToResultDirectory(mp3_filename):
    source = './' + mp3_filename
    distnation = RESULT_DIR + mp3_filename
    shutil.move(source, distnation)
    return True # 임시; 실제로 파일이 있는지 확인한 다음에 리턴할 것.

def escape_characters_content_text(s):
    """ 본문에서 csv 파일에 문제를 일으키는 문자를 제거.
    """
    s = string.replace(s, '"', '')
    s = string.replace(s, '\'', '')
    #s = string.replace(s, ',', '')
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
    full_content = string.replace(full_content, 'OS/2', '오에스투')
    full_content = string.replace(full_content, '8086', '팔공팔육')
    full_content = string.replace(full_content, '80286', '팔공이팔육')
    full_content = string.replace(full_content, '80386', '팔공삼팔육')
    full_content = string.replace(full_content, '80486', '팔공사팔육')
    full_content = string.replace(full_content, '386칩', '삼팔육칩')
    full_content = string.replace(full_content, '386용', '삼팔육용')
    full_content = string.replace(full_content, '386의', '삼팔육의')
    full_content = string.replace(full_content, '386은', '삼팔육은')
    # full_content = string.replace(full_content, '', '')
    return full_content


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def saveConvertedContent(hashed):
    """ 변환한 데이터의 해시를 받아 파일에 추가한다.
    """
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


def getHash(source):
    h = hashlib.new('sha256')
    h.update(source)
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

            hashed = getHash(source)

            full_content = title + '......' + \
                           escape_characters_content_text(row[3])

            if searchConvertedContent(hashed) == False:
                mp3_filename = TODAY_DATE + ' ' + \
                               escape_characters(title) + \
                               '.' + EXTENSION_MP3
                aiff_filename = TODAY_DATE + ' ' + \
                                escape_characters(title) + \
                                '.' + EXTENSION_AIFF

                full_content = correctWords(full_content)

                if convertToVoice(aiff_filename, full_content) == False:
                    logging.warning('FAILED: convertToVoice(' + \
                                    aiff_filename + ', ' + full_content + ')')
                    sys.exit()

                base_cmd = getFFmpegBaseCommand(title, aiff_filename)
                meta_cmd = getFFmpegMetaCommand(title, album, artist, 
                                                genre, mp3_filename)
                cmd = base_cmd + meta_cmd + ' \'' + mp3_filename + '\''
                if runFFmpegCommand(cmd) == False:
                    logging.warning('FAILED: runFFmpegCommand(' + cmd + ')')
                    sys.exit()

                if removeAIFF(aiff_filename) == False:
                    logging.warning('FAILED: removeAIFF(' + aiff_filename + ')')
                    sys.exit()
                
                if moveToResultDirectory(mp3_filename) == False:
                    logging.warning('FAILED: moveToResultDirectory(' + mp3_filename + ')')
                    sys.exit()

                addVoiceToItunesLibrary(RESULT_DIR + mp3_filename)
                saveConvertedContent(hashed)

                # ~ if searchConvertedContent
            else:
                logging.warning('Already converted: Skipped')
            
            count = count + 1

