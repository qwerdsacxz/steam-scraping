#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
n=6
path='1.xlsx'
def getgamelist(n):
    linklist=[]
    IDlist = []
    for pagenum in range(1,n):
        r = requests.get('https://store.steampowered.com/search/?ignore_preferences=1&category1=998&os=win&filter=globaltopsellers&page=%d'%pagenum,headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        soups= soup.find_all(href=re.compile(r"https://store.steampowered.com/app/"),class_="search_result_row ds_collapse_flag")
        for i in soups:
            i = i.attrs
            i = i['href']
            link = re.search('https://store.steampowered.com/app/(\d*?)/',i).group()
            ID = re.search('https://store.steampowered.com/app/(\d*?)/(.*?)/', i).group(1)
            linklist.append(link)
            IDlist.append(ID)
        print('已完成'+str(pagenum)+'页,目前共'+str(len(linklist)))
    return linklist,IDlist

def getdf(n):#转df
    linklist,IDlist = getgamelist(n)
    df = pd.DataFrame(list(zip(linklist,IDlist)),
               columns =['Link', 'ID'])
    return df
if __name__ == "__main__":
    df = getdf(n)#n代表爬取到多少页
    df.to_excel(path)#储存


# In[4]:


df


# In[6]:


def gamename(soup):   #游戏名字
    try:
        a = soup.find(class_="apphub_AppName")
        k = str(a.string)
    except:
        a = soup.find(class_="apphub_AppName")
        k = str(a.text)
    return k

def gameprice(soup):#价格
    try:
        a = soup.findAll(class_="discount_original_price")
        for i in a:
            if re.search('$|free|免费', str(i),re.IGNORECASE):
                a = i
        k = str(a.string).replace('	', '').replace('\n', '').replace('\r', '').replace(' ', '')
    except:
        a = soup.findAll(class_="game_purchase_price price")
        for i in a:
            if re.search('$|free|免费', str(i),re.IGNORECASE):
                a = i
        k = str(a.string).replace('	', '').replace('\n', '').replace('\r', '').replace(' ', '')
    return k

def taglist(soup):#标签列表
    list1=[]
    a = soup.find_all(class_="app_tag")
    for i in a:
        k = str(i.string).replace('	', '').replace('\n', '').replace('\r', '')
        if k == '+':
            pass
        else:
            list1.append(k)
    list1 = str('\n'.join(list1))
    return list1

def description(soup):  #游戏描述
    a = soup.find(class_="game_description_snippet")
    k = str(a.string).replace('	', '').replace('\n', '').replace('\r', '')
    return k

def reviewsummary(soup):   #总体评价
    a = soup.find(class_="summary column")
    try:
        k = str(a.span.string)
    except:
        k=str(a.text)
    return k

def getdate(soup):   #发行日期
    a = soup.find(class_="date")
    k = str(a.string)
    return k

def userreviewsrate(soup):#好评率
    a = soup.find(class_="user_reviews_summary_row")
    k = str((a.attrs)['data-tooltip-html'])
    return k

def developer(soup):   #开发商
    a = soup.find(id="developers_list")
    k = str(a.a.string)
    return k

def getreviews(ID):#获取评论
    r1 = requests.get(
        'https://store.steampowered.com/appreviews/%s?cursor=*&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=schinese&l=schinese&review_type=all&purchase_type=all&playtime_filter_min=0&playtime_filter_max=0&filter_offtopic_activity=1'%str(ID),headers=headers,timeout=10)
    soup = BeautifulSoup(r1.json()['html'], 'lxml')
    a = soup.findAll(class_="content")
    list1 = []
    for i in a:
        list1.append(i.text.replace('	', '').replace('\n', '').replace('\r', '').replace(' ', ','))
    k=str('\n'.join(list1))
    return k

def getdetail(x):
    tag, des, reviews, date, rate, dev, review,name,price = ' ', ' ', ' ', ' ', ' ', ' ', ' ',' ',' '
    global count
    try:
        r = requests.get(x['Link'], headers=headers,timeout=10)
    except:
        print('服务器无响应1')
        try:
            r = requests.get(x['Link'], headers=headers,timeout=10)
        except:
            print('服务器无响应2')
            try:
                r = requests.get(x['Link'], headers=headers,timeout=10)
            except:
                print('服务器无响应3')

    try:
        soup = BeautifulSoup(r.text, 'lxml')
        name = gamename(soup)
        tag = taglist(soup)
        des = description(soup)
        reviews = reviewsummary(soup)
        date = getdate(soup)
        rate = userreviewsrate(soup)
        dev = developer(soup)
        review = getreviews(str(x['ID']))
        price = gameprice(soup)
        print('已完成: '+name+str(x['ID'])+'第%d个'%count)
    except:
        print('未完成:  '+str(x['ID'])+'第%d个'%count)
        price = 'error'

    count += 1
    return name,price,tag,des,reviews,date,rate,dev,review


if __name__ == "__main__":
    df1 = pd.read_excel('1.xlsx')
    count = 1
    df1['详细'] = df1.apply(lambda x: getdetail(x), axis=1)
    df1['名字'] = df1.apply(lambda x: x['详细'][0], axis=1)
    df1['价格'] = df1.apply(lambda x: x['详细'][1], axis=1)
    df1['标签'] = df1.apply(lambda x: x['详细'][2], axis=1)
    df1['描述'] = df1.apply(lambda x: x['详细'][3], axis=1)
    df1['近期评价'] = df1.apply(lambda x: x['详细'][4], axis=1)
    df1['发行日期'] = df1.apply(lambda x: x['详细'][5], axis=1)
    df1['近期数量好评率'] = df1.apply(lambda x: x['详细'][6], axis=1)
    df1['开发商'] = df1.apply(lambda x: x['详细'][7], axis=1)
    df1['评论'] = df1.apply(lambda x: x['详细'][8], axis=1)
    
    df1.to_excel('2.xlsx')
    print('已完成全部')


# In[7]:


df1


# In[ ]:




