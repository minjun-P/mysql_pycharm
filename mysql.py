from typing import List, Any

import pymysql

db = pymysql.connect(host='localhost', port=3306,
                     user='root', passwd='Pmjshpmj78!',
                     db='bestproducts', charset='utf8')
cursor = db.cursor()

sql = '''
CREATE TABLE if not exists items (
    item_code VARCHAR(20) NOT NULL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    ori_price INT NOT NULL,
    dis_price INT NOT NULL,
    discount_percent INT NOT NULL,
    provider VARCHAR(100)
);
'''
cursor.execute(sql)

sql = '''
CREATE TABLE if not exists ranking (
    num INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    main_category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL,
    item_ranking TINYINT UNSIGNED NOT NULL,
    item_code VARCHAR(20) NOT NULL,
    FOREIGN KEY (item_code) REFERENCES items(item_code)
);
'''

cursor.execute(sql)

db.commit()

import requests
from bs4 import BeautifulSoup as BS

url = 'http://corners.gmarket.co.kr/Bestsellers'
res = requests.get(url)
soup = BS(res.content, 'lxml')

categories = soup.select('#categoryTabG li a')

for category in categories:
    url = 'http://corners.gmarket.co.kr' + category['href']
    res = requests.get(url)
    soup = BS(res.content, 'lxml')

    items = soup.select('div.best-list')
    items = items[1]

    for index, item in enumerate(items.select('li')):

        data_dict = dict()


        # 각 중요 변수 수집

        category_name = category.get_text()
        sub_category_name = 'ALL'
        ranking = index + 1
        title = item.select_one('a.itemname')
        ori_price = item.select_one('div.o-price')
        dis_price = item.select_one('div.s-price strong span')
        dis_percent = item.select_one('div.s-price > span > em')

        product_link = item.select_one('div.thumb a')['href']
        item_code = product_link.split('=')[1].split('&')[0]

        res = requests.get(product_link)
        temp_soup = BS(res.content, 'lxml')
        provider = temp_soup.select_one('p > span.text__seller')

        # 변수 전처리
        if ori_price is None or ori_price.get_text() == '':
            ori_price = dis_price

        if dis_price is None:
            dis_price, ori_price = 0, 0
        else:
            ori_price = ori_price.get_text().replace(',', '').replace('원', '')
            dis_price = dis_price.get_text().replace(',', '').replace('원', '')

        if dis_percent is None or dis_percent.get_text() == '':
            dis_percent = 0
        else:
            dis_percent = dis_percent.get_text().replace('%', '')
        if provider is None:
            provider = ''
        else:
            provider = provider.get_text().strip()

            # 변수 딕셔너리에 저장
        data_dict['category_name'] = category_name
        data_dict['sub_category_name'] = sub_category_name
        data_dict['ranking'] = ranking
        data_dict['title'] = title.get_text()
        data_dict['ori_price'] = ori_price
        data_dict['dis_price'] = dis_price
        data_dict['dis_percent'] = dis_percent
        data_dict['item_code'] = item_code
        data_dict['provider'] = provider

        sql = "SELECT COUNT(*) FROM items WHERE item_code = '{}';".format(data_dict['item_code'])
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result[0])
        if result[0] == 0:
            sql = '''INSERT INTO items (item_code, title, ori_price, dis_price, discount_percent, provider) VALUES(
                '{}','{}', {}, {}, {}, '{}');'''.format(data_dict['item_code'], data_dict['title'],
                                                        data_dict['ori_price'], data_dict['dis_price'],
                                                        data_dict['dis_percent'], data_dict['provider']).replace('\n',
                                                                                                                 '')
            cursor.execute(sql)

        sql = '''INSERT INTO ranking (main_category, sub_category, item_ranking, item_code) VALUES(
            '{}','{}',{},'{}');'''.format(data_dict['category_name'], data_dict['sub_category_name'],
                                          data_dict['ranking'], data_dict['item_code']).replace('\n', '')
        cursor.execute(sql)

        db.commit()
        print(data_dict['category_name'], data_dict['ranking'])


    sub_categories = soup.select('div.navi.group > ul > li > a')


    for sub_category in sub_categories:
        res = requests.get('http://corners.gmarket.co.kr' + sub_category['href'])
        soup = BS(res.content, 'lxml')

        items = soup.select('div.best-list')
        items = items[1]

        for index, item in enumerate(items.select('li')):

            data_dict = dict()

            # 각 중요 변수 수집

            category_name = category.get_text()
            sub_category_name = sub_category.get_text()
            ranking = index + 1
            title = item.select_one('a.itemname')
            ori_price = item.select_one('div.o-price')
            dis_price = item.select_one('div.s-price strong span')
            dis_percent = item.select_one('div.s-price > span > em')

            product_link = item.select_one('div.thumb a')['href']
            item_code = product_link.split('=')[1].split('&')[0]

            res = requests.get(product_link)
            soup = BS(res.content, 'lxml')
            provider = soup.select_one('p > span.text__seller')

            # 변수 전처리
            if ori_price is None or ori_price.get_text() == '':
                ori_price = dis_price

            if dis_price is None:
                dis_price, ori_price = 0, 0
            else:
                ori_price = ori_price.get_text().replace(',', '').replace('원', '')
                dis_price = dis_price.get_text().replace(',', '').replace('원', '')

            if dis_percent is None or dis_percent.get_text() == '':
                dis_percent = 0
            else:
                dis_percent = dis_percent.get_text().replace('%', '')
            if provider is None:
                provider = ''
            else:
                provider = provider.get_text().strip()

            # 변수 딕셔너리에 저장
            data_dict['category_name'] = category_name
            data_dict['sub_category_name'] = sub_category_name
            data_dict['ranking'] = ranking
            data_dict['title'] = title.get_text()
            data_dict['ori_price'] = ori_price
            data_dict['dis_price'] = dis_price
            data_dict['dis_percent'] = dis_percent
            data_dict['item_code'] = item_code
            data_dict['provider'] = provider

            sql = "SELECT COUNT(*) FROM items WHERE item_code = '{}';".format(data_dict['item_code'])
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result[0])
            if result[0] == 0:
                sql = '''INSERT INTO items (item_code, title, ori_price, dis_price, discount_percent, provider) VALUES(
                    '{}','{}', {}, {}, {}, '{}');'''.format(data_dict['item_code'], data_dict['title'],
                                                            data_dict['ori_price'], data_dict['dis_price'],
                                                            data_dict['dis_percent'], data_dict['provider']).replace(
                    '\n', '')
                cursor.execute(sql)

            sql = '''INSERT INTO ranking (main_category, sub_category, item_ranking, item_code) VALUES(
                '{}','{}',{},'{}');'''.format(data_dict['category_name'], data_dict['sub_category_name'],
                                              data_dict['ranking'], data_dict['item_code']).replace('\n', '')
            cursor.execute(sql)

            db.commit()
            print('sub',data_dict['sub_category_name'], data_dict['ranking'])


db.close()
