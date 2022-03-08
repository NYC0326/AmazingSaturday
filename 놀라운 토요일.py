from bs4 import BeautifulSoup as BS
import requests, re, random
from selenium import webdriver as WD
def get_lyrics(songId):
    lyrics = str(BS(requests.get('https://www.melon.com/song/detail.htm?songId=' + str(songId), headers=header).text, 'lxml').find("div", {"class": "lyric"})).replace('<div class="lyric" id="d_video_summary"><!-- height:auto; 로 변경시, 확장됨 -->', '').replace('</div>', '').strip().split('<br/>')
    lyrics[:], isKoreanOrEnglish = [x for x in lyrics if x], []  #빈 문자열 제거
    if diff == 'M':
        i = random.randrange(len(lyrics) - 2)
        answer = lyrics[i].split()
        lyrics_list = [lyrics[i - 1], '___________________', lyrics[i + 1]]
    if diff == 'H':
        i = random.randrange(len(lyrics) - 3)
        answer = (lyrics[i-1] + ' ' + lyrics[i] + ' ' + lyrics[i+1]).split()
        lyrics_list = [lyrics[i-2],'___________________', '___________________', '___________________', lyrics[i+2]]
    for a in answer:
        k_count, e_count = 0, 0
        for c in a:
            if ord('가') <= ord(c) <= ord('힣'):
                k_count += 1
            elif ord('a') <= ord(c.lower()) <= ord('z'):
                e_count += 1
        isKoreanOrEnglish.append('한글') if k_count > 0 else isKoreanOrEnglish.append('영어')
    lenth_hint = [x+' ' + str(len(y)) + '글자' for x, y in zip(isKoreanOrEnglish, answer)]
    return lyrics_list, answer, lenth_hint
def play_song(title, SID):
    rand, breakValue, i = random.randrange(len(title)), True, 0
    global point
    a = input('%s\n노래가 선택되었습니다.\n이 노래로 계속할까요? (Y, N으로 답해주세요)' % title[rand]).upper()
    while a == 'N':
        rand = random.randrange(len(title))
        a = input('다시 노래를 선택합니다\n\n%s\n노래가 선택되었습니다.\n이 노래로 계속할까요? (Y, N으로 답해주세요)' % title[rand]).upper()
    while a != ('Y' or 'N'):
        rand = random.randrange(len(title))
        a = input('잘못 입력하셨습니다. 다시 입력해주세요\n\n%s 노래가 선택되었습니다.\n이 노래로 계속할까요? (Y, N으로 답해주세요)' % title[rand]).upper()
    print('이 노래로 진행합니다')
    question, answer, lenth_hint = get_lyrics(SID[rand])
    title[rand] = title[rand].replace(' ' '&', '+')
    title[rand] = title[rand].replace('&', '+')
    driver.get('https://www.youtube.com/results?search_query=' + title[rand] + ' 가사')
    driver.find_elements_by_class_name("style-scope ytd-video-renderer")[i].click()
    a = input('노래가 문제가 있으면 Y, 없으면 N을 쳐주세요.').upper()
    while a != 'N':
        if a == 'Y':
            print('다른 영상을 틉니다.')
            i += 1
            driver.get('https://www.youtube.com/results?search_query=' + title[rand] + ' 가사')
            driver.find_elements_by_class_name("style-scope ytd-video-renderer")[i].click()
        else:
            print('잘못 입력하셨습니다. 다시 입력해주세요')
        a = input('노래가 문제가 있으면 Y, 없으면 N을 쳐주세요.').upper()
    print('난이도: %s\n문제:\n' % diff, "\n".join(str(i) for i in question), '\n')
    while True:
        player_answer = input('정답을 써주세요. (단어마다 띄어쓰기를 꼭 해주세요)\n*길이 힌트가 필요하면 lenth, 틀린거 개수가 알고 싶으면 error를 입력하세요\n**다시 들을려면 RE(대문자)를 입력하세요').split()
        if player_answer[0] == 'error':
            print('아직 답을 입력하지 않으셨습니다.') if answer_count == 0 else print('저번 답에서 틀린 단어의 개수는 %d개입니다' % answer_count)
        elif player_answer[0] == 'lenth':
            print('이 문제의 답은')
            for i in range(len(lenth_hint)):
                print(lenth_hint[i])
            print('로 이루어져 있습니다.')
            point -= 100
        elif player_answer[0] == 'RE':
            driver.get(driver.current_url)
            point -= 100
        else:
            answer_count = 0
            for i in range(min(len(answer), len(player_answer))):
                answer_count = answer_count if player_answer[i].lower() == str(answer[i].lower()) else (answer_count + 1)
            if len(answer) > len(player_answer):
                answer_count += int(len(answer)-len(player_answer))
            if len(answer) < len(player_answer):
                answer_count += int(len(player_answer)-len(answer))
            if answer_count == 0:
                break
            else:
                print('땡!! 다시 해보세요.')
                point -= 100
    a = input('정답입니다. 총 %d점 받았습니다.\n 다시 하시려면 RE를 눌러주세요\n 종료하시려면 아무거나 누르세요' % point)
    start() if a == 'RE' else driver.quit()
