listen-while-walking
====================
'걸어다니며 듣기'는 온라인 상에 읽고 싶은 글은 많은데 시각을 동원할 시간은 부족한 상황을 극복하기 위해 고민하다가 OSX에 있는 말하기 기능을 활용해 원하는 글을 걸어다니며 귀로 들을 수 있도록 하기 위한 스크립트입니다. OSX의 말하기 기능과 아이튠즈, FFmpeg, 구글 문서도구를 사용합니다.

## 이런 시나리오로 동작합니다.
 * 웹을 돌아다니다가 읽고 싶지만 지금은 읽기 곤란한 글을 찾아냅니다.
 * 즐겨찾기에서 미리 만들어 둔 구글 문서도구 '양식'을 연 다음 붙여넣습니다.
 * 맥에서 이 스크립트를 실행합니다. 스크립트가 구글 문서도구의 스프레드시트를 열어 글을 음성으로 변환해 아이튠즈 라이브러리에 등록합니다.
 * iOS 장비를 동기화합니다.
 * iOS 장비를 들고 걸어 다니며 스크랩 한 글을 듣습니다.

## 사용하려면 이런 것들이 필요합니다.
 * https://developers.google.com/gdata/articles/python_client_lib
 * http://ffmpegmac.net/

## 설치 방법
### 구글 드라이브에 양식과 스프레드시트 만들기.
#### 다음 주소를 참고해 'Google Data Python Library'를 설치합니다.
 * https://developers.google.com/gdata/articles/python_client_lib
#### 다음 주소의 파일을 적당한 디렉토리에 가져갑니다.
 * https://github.com/neoocean/listen-while-walking.git
#### ffmpeg를 다운로드해서 위 디렉토리에 복사합니다.
 * http://ffmpegmac.net/
#### 구글 드라이브에 새 양식을 생성합니다. (아래 공개 양식을 참고하세요.)
 * https://drive.google.com/folderview?id=0B-H586Q4RPiucm8tZTlMNm14cWs&usp=sharing
#### 위에서 만든 스프레드시트를 열고 칼럼 이름이 다음과 같은지 확인합니다. 맨 뒤에 '변환됨'이 없다면 첫 번째 행 마지막에 입력합니다.
 * '타임스탬프', '주소', '제목', '내용', '변환됨'
#### 구글 드라이브에 만든 양식에 주소, 제목, 내용을 각각 입력해 봅니다.
#### 스프레드시트를 열고 양식을 이용해 입력한 내용이 반영되는지 확인합니다.
#### 스프레드시트에 워크시트를 추가하고 칼럼 이름을 다음과 같이 입력합니다. (아래 주소를 참고하세요.)
 * '찾을 단어', '고칠 단어'
 * https://docs.google.com/a/neoocean.net/spreadsheet/ccc?key=0AuH586Q4RPiudGYzSnRSZzAwUnhDNnBkTmhSMWRfNWc&usp=drive_web#gid=0
### 'config.py' 파일을 설정합니다.
#### 'configGoogleAccountName'에 구글 아이디를 입력합니다.
#### 'configGoogleAccountPassword'에 구글 패스워드를 입력합니다. 애플리케이션 패스워드를 사용하면 패스워드를 평문으로 보관하는 부담을 줄일 수 있습니다.
#### 'configSpreadsheetKey'에 위에서 만든 '스프레드시트' 아이디를 입력하고 저장합니다.
 * 스프레드시트 아이디는 주소의 'key' 부분입니다.
 * 가령 이 예에서 주소는 'https://docs.google.com/a/neoocean.net/spreadsheet/ccc?key=0AuH586Q4RPiudGYzSnRSZzAwUnhDNnBkTmhSMWRfNWc&usp=drive_web#gid=0' 이므로 키는 '0AuH586Q4RPiudGYzSnRSZzAwUnhDNnBkTmhSMWRfNWc'가 됩니다.
#### 'help.py'를 실행해 결과를 어딘가에 복사해 둡니다. (결과는 아래와 같이 나타납니다.)
    구글 드라이브에 연결하고 있습니다.
    아이디     워크시트 이름
    od6         응답 양식
    od7         발음 교정
    [Finished in 2.4s]
#### 위 결과에서 'od6'이나 'od7' 부분을 config.py의 'configCorrectWorksheetKey'와 'configContentsWorksheetKey'에 입력합니다. 다음과 유사한 형태가 됩니다.
    # 'help.py'를 실행해서 나온 결과를 추가: 
    configCorrectWorksheetKey = 'od6'
    configContentsWorksheetKey = 'od7'
### 'main.py'를 실행합니다.