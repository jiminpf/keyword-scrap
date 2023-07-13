import pymysql.err
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import time
import random
from database import connectDB
import re

def bunjang_start():
    print("크롬 시작")
    page_number = 1 #시작페이지(정수로 써야함)
    max_page = 2 #최대 페이지

    data_list=[] #데이터리스트 빈 배열

    chrome_options = webdriver.ChromeOptions()
    # chrome 창에 쓸 수 있는 옵션들
    chrome_options.add_argument('headless') # 크롤링 할 때마다 크롬창 켜지는 거 귀찮으니까 숨김처리하기 - headless
    chrome_options.add_argument('window-size=1920x1080')  # 크롬 켤 때 창크기
    chrome_options.add_argument("disable-gpu")

    # 크롬과 크롬을 조정할 수 있는 드라이버의 버전을 맞추는 것
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    # 최대페이지(2)까지 돌 때까지 반복문
    for page in range(page_number, max_page+1):
        url = "https://m.bunjang.co.kr/search/products?order=date&page=" + str(page) + "&q=%EC%B9%98%EC%9D%B4%EC%B9%B4%EC%99%80"

        print(url)

        # 해당 url 가져오기
        driver.get(url)
        html = driver.page_source  # html이라는 변수에 driver.page_source 넣기
        soup = bs(html, 'html.parser')  # 읽어온 html 텍스트를 parser에 넣어주기 여기에 넣으면 select나 find 같은 기능을 쓸 수 있음
        temp_obj = soup.select_one(
            '#root > div > div > div:nth-child(4) > div > div.sc-ecaExY.jDDRxw > div > div:nth-child(8) > a > div.sc-eInJlc.eNTDiJ > div.sc-gtfDJT.brQSgh')

        product_list = soup.select_one('#root > div > div > div:nth-child(4) > div > div.sc-ecaExY.jDDRxw > div')
        # product_list에서 바로 다음 div 하나 가져오기

        for data in product_list.select('div.sc-kcDeIU.WTgwo'):

            product = data.find('a')
            if product is None:
                print(product)
                continue

            product_info = {
                'pid': None,
                'href': None,
                'image': None,
                'title': None,
                'price': None,
            }

            # 파이썬에서 is not None 은 !=null 같은 의미. product.attr 중에 data-pid가 있으면~

            pid = product.attrs['data-pid']
            if pid is not None:
                product_info['pid'] = pid
            else:
                continue

            href = product.attrs['href']
            if href is not None:
                product_info['href'] = 'https://m.bunjang.co.kr' + href
            else:
                continue

            image_div = product.find('div', {"class": ["sc-hgHYgh", "ieNgVs"]})
            image = image_div.find('img')
            if image is not None:
                product_info['image'] = image.attrs['src']
            else:
                continue

            title = product.find('div', {"class": ["sc-gtfDJT", "brQSgh"]})
            if title is not None:
                product_info['title'] = title.string
            else:
                continue

            price = product.find('div', {"class": ["sc-fOICqy", "ikGLLE"]})
            if price is not None:
                product_info['price'] = price.string
            else:
                continue

            # print(product_info)
            data_list.append(product_info) #미리 만들어둔 배열에 가져온 정보 넣기
            # break # 각 매물 정보 가져 오는 반복문
        # break # 2페이지 도는 반복문

        count = random.randrange(2, 6) #2~6랜덤 값 가져오기
        time.sleep(count) # count초 대기
    # return


    driver.quit() # 크롬 창 끄기

    db = connectDB()
    for product in data_list:

        cur = db.cursor(pymysql.cursors.DictCursor)
        # 중복 있는 지 확인. from 뒤에 오는 거에 mysql에서 만든 table 이름 적기
        cur.execute("select count(*) as cnt from products where p_id=%s and source='번개장터'", product['pid'])
        beforeCount = cur.fetchone() #결과를 한 줄만 가져오기
        cur.close() #커서 끄기

        if(beforeCount['cnt'] >= 1):
            continue
        # insert into 테이블명 : 테이블에 데이터 추가하기
        sql = "insert into products " \
            "(`title`, `p_id`, `image`, `url`, `created_at`, `hit_count`, `price`, `source`)" \
            " values " \
            "(%s, %s, %s, %s, now(), 0, %s, '번개장터')"  #s는 string d는 숫자. string, 지금시간, 디폴트값 같이 형 정해주는 거..?같음
        cur = db.cursor(pymysql.cursors.DictCursor)
        try:
            product['price'] = re.sub(",", "", product['price']) # 가격에 ,없애고
            product['price'].strip() #공백없애기
            
            cur.execute(sql, (product['title'], product['pid'], product['image'], product['href'], int(product['price'])))
            db.commit()

        except pymysql.err.InternalError as e:
            code, msg = e.args
            print(msg)

        cur.close()

        # break

    db.close()