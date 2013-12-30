# coding=utf-8

import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service

from config import *

gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = configGoogleAccountName
gd_client.password = configGoogleAccountPassword
gd_client.source = configApplicationName

print '구글 드라이브에 연결하고 있습니다.'
gd_client.ProgrammaticLogin()

def PrintFeed(feed):
    print '아이디\t\t워크시트 이름'
    for i, entry in enumerate(feed.entry):
        print '%s\t\t\t%s' % (entry.id.text.split('/')[-1], entry.title.text)

PrintFeed(gd_client.GetWorksheetsFeed(key=configSpreadsheetKey))