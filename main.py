from bunjang import bunjang_start
import schedule
import time
import asyncio
from database import connectDB
# bunjang으로 파일 따로 빼서 bunjang_start함수 import하기

def print_hi(name):
    # 스크립트를 디버그하려면 하단 코드 줄의 중단점을 사용합니다.
    print(f'Hi, {name}')  # 중단점을 전환하려면 Ctrl+F8을(를) 누릅니다.


# 스크립트를 실행하려면 여백의 녹색 버튼을 누릅니다.
if __name__ == '__main__':
    bunjang_start()
    schedule.every(2).minutes.do(bunjang_start)
    while True:
        schedule.run_pending()
        time.sleep(1)
# https://www.jetbrains.com/help/pycharm/에서 PyCharm 도움말 참조
