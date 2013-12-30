# coding=utf-8

import sys
import commands
import os
import pwd
import string
import shutil
import struct
import glob
import logging

import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import os

from google_drive_authentication import *

from datetime import datetime


reload(sys)
sys.setdefaultencoding('utf-8')



#setting
TEST_MODE = False

album = u'걸어다니며 듣기'
artist = u'걸어다니며 듣기'
genre = u'Voice'
iTunesPlayList = u'걸어다니며 듣기'

TODAY_DATE = str(datetime.now().strftime('%Y%m%d'))
TODAY_TIME = str(datetime.now().strftime('%H%M%S'))
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

##

def convertToVoice(filename, full_content):
    cmd = 'say -o ./\'' + filename + '\' \'' + full_content + '\''
    result = commands.getstatusoutput(cmd)
    if result[0] == 0:
        return True
    else:
        return False


def getFFmpegEncodingCommand(aiff_filename, mp3_filename):
    cmd = ''
    cmd = './ffmpeg -y -i "' + aiff_filename \
          + '" -f mp3 -acodec libmp3lame -ab 320000 -ar 44100 "' + TEMP_FILE + '"'
    return cmd

def getFFmpegConcatCommand(mp3_filename, title, album, artist, genre):
    cmd = ''
    cmd = './ffmpeg -i "concat:' + TEMP_FILE + '|' + EFFECT_FILE \
          + '" -f mp3 -acodec libmp3lame -ab 48000 -ar 22050 ' \
          + ' -metadata title="' + escape_characters(title) + '"' \
          + ' -metadata album="' + album + '"' \
          + ' -metadata artist="' + artist + '"' \
          + ' -metadata TIT1="' + album + '"' \
          + ' -metadata genre="' + genre + '"' \
          + ' -metadata TIT3="' + mp3_filename + '"' \
          + ' "./' + mp3_filename + '"'
    return cmd

def runFFmpegCommand(cmd):
    # ffmpeg를 실행한다. 실행하기 전에 파일 유무를 확인하는 것이 좋겠다.
    print cmd
    result = commands.getstatusoutput(cmd)
    if result[0] == 0:
        return True
    else:
        return result[1]

def cleanupBeforeStart():
    try:
        os.remove(TEMP_FILE)
    except OSError:
        return False
    return True

def removeAIFF(aiff_filename):
    try:
        os.remove(aiff_filename)
    except OSError:
        return False
    return True

def getUserName():
    return pwd.getpwuid(os.getuid())[0]
def addVoiceToItunesLibrary(mp3_filename):
    source = './' + mp3_filename
    distnation = '/Users/' + getUserName() \
                           + '/Music/iTunes/iTunes Media/' \
                           + 'Automatically Add to iTunes.localized'
    shutil.move(source, distnation)


def moveToResultDirectory(mp3_filename):
    source = './' + mp3_filename
    distnation = RESULT_DIR + mp3_filename
    shutil.move(source, distnation)
    return True # 임시; 실제로 파일이 있는지 확인한 다음에 리턴할 것.


def escape_characters(s):
    for char in [':', '.', '\\', '!', '/', '#', '&', '*', '(', ')', '{', '}', 
                 '[', ']', '@', '$', '?', '^', '"', ',', '\'', '\t', '\n', '`']:
        if char in s:
            s = s.replace(char, '')

    return s


def correctWords(gd, full_content):
    rows = gd.getCorrectRows()

    for sheet in rows:
        if sheet.content.text == None:
            correct_to = ''
        else:
            correct_to = sheet.content.text.split(':')[1].strip()
        full_content = string.replace(full_content, sheet.title.text, correct_to)
        # print 'full_content = string.replace(full_content, ' + sheet.title.text + ', ' + sheet.content.text.split(':')[1].strip() + ')'

    return full_content


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


class GoogleDocs:
    def __init__(self):
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        self.gd_client.email = getGoogleAccountName()
        self.gd_client.password = getGoogleAccountPassword()
        self.gd_client.source = getApplicationName()
        self.gd_client.ProgrammaticLogin()

    def getContentsRows(self):
        spreadsheet_key = getSpreadsheetKey()
        worksheet_id = getContentsWorksheetKey()
        return self.gd_client.GetListFeed(spreadsheet_key, worksheet_id).entry

    def getCorrectRows(self):
        spreadsheet_key = getSpreadsheetKey()
        worksheet_key = getCorrectWorksheetKey()
        return self.gd_client.GetListFeed(spreadsheet_key, worksheet_key).entry

    def updateRow(self, entry, new_row_data):
        self.gd_client.UpdateRow(entry, new_row_data)


def run():
    count = 2

    gd = GoogleDocs()

    for row in gd.getContentsRows(): 
        print str(count) + '. ' + row.custom[COLUMN_NAME_TITLE].text

        source = row.custom[COLUMN_NAME_SOURCE].text
        title = escape_characters(row.custom[COLUMN_NAME_TITLE].text)
        full_content = title + ', ' + escape_characters(row.custom[COLUMN_NAME_CONTENT].text)

        if row.custom[COLUMN_NAME_CONVERTED].text == None:
            cleanupBeforeStart()

            mp3_filename = TODAY_DATE + ' ' + escape_characters(title) + '.' + EXTENSION_MP3
            aiff_filename = TODAY_DATE + ' ' + escape_characters(title) + '.' + EXTENSION_AIFF

            full_content = correctWords(gd, full_content)

            if convertToVoice(aiff_filename, full_content) == False:
                logging.warning('FAILED: convertToVoice(' + aiff_filename + ', ' + full_content + ')')
                sys.exit()

            # 인코딩
            cmd = getFFmpegEncodingCommand(aiff_filename, mp3_filename)
            result = runFFmpegCommand(cmd)
            if result == False:
                logging.warning('FAILED: runFFmpegCommand(' + cmd + ')')
                logging.warning('FAILED: runFFmpegCommand(' + str(result) + ')')
                sys.exit()

            # 끝에 이펙트 연결
            cmd = getFFmpegConcatCommand(mp3_filename, title, album,artist, genre)
            if runFFmpegCommand(cmd) == False:
                logging.warning('FAILED: runFFmpegCommand(' + cmd + ')')
                sys.exit()

            if removeAIFF(aiff_filename) == False:
                logging.warning('FAILED: removeAIFF(' + aiff_filename + ')')
                sys.exit()        
            if moveToResultDirectory(mp3_filename) == False:
                logging.warning('FAILED: moveToResultDirectory(' + mp3_filename + ')')
                sys.exit()

            if TEST_MODE == False:
                addVoiceToItunesLibrary(RESULT_DIR + mp3_filename)

                new_row_data = {}
                new_row_data[COLUMN_NAME_SOURCE] = row.custom[COLUMN_NAME_SOURCE].text
                new_row_data[COLUMN_NAME_TITLE] = row.custom[COLUMN_NAME_TITLE].text
                new_row_data[COLUMN_NAME_CONTENT] = row.custom[COLUMN_NAME_CONTENT].text
                new_row_data[COLUMN_NAME_TIMESTAMP] = row.custom[COLUMN_NAME_TIMESTAMP].text
                new_row_data[COLUMN_NAME_CONVERTED] = 'O'
                
                gd.updateRow(row, new_row_data)

        else:
            logging.warning('Already converted: Skipped')

        count = count + 1

run()