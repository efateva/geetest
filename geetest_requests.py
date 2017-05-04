#-*-coding:utf-8-*-

import requests
import time
import json
import random
import re
import math
from bs4 import BeautifulSoup
from PIL import Image
import StringIO

class jianshu(object):
    def __init__(self):
        self.ssn = requests.session()
        self.ck_jianshu = {}
        self.ck_geetest = {}
        self.info = {}
        self.user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)  Safari/537.36"


    def run(self):
        self.process_1()
        self.process_2()
        self.process_3()
        self.process_4()
        self.process_5()


    def repeat(self, url, hd, ck={}):
        times = 5
        while times > 0:
            try:
                ans = self.ssn.get(url, headers=hd, cookies=ck, timeout=5)
                if ans.content: return ans
            except:
                times -= 1


    def gen_timestamp(self):
        return str(int(random.random()*10000+int(time.time()*1000)))


    def process_1(self):
        hd = {"Host": "www.jianshu.com",
              "User-Agent": self.user_agent}
        ans = self.repeat("https://www.jianshu.com/sign_in", hd)
        self.ck_jianshu.update(dict(ans.cookies)) 
        

    def process_2(self):
        hd = {"Host": "api.geetest.com",
              "Referer": "https://www.jianshu.com/sign_in",
              "User-Agent": self.user_agent}
        ans = self.repeat("https://api.geetest.com/get.php", hd)
        self.ck_geetest.update(dict(ans.cookies))


    def process_3(self):
        hd = {"Host": "www.jianshu.com",
              "Referer": "https://www.jianshu.com/sign_in",
              "User-Agent": self.user_agent}
        ans = self.repeat("https://www.jianshu.com/captchas/new", hd, self.ck_jianshu)
        self.info.update(json.loads(ans.content))
        self.ck_jianshu.update(dict(ans.cookies)) 


    def process_4(self):
        hd = {"Host": "api.geetest.com",
              "Referer": "https://www.jianshu.com/sign_in",
              "User-Agent": self.user_agent}
        url = "https://api.geetest.com/get.php?challenge={}&success=1&gt={}&product=float&lang=zh-cn&https=false&type=slide&callback=geetest_{}".format(self.info["challenge"], self.info["gt"], self.gen_timestamp())
        ans = self.repeat(url, hd, self.ck_geetest)
        tjson = re.findall("\((.*?)\)", ans.content)[0]
        self.info.update(json.loads(tjson))


    def process_5(self):
        xpos, tracks = self.get_xpos_trace()
        if not xpos:
            print "fail! retry in 1 second"
            return
        print xpos
        act = self.gee_f(self.gee_c(tracks))
        time.sleep(0.6)
        passtime = str(tracks[-1][-1])
        imgload = str(random.randint(0,200) + 50)
        userresponse = self.gee_userresponse(xpos, self.info["challenge"])
        time.sleep(0.6)
        hd = {"Host": "api.geetest.com",
              "Referer": "https://www.jianshu.com/sign_in",
              "User-Agent": self.user_agent}
        url = "https://api.geetest.com/ajax.php?gt={}&challenge={}&userresponse={}&passtime={}&imgload={}&a={}&callback=geetest_{}".format(self.info["gt"], self.info["challenge"], userresponse, passtime, imgload, act, self.gen_timestamp())
        ans = self.repeat(url, hd, self.ck_geetest)
        print ans.content


    def get_xpos_trace(self):
        xpos = 110
        times = 4
        while xpos > 90:
            img_url1 = "http://static.geetest.com/" + self.info["fullbg"]
            img_url2 = "http://static.geetest.com/" + self.info["bg"]
            xpos, tracks = crack_picture(img_url1, img_url2).pictures_recover()
            if xpos <= 90: return xpos, tracks
            times -= 1
            if times == 0:
                print "fail"
                return None, None
            self.refresh()
            

    def refresh(self):
        hd = {"Host": "api.geetest.com",
              "Referer": "https://www.jianshu.com/sign_in",
              "User-Agent": self.user_agent}
        url = "https://api.geetest.com/refresh.php?challenge={}&gt={}&callback=geetest_{}".format(self.info["challenge"], self.info["gt"], self.gen_timestamp())
        ans = self.repeat(url, hd, self.ck_geetest)
        tjson = re.findall("\((.*?)\)", ans.content)[0]
        self.info.update(json.loads(tjson))


    def gee_c(self, a):
        e = []
        f = 0
        g = []
        h = 0
        for h in range(len(a) - 1):
            b = int(round(a[h+1][0] - a[h][0]))
            c = int(round(a[h+1][1] - a[h][1]))
            d = int(round(a[h+1][2] - a[h][2]))
            g.append([b, c, d])
            if b == 0 and c == 0 and d == 0:
                pass
            elif b ==0 and c == 0:
                f += d
            else:
                e.append([b, c, d+f])
                f = 0
        if f != 0:
            e.append([b, c, f])
        return e


    def gee_d(self, a):
        b = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
        c = len(b)
        d = ""
        e = abs(a)
        f = e/c
        if f >= c: f = c - 1
        if f: d = b[f]
        e %= c
        g = ""
        if a < 0: g += "!"
        if d: g += "$"
        return g + d + b[e]


    def gee_e(self, a):
        b = [[1, 0], [2, 0], [1, -1], [1, 1], [0, 1], [0, -1], [3, 0], [2, -1], [2, 1]]
        c = "stuvwxyz~"
        for d in range(len(b)):
            if a[0] == b[d][0] and a[1] == b[d][1]:
                return c[d]
        return 0

            
    def gee_f(self, a):
        g = []
        h = []
        i = []
        for j in range(len(a)):
            b = self.gee_e(a[j])
            if b:
                h.append(b)
            else:
                g.append(self.gee_d(a[j][0]))
                h.append(self.gee_d(a[j][1]))
            i.append(self.gee_d(a[j][2]))
        return "".join(g) + "!!" + "".join(h) + "!!" + "".join(i)


    def gee_userresponse(self, a, b):
        c = b[32:]
        
        d = []
        for i in range(len(c)):
            f = ord(c[i])
            d.append(f-87 if f > 57 else f-48)
        c = 36 * d[0] + d[1]
        g = round(a) + c
        b = b[0:32]
        i = [[],[],[],[],[]]
        j = {}
        k = 0
        for e in range(len(b)):
            h = b[e]
            if h not in j:
                j[h] = 1
                i[k].append(h)
                k = k + 1
                if k == 5: k = 0      
        n = g
        o = 4
        p = ""
        q = [1,2,5,10,50]
        while n > 0:
            if n - q[o] >= 0:
                m = int(random.random() * len(i[o]))
                p += str(i[o][m])
                
                n -= q[o]
            else:
                i = i[:o] + i[o+1:]
                q = q[:o] + q[o+1:]
                o -= 1
        return p


