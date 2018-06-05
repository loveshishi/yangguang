import threading
import time

import requests
import lxml
import lxml.etree
import re


"""
提取每个页面的数据
"""
def get_data(urllist, file):
    for url in urllist:
        try:
            page_text = requests.get(url).content.decode("gb2312", errors="ignore")
            page_etree = lxml.etree.HTML(page_text)
            trs = page_etree.xpath("//table[@cellspacing='0']//"
                                   "table[@cellspacing='0']//tr")
            for tr in trs:
                line = ''
                num = tr.xpath("./td[@bgcolor='#FFFFFF']/text()")[0]
                dtype = tr.xpath("./td[@width='590']/a[@class='red14']"
                                 "/text()")[0]
                title = tr.xpath("./td[@width='590']/a[@class='news14']"
                                 "/text()")[0]
                addr = tr.xpath("./td[@width='590']/a[@class='t12h']"
                                 "/text()")[0]
                status1 = tr.xpath(".//span[@class='qgrn']/text()")
                status2 = tr.xpath(".//span[@class='qblue']/text()")
                if len(status1) != 0:
                    statu = status1[0]
                elif len(status2) != 0:
                    statu = status2[0]
                else:
                    statu = tr.xpath(".//span[@class='qred']/text()")[0]
                name = tr.xpath("./td[@class='t12h']/text()")[0]
                datetime = tr.xpath("./td[@class='t12wh']/text()")[0]
                line = line + num + "  " + dtype + "  " + title + "  " + addr + \
                        "  " + statu + "  " + name + "  " + datetime + "\r\n"
                print(line)
                with rlock:
                    file.write(line.encode("utf-8", errors='ignore'))
        except:
            print( "error" )


def getPageNumbers(url):
    response = requests.get(url).content
    text = response.decode("gb2312", errors="ignore")
    pagetext = lxml.etree.HTML(text)
    nums = pagetext.xpath("//div [@class='pagination']/text()") [-1]
    regx = re.compile("\d+", re.IGNORECASE)
    num = regx.findall(nums) [0]
    return num

"""
提取所有的url,每页30条数据，根据上面的page_nums(反映的
问题的总条数)来分析，如果page_nums能够整取30，则执行else
部分的语句，不能，则执行if部分的代码
"""
def makeUrlList(page_nums, url):
    urllist =  []
    if page_nums % 30 != 0:
        for pagenum in range(page_nums // 30 + 1):
            urllist.append(url + str(pagenum * 30))
    else:
        for pagenum in range(page_nums/30):
            urllist.append(url + str(pagenum * 30))
    return urllist



if __name__ == '__main__':

    start = time.clock()
    # 抓取的网址
    url = "http://wz.sun0769.com/index.php/question/report?page="

    #抓取的数据存储的文件
    file = open("阳光问政.txt", "wb")
    """
    提取总共的数目
    """
    page_nums = int(getPageNumbers(url))
    urllist = makeUrlList(page_nums, url)

    """
    开启线程锁，防止多线程写入文件冲突
    """
    rlock = threading.RLock()

    """
    开启线程的数目
    """
    threadNum = [[], [], [], [], [], [], [], [], [], []]
    num = len(threadNum)

    """
    为每个线程分配任务
    """
    for urlNum in range(len(urllist)):
        threadNum[urlNum % num].append(urllist[urlNum])

    threadList = []

    for i in range(num):
        thread = threading.Thread(target=get_data, args=(threadNum[i],file))
        thread.start()
        threadList.append(thread)

    for thd in threadList:
        thd.join()

    file.close()

    end = time.clock()

    print("所用时间:%s秒"%(end-time))
