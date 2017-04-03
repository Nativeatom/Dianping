# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 12:20:42 2017

@author: Y40
"""
import re
import json
from bs4 import BeautifulSoup    
import threading  
from requests import Session
import urllib2
import time
import random
import chardet
import string
import codecs
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

class dazp_bj:  
    def __init__(self,category):  
        self.baseUrl='http://www.dianping.com'  
        self.bgurl=category[0][0]+'/review_more'
        self.typename=category[0][1] 
        self.comment = category[0][2] 
        self.status = category[1]
        self.page=1  
        self.pagenum = 20
        self.headers={  
            "Host":"www.dianping.com",  
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",  
            "Referer":category[0][0]+'/review_all',
        }
        
#    def PageNum(self,bgurl):
#        html=self.s.post(bgurl,headers=self.headers).text
#        soup=BeautifulSoup(html,'lxml')
#        pagelist = soup.find('div',class_='comment mode').find('div',class_='Pages').find('div',class_='Pages').find_all('a')
#        return len(pagelist)
        
    def start(self):  
        self.s=Session()    #定义一个Session()对象  
        print self.typename, self.bgurl   
        self.typename = self.typename.decode('utf-8')
        html=self.s.post(self.bgurl,headers=self.headers).text
        soup_page=BeautifulSoup(html,'lxml')
        CommentTotal = soup_page.find('div',class_='comment-tab').find('div',class_='tabs').find('span',class_='active').em.get_text()
        Comment_T = CommentTotal.replace("(",'').replace(')','')
        if type(int(Comment_T) == int):
            self.comment = int(Comment_T) 
            print "评论update: %d 条\n"%(self.comment)
#获取评论页数
        page = []
        for a in soup_page.find('div',class_='comment-mode').find('div',class_='Pages').find('div',class_='Pages').find_all('a'):
            now_page = a.get_text().encode('utf-8')
            page.append(now_page)
            time.sleep(random.randint(0,20))
        self.pagenum = int(page[-2])
        print "评论共有", self.pagenum, "页 ", self.comment, "条"
#       
        comment_count = 0
        dazp_bj.__parseHtml(self,self.bgurl,comment_count) #调用__parseHtml函数
        print self.typename, "comment getting finished\n"
        try:
            f2 = open('comment_index.txt','a')
            #code = chardet.detect(self.typename)['encoding']
            f2.write(self.typename.encode('utf-8')+'.txt' + "\r\n")
        except UnicodeEncodeError:
            print self.typename," 写入失败\n"
        finally:
            pass
        print 'get data of %s down'%(self.status['Restaurant'])
        html=self.s.post(self.bgurl,headers=self.headers).text
#        soup=BeautifulSoup(html,'lxml')
#        self.pagenum=int(soup.find('div',class_='comment mode').find('div',class_='Pages').find('div',class_='Pages').find_all('a')[-2].get_text().encode('utf-8')) #设置最大页面数目
#        maxpage = dazp_bj.PageNum(self, self.bgurl)
#        print "Review has ", maxpage, "pages\n"
    def ch_en_utfenode(self, text):
        pass
    
    def __parseHtml(self,preurl, comment_count):  
        comment=dict()
        html=self.s.post(preurl,headers=self.headers).text
        soup=BeautifulSoup(html,'lxml')
        name2 = ['商家','用户名','总评','口味','环境','服务','评论','日期','人均','赞','喜欢的菜']
        comment[name2[0]] = self.typename.encode('utf-8')
        fail = 0
#评论页面查询方法

        for li in soup.find('div',class_='comment-list').ul.find_all('li'):
            try:
                comment[name2[1]] = li.find('div',class_='pic').find('p',class_='name').a.get_text().encode('utf-8')
                print comment[name2[1]]#用户名
            except:
                continue
            Comment = li.find('div',class_="content")
            comment[name2[2]] = Comment.find('div',class_='user-info').span['title'].encode('utf-8')
            print comment[name2[2]]#总评
            comment[name2[3]] = Comment.find('div',class_='user-info').find('div',class_='comment-rst').find_all('span')[0].get_text().encode('utf-8')
#            print comment[name2[3]]#口味
            comment[name2[4]] = Comment.find('div',class_='user-info').find('div',class_='comment-rst').find_all('span')[1].get_text().encode('utf-8')
#            print comment[name2[4]]#环境
            comment[name2[5]] = Comment.find('div',class_='user-info').find('div',class_='comment-rst').find_all('span')[2].get_text().encode('utf-8')
#            print comment[name2[5]]#服务
#            for br in Comment.find('div',class_='comment-txt').find('div',class_='J_brief-cont').find_all('br'):
#            comment[name2[6]] + = Comment.find('div',class_='comment-txt').find('div',class_='J_brief-cont').find('br').get_text
#            except:
            comment[name2[6]] = Comment.find('div',class_='comment-txt').find('div',class_='J_brief-cont').get_text().encode('utf-8').lstrip().rstrip()
            print comment[name2[6]]
            comment[name2[7]] = Comment.find('div', attrs={'class':"misc-info"}).find('span',class_='time').get_text().encode('utf-8')     
#            print comment[name2[7]]#日期
            try:
                comment[name2[8]] = Comment.find('div',class_='user-info').find('span',class_="comm-per").get_text().encode('utf-8')[4:]
                print comment[name2[8]]
            except:
                comment[name2[8]]=0 #没有标注人均消费
            comment[name2[9]] = int(Comment.find('div', attrs={'class':"misc-info"}).find('span',class_='col-right').find('span',class_='countWrapper').a['data-count'])  
            print comment[name2[9]]
            try:
                comment[name2[10]] = Comment.find('div',class_='comment-recommend').find_all('a').get_text().encode('utf-8')
            except:
                comment[name2[10]]='无'
#            print comment[name2[10]]
            self.status['comment']+=1
            comment_count+=1
            time.sleep(random.randint(0,45))
#            
##Addition over
#
            try:
                with open(self.typename+'.json','a') as outfile:  
                    json.dump(comment,outfile,ensure_ascii=False)  
                with open(self.typename+'.json','a') as outfile:  
                    outfile.write(',\n') 
                print "Comment: #", comment_count,"/",self.comment,"\n"
            except AttributeError:
                fail+=1
                print "评论写入失败： ", fail
                pass
            except UnicodeEncodeError:
                try:
                    self.typename = self.typename.encode('utf-8')
                    #decode(chardet.detect(self.typename)['encoding'])
                except UnicodeEncodeError:
                    try:
                        comment_list = list(comment)
                        fileObject = open(self.typename + '.txt', 'w')  
                        for ip in comment_list:  
                            fileObject.write(ip)  
                            fileObject.write('\n')  
                        fileObject.close()
                        print comment_count," 评论写入失败\n"
                        comment_count+=1
                    except UnicodeEncodeError:
                        print comment_count," 评论写入失败\n"
                        comment_count+=1
                        pass
                except UnicodeEncodeError:
                        print comment_count," 评论写入失败\n"
                        comment_count+=1
                        pass
                try:
                    with open(self.typename+'.json','a') as outfile:
                        json.dump(comment,outfile,ensure_ascii=False)
                except IOError:
                    file=codecs.open(self.typename+'.txt','w','utf-8')
                    for key in comment:
                        
                        #for j in comment_get[i]:
                        #    j = j + ' '
                        file.write(str(key) + ': ')
                        file.write(comment[key])
                        file.write(',')
                    file.write('\r\n')
                    pass
                except UnicodeEncodeError:
                    continue
                try:
                    with open(self.typename+'.json','a') as outfile:
                        outfile.write(',\n')
                except IOError:
                    outfile.write(',\n')
                    pass
                print "Comment: #", comment_count,"/",self.comment,"\n"
                self.status['user-name'] = comment[name2[1]]
                self.status['comment'] = comment_count
#            except IOError:
#                fail+=1
#                print"写入IOError ", fail
#                pass
        print "评论第", self.page,"页结束\n"
        self.page+=1  
        self.status['page'] = self.page
        if self.page<self.pagenum:  
            self.nexturl=self.bgurl+soup.find('div',class_='comment-mode').find('div',class_='Pages').find('div',class_='Pages').find('a',class_='NextPage')['href']  #获得下一页的链接
            time.sleep(random.randint(0,10))
            print "评论第", self.page,"/",self.pagenum,"页"
        if self.page == self.pagenum:
            return 1
        try:
            dazp_bj.__parseHtml(self,self.nexturl, comment_count)
        except AttributeError:
            fail+=1
            print "Error: ",fail
            pass
        except IOError:
            fail+=1
            print "出现IOError ",fail 
            pass
        except urllib2.URLError:
            print "出现网络连接错误\n"
            local_time = time.strftime('%Y-%m-%d %H:%M:%S  %Z',time.localtime(time.time()))
            self.status['time'] = local_time
            print self.status #显示断点信息
            f3 = open('comment_breakpoint','a')
            for key in self.status:
                f3.write(key + ':' + self.status[key] + ' ')
            f3.write('\r\n')
            time.sleep(600)
            pass
            
     
#        except ERROR:execution aborted:
#            fail+=1
#            print"出现错误\n"
            
 
#New function
        
if __name__=='__main__':  
    name = []
    link = []
    comNum = []
    content = []
    finish_num = [0,1,2,5,6]
    f = open('Restaurant_Nanjing.txt','r')
    for line in f.readlines():
        content.append(line)
    for line in content:
        split = line.split('"')
        resname = split[3]
        name.append(resname)
        linkage = split[-6]
        link.append(linkage)
        commentNumber = split[-1].lstrip(": ").replace("},",'')
        comNum.append(int(commentNumber))
    if len(link)!=len(name):
        print "get link error for number unmatch\n"
    else:
        print len(link) ,"restaurants included\n","Example:",name[0],": ",link[0],"Comment: ",comNum[0],"\n"
    f.close()
    
    start_num = 16
    
    status = dict() #记录爬虫当前状态
    for i in range(start_num,len(link)-1):#restart 改这个参数 3 4 11 12 13没做  i=5次数少可用于测试
        linkex = link[i]
        nameex = name[i]#.decode('utf-8')
        commex = comNum[i]
        status = {'Restaurant':name[i], 'link': link[i], 'page':1, 'comment':0, 'user-name':'爬壁神偷'}
        cat=[(linkex,nameex,commex),status]
        obj=list()  
        obj.append(dazp_bj(cat))  
        [threading.Thread(target=foo.start(),args=()).start for foo in obj]#多线程执行obj列表中的任务 