class crack_picture(object):
    def __init__(self, img_url1, img_url2):
        self.img1, self.img2 = self.picture_get(img_url1, img_url2)


    def picture_get(self, img_url1, img_url2):
        hd = {"Host": "static.geetest.com",
              "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)  Safari/537.36"}
        img1 = StringIO.StringIO(self.repeat(img_url1, hd).content)
        img2 = StringIO.StringIO(self.repeat(img_url2, hd).content)
        return img1, img2


    def repeat(self, url, hd):
        times = 10
        while times > 0:
            try:
                ans = requests.get(url, headers=hd)
                return ans
            except:
                times -= 1   


    def pictures_recover(self):
        xpos = self.judge(self.picture_recover(self.img1, 'img1.jpg'), self.picture_recover(self.img2, 'img2.jpg')) - 6
        return xpos, self.darbra_track(xpos)


    def picture_recover(self, img, name):
        a =[39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12, 13, 23, 22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]
        im = Image.open(img)
        im_new = Image.new("RGB", (260, 116))
        for row in range(2):
            for column in range(26):
                right = a[row*26+column] % 26 * 12 + 1
                down = 58 if a[row*26+column] > 25 else 0
                for w in range(10):
                    for h in range(58):
                        ht = 58 * row + h
                        wd = 10 * column + w
                        im_new.putpixel((wd, ht), im.getpixel((w + right, h + down)))
        im_new.save(name)
        return im_new


    def darbra_track(self, distance):
        if distance > 100:
            return []
        y_float = 0.0
        xps = distance
        #轨迹代码已删除


    def diff(self, img1, img2, wd, ht):
        rgb1 = img1.getpixel((wd, ht))
        rgb2 = img2.getpixel((wd, ht))
        tmp = reduce(lambda x,y: x+y, map(lambda x: abs(x[0]-x[1]), zip(rgb1, rgb2)))
        return True if tmp >= 190 else False

            
    def col(self, img1, img2, cl):
        for i in range(img2.size[1]):
            if self.diff(img1, img2, cl, i):
                return True
        return False


    def judge(self, img1, img2):
        for i in range(img2.size[0]):
            if self.col(img1, img2, i):
                return i
        return -1


if __name__ == "__main__":
    while True:
        jsh = jianshu()
        jsh.run()
        time.sleep(0.5)
