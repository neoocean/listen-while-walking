# coding=utf-8

import sys
import commands
import os
import os.path
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

from config import *


reload(sys)
sys.setdefaultencoding('utf-8')


#setting
TEST_MODE = False

##

def fileExists(file):
    return os.path.exists(file)

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

    if fileExists('./ffmpeg') == False:
        print 'ffmpeg를 찾을 수 없습니다. http://ffmpegmac.net/ 에서 받을 수 있습니다.'
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
def addVoiceToItunesLibrary(mp3withPath, mp3withoutPath):
    source = mp3withPath
    distnation = '/Users/' + getUserName() \
                           + '/Music/iTunes/iTunes Media/' \
                           + 'Automatically Add to iTunes.localized'
    if fileExists(source) == False:
        print 'mp3 파일을 찾지 못했습니다.'
        sys.exit(1)
    if fileExists(distnation + '/' + mp3withoutPath) == True:
        try: 
            os.unlink(distnation)
        except: 
            print 'source: ' + source
            print 'distnation: ' + distnation
            sys.exit(1)

    try: 
        shutil.move(source, distnation)
    except: 
        print 'mp3 파일을 아이튠즈 라이브러리에 추가하는데 실패했습니다.'
        sys.exit(1)


def moveToResultDirectory(mp3_filename):
    source = './' + mp3_filename
    distnation = RESULT_DIR + mp3_filename

    try:
        shutil.move(source, distnation)
    except IOError: 
        return False

    return True


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
        self.gd_client.email = configGoogleAccountName
        self.gd_client.password = configGoogleAccountPassword
        self.gd_client.source = configApplicationName
        try: 
            print '구글 드라이브에 연결하고 있습니다.'
            self.gd_client.ProgrammaticLogin()
        except gdata.service.RequestError, inst:
            response = inst[0]  
            status = response['status']  
            reason = response['reason']  
            body = response['body']
            print 'status: ' + response['status'] \
                  + ' reason: ' + response['reason'] \
                  + ' body: ' + response['body']

    def getContentsRows(self):
        spreadsheet_key = configSpreadsheetKey
        worksheet_id = configContentsWorksheetKey

        try:
            entry = self.gd_client.GetListFeed(spreadsheet_key, worksheet_id).entry
        except gdata.service.RequestError, inst:
            response = inst[0]  
            status = response['status']  
            reason = response['reason']  
            body = response['body']
            print 'status: ' + response['status'] \
                  + ' reason: ' + response['reason'] \
                  + ' body: ' + response['body']
        return entry

    def getCorrectRows(self):
        spreadsheet_key = configSpreadsheetKey
        worksheet_key = configCorrectWorksheetKey

        try:
            entry = self.gd_client.GetListFeed(spreadsheet_key, worksheet_key).entry 
        except gdata.service.RequestError, inst:
            response = inst[0]  
            status = response['status']  
            reason = response['reason']  
            body = response['body']
            print 'status: ' + response['status'] \
                  + ' reason: ' + response['reason'] \
                  + ' body: ' + response['body']
        return entry

    def updateRow(self, entry, new_row_data):
        try:
            self.gd_client.UpdateRow(entry, new_row_data)
        except gdata.service.RequestError, inst:
            response = inst[0]  
            status = response['status']  
            reason = response['reason']  
            body = response['body']
            print 'status: ' + response['status'] \
                  + ' reason: ' + response['reason'] \
                  + ' body: ' + response['body']


def run():
    count = 1

    gd = GoogleDocs()

    for row in gd.getContentsRows(): 
        source = row.custom[COLUMN_NAME_SOURCE].text
        title = escape_characters(row.custom[COLUMN_NAME_TITLE].text)
        full_content = title + ', ' + escape_characters(row.custom[COLUMN_NAME_CONTENT].text)

        if row.custom[COLUMN_NAME_CONVERTED].text == None:
            cleanupBeforeStart()

            mp3_filename = TODAY_DATE + ' ' + escape_characters(title) + '.' + EXTENSION_MP3
            aiff_filename = TODAY_DATE + ' ' + escape_characters(title) + '.' + EXTENSION_AIFF

            full_content = correctWords(gd, full_content)

            if convertToVoice(aiff_filename, full_content) == False:
                print '텍스트를 음성으로 변환하는데 실패했습니다.'
                sys.exit()

            # 인코딩
            cmd = getFFmpegEncodingCommand(aiff_filename, mp3_filename)
            result = runFFmpegCommand(cmd)
            if result == False:
                print '음성 파일을 인코딩하는데 실패했습니다.'
                sys.exit()

            # 끝에 이펙트 연결
            cmd = getFFmpegConcatCommand(mp3_filename, title, album,artist, genre)
            if runFFmpegCommand(cmd) == False:
                print '음성 파일에 효과음을 추가하는데 실패했습니다.'
                sys.exit()

            if removeAIFF(aiff_filename) == False:
                print '음성 파일을 정리하지 못했습니다.'
                sys.exit()        
            if moveToResultDirectory(mp3_filename) == False:
                print '인코딩 된 파일을 이동하는데 실패했습니다.'
                sys.exit()

            if TEST_MODE == False:
                addVoiceToItunesLibrary(RESULT_DIR + mp3_filename, mp3_filename)

                new_row_data = {}
                new_row_data[COLUMN_NAME_SOURCE] = row.custom[COLUMN_NAME_SOURCE].text
                new_row_data[COLUMN_NAME_TITLE] = row.custom[COLUMN_NAME_TITLE].text
                new_row_data[COLUMN_NAME_CONTENT] = row.custom[COLUMN_NAME_CONTENT].text
                new_row_data[COLUMN_NAME_TIMESTAMP] = row.custom[COLUMN_NAME_TIMESTAMP].text
                new_row_data[COLUMN_NAME_CONVERTED] = 'O'
                
                gd.updateRow(row, new_row_data)

            print str(count) + '. ' + row.custom[COLUMN_NAME_TITLE].text + ' (변환 완료)'
        else:
            print str(count) + '. ' + row.custom[COLUMN_NAME_TITLE].text + ' (건너뜀)'

        count = count + 1

run()