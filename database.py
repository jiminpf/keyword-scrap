import pymysql
from configparser import ConfigParser

def connectDB():
    config = ConfigParser()
    config.read('./env.ini', encoding='utf-8')
    
    conn = pymysql.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        db=config['database']['database'],
        charset='utf8mb4'
    )

    return conn