def crawl_artist():
    artist = input('\n아티스트의 이름을 입력해주세요.')
    SID, title = BS(requests.get('https://www.melon.com/search/song/index.htm?q=' + str(artist) + '&section=artist', headers=header).text, 'lxml').select('a[href*=playSong]', limit=10), BS(requests.get('https://www.melon.com/search/song/index.htm?q=' + str(artist) + '&section=artist', headers=header).text, 'lxml').find_all("a", {"class": "fc_gray"}, limit=10)
    for i in range(len(title)):
        title[i], SID[i] = title[i].text, re.search(r",'(\d+)'", SID[i]['href']).group(1)
    play_song(title, SID)
def crawl_date_chart():
    date = input('\n날짜를 입력해주세요. (ex. 20200516) / 2018년 10월 28일 이후로 됨')
    year, month, day, SID = date[0:4], date[4:6], date[6:8], []
    title = BS(requests.get('https://guyso.me/melon/dailychart/' + year + '/' + month + '/' + day, headers=header).text, 'lxml').find_all("td", {"class": "subject"}, limit=10)
    for i in range(len(title)):
        title[i] = title[i].find('p').text
        SID.append(re.search(r",'(\d+)'", BS(requests.get('https://www.melon.com/search/total/index.htm?q=' + str(title[i]), headers = header).text, 'lxml').select('a[href*=playSong]')[0]['href']).group(1))
    play_song(title, SID)
def crawl_year_chart():
    year = input('\n연도를 입력해주세요. (ex. 2020)\n')
    driver.get('https://www.melon.com/chart/age/index.htm?chartType=YE&chartGenre=KPOP&chartDate=' + year)
    SID, title = BS(driver.page_source, 'lxml').select('a[href*=playSong]', limit=10), BS(driver.page_source, 'lxml').find_all("div", {"class": "ellipsis rank01"}, limit=10)
    for i in range(len(title)):
        title[i], SID[i] = title[i].find('a').text, re.search(r",'(\d+)'", SID[i]['href']).group(1)
    play_song(title, SID)
def crawl_live_chart():
    title, SID = BS(requests.get('https://www.melon.com/chart/index.htm', headers=header).text, 'html.parser').find_all("div", {"class": "ellipsis rank01"}, limit=10), BS(requests.get('https://www.melon.com/chart/index.htm', headers=header).text, 'html.parser').select('a[href*=playSong]', limit=10)
    for i in range(len(title)):
        title[i], SID[i] = title[i].text, re.search(r",(\d+)", SID[i]['href']).group(1)
    play_song(title, SID)
def choose_song_list(status = True):
    print('\n숫자를 잘못 입력하셨습니다. 다시 입력해주세요') if status == False else None
    number = input("어떤 노래 리스트를 선택하시겠습니까?\n1. 특정 아티스트\n2. 특정 날의 일간차트\n3. 특정년도 연간차트\n4. 현재 실시간 차트\n")
    crawl_artist() if number == '1' else crawl_date_chart() if number == '2' else crawl_year_chart() if number == '3' else crawl_live_chart() if number == '4' else choose_song_list(False)
def start():
    driver.get('https://www.youtube.com')
    global diff, point
    diff, point = input("난이도를 입력해주세요.\n(운영중단)*E: 가사 2~3줄 중 몇몇 단어만 맞추기\n*M: 가사 3줄 중 1줄만 맞추기\n*H: 3줄 다 맞추기\n(운영중단)*S: 다 맞추기\n").upper(), 1000
    while  diff != 'M' and  diff != 'H':
        diff = input ("\n잘못 입력하셨습니다.\n난이도를 입력해주세요.\n(운영중단)*E: 가사 2~3줄 중 몇몇 단어만 맞추기\n*M: 가사 3줄 중 1줄만 맞추기\n*H: 3줄 다 맞추기\n(운영중단)*S: 다 맞추기\n").upper()
    choose_song_list()
options = WD.ChromeOptions()
options.add_extension('adblock.crx')
header, driver, diff, point = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}, WD.Chrome('chromedriver_win32/chromedriver.exe', options=options), '', 1000
start()