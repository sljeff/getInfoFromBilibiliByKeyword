#!usr/bin/python3
# coding: utf-8
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import json
import gevent.pool
from gevent import monkey
import os

monkey.patch_all()


def getBzhanInfoByKeywords(keyword='曾艳芬'):
    """
    保存所有封面，返回值是一个json，结构为[{"imgURL": imgURL, "shareURL": flash地址, "title": 标题, 'up': UP主},……]
    :type keywords: str
    :return: json
    """
    k = urlencode({'keyword': keyword})
    baseURL = 'http://search.bilibili.com/ajax_api/video?%s&order=totalrank&page=' % k

    if not os.path.exists('img'):
        os.mkdir('img')

    # 预处理
    preNum = 1
    preR = requests.get(baseURL + str(preNum))
    prerResult = preR.json()
    numPages = int(prerResult['numPages'])
    pool = gevent.pool.Pool(50)

    def downloadImg(imgURL):
        """
        :type imgURL: str
        :return: None
        """
        r = requests.get(imgURL)
        index = imgURL.index('archive') + 8
        saveName = str(imgURL[index:])
        with open(os.path.join('img', str(saveName)), 'wb') as f:
            f.write(r.content)

    def getInfoFromLi(li):
        soupTemp = BeautifulSoup(str(li), "html.parser")
        avURL = str(soupTemp.a['href'])
        _avIndex = avURL.index('av')
        avCode = avURL[_avIndex + 2:-1]
        shareURL = 'http://static.hdslb.com/miniloader.swf?aid=%s&page=1' % avCode
        title = soupTemp.img['title']
        imgURL = soupTemp.img['src']
        upSpan = soupTemp.find_all('span')[-1]
        try:
            up = BeautifulSoup(str(upSpan), "html.parser").a.string
        except:
            up = 'None'
        return {'shareURL': shareURL, 'title': title, 'imgURL': imgURL, 'up': up}

    def getInfoFromHTML(html):
        soup = BeautifulSoup(html, "html.parser")
        info = soup.find_all('li')
        return info

    result = []
    urls = []

    for i in range(1, numPages + 1):
        url = baseURL + str(i)
        urls.append(url)
    print('parsing......')
    rs = pool.map(requests.get, urls)

    for r in rs:
        html = r.json()['html']
        lis = getInfoFromHTML(html)
        for li in lis:
            temp = getInfoFromLi(li)
            result.append(temp)
            try:
                # pool.spawn(downloadImg(temp['imgURL']))
                print(temp['imgURL'])
                pass
            except:
                print('error with %s' % temp['imgURL'])

    print('ok!!!!!')
    pool.join()

    return json.dumps(result)


if __name__ == '__main__':
    r = getBzhanInfoByKeywords()
    with open('r.txt', 'w', encoding='utf-8') as f:
        f.write(r)
        print("saved as r.txt")
