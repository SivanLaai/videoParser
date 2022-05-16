import requests
import re
import time
from m3u8download_hecoter import m3u8download
from prettytable import PrettyTable
import subprocess
from subprocess import Popen, PIPE, STDOUT
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
import json
import os
import configparser

config = configparser.ConfigParser()
config.sections()
config.read("cookies.ini")


definitionsMap = {
        "4K":   "8",
        "蓝光": "6",
        "超清": "5",
        "高清": "3",
        "流畅": "2",
        "低清": "1",
        }
bidMap = {
        "8" : "4K",
        "6" : "1080P",
        "5" : "720P",
        "3" : "540P",
        "2" : "360P",
        "1" : "210P",
        }

class IQIYI:
    def __init__(self,):
        self.Cookie = config["COOKIE"]["Cookie"]
        self.Cookie_P00003 = config["COOKIE"]["Cookie_P00003"]
        self.Cookie_QC005 = config["COOKIE"]["Cookie_QC005"]
        self.Cookie_dfp = config["COOKIE"]["Cookie_dfp"]
        self.url = ""

    def get_vf(self,url):
        with open('helper.js', 'r', encoding='utf-8') as f:
            js = f.read()

        cxt = execjs.compile(js)
        vf = cxt.call('parse_vf', url)
        return vf

    def format_header(self, header_str='', referer=''):
        header = dict()
        for line in header_str.split('\n'):
            line = line.replace(": ", ":")
            header[line.split(':')[0]] = ":".join(line.split(':')[1:])
            #header[line.split(': ')[0]] = line.split(': ')[1]

        return header

    def parseVideos(self, FilmResults, aid, data):
        for d in data:
            #print(d)
            curr = dict()
            curr['title'] = d["name"]
            curr['aid'] = aid
            curr['tvid'] = d["tvId"]
            curr['vid'] = d["vid"]
            curr['url'] = d["playUrl"]
            #self.parseCurrUrlVideo(FilmResults, TVUrl=d["playUrl"])
            FilmResults.append(curr)

    def getSeriesVideoTitle(self, aid):
        header_str = '''User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39'''
        header = self.format_header(header_str=header_str)
        pageIndex = 1
        url = \
        f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={aid}&page={pageIndex}&size=30&callback=jsonp_1652620011037_27673"
        response = requests.get(url, headers=header).text
        s = response.find("({")
        e = response.rfind("}}")
        data = json.loads(response[s+1:e+2])["data"]["epsodelist"]
        FilmResults = list()
        self.parseVideos(FilmResults, aid, data)
        while len(data) > 0:
            pageIndex += 1
            url = \
            f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={aid}&page={pageIndex}&size=30&callback=jsonp_1652620011037_27673"
            response = requests.get(url, headers=header).text
            s = response.find("({")
            e = response.rfind("}}")
            data = json.loads(response[s+1:e+2])["data"]["epsodelist"]
            self.parseVideos(FilmResults, aid, data)
        return FilmResults

    def parseCurrUrlVideo(self, FilmResults, response=None, TVUrl=None):
        if response is None:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.75',
                'cookie': self.Cookie
            }
            response = requests.get(url=TVUrl, headers=headers).text

        html=etree.HTML(response, etree.HTMLParser())

        aid = re.findall('"albumId":(\d+)', response)[0]
        tvid = re.findall('"tvId":(\d+)', response)[0]
        vid = re.findall('"vid":"(.+?)"', response)[0]
        for node in html.xpath('//title'):
            curr = dict()
            curr['title'] = node.text.split('-')[0]
            curr['aid'] = aid
            curr['tvid'] = tvid
            curr['vid'] = vid
            curr['url'] = TVUrl
            FilmResults.append(curr)

    def getVideoTitle(self, TVUrl):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.75',
            'cookie': self.Cookie
        }
        response = requests.get(url=TVUrl, headers=headers).text
        html=etree.HTML(response, etree.HTMLParser())
        FilmResults = list()

        aid = re.findall('"albumId":(\d+)', response)[0]
        #for node in html.xpath('//meta[@name="apple-itunes-app"]'):
        #    aid = node.attrib["content"].split("&")[-3].split("=")[1]

        for node in html.xpath('//title'):
            videoType = node.text.split('-')[1]
            if "电影" in videoType:
                self.parseCurrUrlVideo(FilmResults, response)
            else:
                FilmResults = self.getSeriesVideoTitle(aid)
            break
        return FilmResults

    def downloadVideo(self, title, m3u8url, exportConfirm=2):
        #m3u8download(m3u8url=m3u8url,title=title)
        if exportConfirm == 2:
            os.remove(m3u8url)


    def getFilmDownloadList(self, tvid='32754820', vid='32754820', videoName='爱情神话'):
        #print (apiUrl)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.75',
            'cookie': self.Cookie
        }
        tm = int(time.time() * 1000)
        bid = 800
        url_with_dash_but_vf2 = f'/jp/dash?tvid={tvid}&bid={bid}&vid={vid}&src=03020031010000000000&vt=0&rs=1&uid={self.Cookie_P00003}&ori=pcw&ps=0&k_uid={self.Cookie_QC005}&pt=0&d=0&s=&lid=&cf=&ct=&k_tag=1&ost=0&ppt=0&dfp={self.Cookie_dfp}&locale=zh_cn&k_err_retries=0&qd_v=2&tm={tm}&qdy=a&qds=0&k_ft2=8191&callback=hecoter&ut=1'
        vf = self.get_vf(url_with_dash_but_vf2)

        videoCacheUrl = 'https://cache.video.iqiyi.com' + vf
        response = requests.get(url=videoCacheUrl, headers=headers).text
        s = response.find("({")
        e = response.rfind("}\n")
        data = json.loads(response[s+1:e+2])["data"]["program"]["video"]
        videoList = list()
        for d in data:
            curr = dict()
            curr["bid"] = d["bid"]
            curr["vid"] = d["vid"]
            if d["ff"] == "f4v":
                curr["format"] = "H264"
            else:
                curr["format"] = "H265"
            videoList.append(curr)
        #print(videoList)
        download_list = list()
        for video in videoList:
            bid = video["bid"]
            vid = video["vid"]
            format = video["format"]
            tm = int(time.time() * 1000)
            url_with_dash_but_vf2 = f'/jp/dash?tvid={tvid}&bid={bid}&vid={vid}&src=03020031010000000000&vt=0&rs=1&uid={self.Cookie_P00003}&ori=pcw&ps=0&k_uid={self.Cookie_QC005}&pt=0&d=0&s=&lid=&cf=&ct=&k_tag=1&ost=0&ppt=0&dfp={self.Cookie_dfp}&locale=zh_cn&k_err_retries=0&qd_v=2&tm={tm}&qdy=a&qds=0&k_ft2=8191&callback=hecoter&ut=1'
            vf = self.get_vf(url_with_dash_but_vf2)

            videoCacheUrl = 'https://cache.video.iqiyi.com' + vf
            response = requests.get(url=videoCacheUrl, headers=headers).text
            s = response.find("({")
            e = response.rfind("}\n")
            data = json.loads(response[s+1:e+2])["data"]["program"]["video"]
            videoInfo = None
            for d in data:
                if d["_selected"] and bid == d["bid"]:
                    videoInfo = d
                    break
            if videoInfo is None:
                continue
            m3u8 = videoInfo["m3u8"]
            #m3u8 = re.findall('"m3u8":"(.+?)"', response)[0].replace('/', '').replace('\\', '/')
            m3u8s = m3u8.split('/n')
            m3u8 = '\n'.join(m3u8s)

            vsize = videoInfo["vsize"]
            vsize = int(int(vsize) / 1024.0 / 1024)
            vssize = str(vsize) + 'MB'
            scrsz = videoInfo["scrsz"]
            fileName = f"{videoName}_{bidMap[str(bid)[0]]}_format_{format}"
            if not os.path.exists("./Downloads"):
                os.mkdir("./Downloads")
            m3u8url = f'./Downloads/{fileName}.m3u8'

            with open(m3u8url, 'w', encoding='utf-8') as f:
                f.write(m3u8)

            curr = dict()
            curr['fileName'] = fileName
            curr['m3u8url'] = m3u8url
            #curr['m3u8'] = m3u8
            curr['fileSize'] = vssize
            curr['resolution'] = scrsz
            curr['format'] = format
            curr['name'] = videoName
            curr['definition'] = bidMap[str(bid)[0]]
            curr['bid'] = str(bid)
            download_list.append(curr)
        return download_list

    def startSingleDownload(self, fileResults):
        videoIndex = int(input("请输入要下载的视频序号："))

        while videoIndex < 0 or videoIndex >= len(fileResults):
            print("输入序号错误，请重新输入！！！")
            videoIndex = int(input("请输入要下载的视频序号："))
        download_list = self.getFilmDownloadList(fileResults[videoIndex]['tvid'], fileResults[videoIndex]['vid'], fileResults[videoIndex]['title'])

        downloadTable = PrettyTable(["序号", "片名", "清晰度", "视频格式", "分辨率", "大小"])
        exportTable = PrettyTable(["序号", "片名", "分辨率", "清晰度", "视频格式", "m3u8文件"])
        #print(download_list)
        exportConfirm = input("请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2

        for i in range(len(download_list)):
            downloadTable.add_row([i, download_list[i]['name'], download_list[i]['definition'], download_list[i]['format'], download_list[i]['resolution'], download_list[i]['fileSize']])
            exportTable.add_row([i, download_list[i]['name'], download_list[i]['resolution'], download_list[i]['definition'], \
                download_list[i]['format'], download_list[i]['m3u8url']])
        print(downloadTable)
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("m3u8文件汇总已经导出到export.txt")
        resIndex = int(input("请输入要下载的视频序号:"))
        m3u8url = download_list[resIndex]['m3u8url']
        fileName = download_list[resIndex]['fileName']
        self.downloadVideo(fileName, m3u8url, exportConfirm)
        if int(exportConfirm) == 2:
            for i in range(len(download_list)):
                os.remove(download_list[i]["m3u8url"])
        print()

    def selectDefinition(self, definition, download_list):
        bidStart = definitionsMap[definition]
        for i in range(len(download_list)):
            if bidStart == download_list[i]["bid"][0]:
                return i
        for bidStart in bidMap:
            for i in range(len(download_list)):
                if bidStart == download_list[i]["bid"][0]:
                    return i
        return 0

    def startMultSelectedDownload(self, fileResults, downloadAllFlag=False, exportFlag=False):
        videoIndexs = list()
        if exportFlag:
            videoIndexStr = input("""
当前是批量导出：
输入 1-4 会批量导出第1到第4个视频，如有多个区间则用逗号(逗号应为英文逗号)分开 如 1-3, 5-8
请输入要批量导出的多选视频序号：""").replace('，', ',')
            for indexs in videoIndexStr.split(','):
                indexs = [int(index) for index in indexs.split('-')]
                if len(indexs) == 1:
                    videoIndexs.append(indexs[0])
                    continue
                for index in range(indexs[0], indexs[1] + 1):
                    videoIndexs.append(index)
        elif not downloadAllFlag:
            videoIndexStr = input("""
当前是多选视频下载：
输入 1-4 会下载第1到第4个视频，如有多个区间则用逗号(逗号应为英文逗号)分开 如 1-3, 5-8
请输入要下载的多选视频序号：""").replace('，', ',')
            for indexs in videoIndexStr.split(','):
                indexs = [int(index) for index in indexs.split('-')]
                for index in range(indexs[0], indexs[1] + 1):
                    videoIndexs.append(index)
        else:
            videoIndexs = range(len(fileResults))
        download_list = list()
        downloadTable = PrettyTable(["序号", "片名", "清晰度", "视频格式", "分辨率", "大小"])
        definitions = ['低清', '流畅', '高清', '超清', '蓝光', '4K']
        if not exportFlag:
            resIndex = int(input("""0 - 低清，1 - 流畅， 2 - 高清，3 - 超清，4 - 蓝光，5 - 4K
如果选择的分辨率没有，默认下载最高清的资源
请选择要下载的视频清晰度:"""))

        else:
            resIndex = int(input("""0 - 低清，1 - 流畅， 2 - 高清，3 - 超清，4 - 蓝光，5 - 4K
如果选择的分辨率没有，默认导出最高清的资源
请选择要导出的视频清晰度:"""))
        i = 0
        exportTable = PrettyTable(["序号", "片名", "分辨率", "清晰度", "视频格式", "m3u8文件"])
        for videoIndex in videoIndexs:
            currDownlist = self.getFilmDownloadList(fileResults[videoIndex]['tvid'], fileResults[videoIndex]['vid'], fileResults[videoIndex]['title'])
            currIndex = self.selectDefinition(definitions[resIndex], currDownlist)
            downloadTable.add_row([i, currDownlist[currIndex]['name'], currDownlist[currIndex]['definition'], currDownlist[currIndex]['format'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['fileSize']])
            exportTable.add_row([i, currDownlist[currIndex]['name'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['definition'], \
                currDownlist[currIndex]['format'], currDownlist[currIndex]['m3u8url']])
            i += 1
            download_list.append(currDownlist[currIndex])
        print(downloadTable)
        if exportFlag:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("m3u8文件已经导入到export.txt")
            return
        exportConfirm = input("请选择是否导出m3u8文件到export.txt(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("m3u8文件已经导入到export.txt")

        for i in range(len(download_list)):
            m3u8url = download_list[i]['m3u8url']
            fileName = download_list[i]['fileName']
            print(f"下载第{i+1}/{len(download_list)}个文件：")
            self.downloadVideo(fileName, m3u8url, exportConfirm)
            print()


    def startDownload(self):
        exitConfirm = 'N'
        while exitConfirm.lower() not in ['y', 'yes']:
            pptvurl = input("请输入iqiyi视频网址：")
            self.url = pptvurl
            fileResults = self.getVideoTitle(TVUrl=pptvurl)
            videoTable = PrettyTable(["序号", "名称"])
            for i in range(len(fileResults)):
                videoTable.add_row([i, fileResults[i]['title']])
            print(videoTable)
            videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出m3u8
请输入选择的方式序号：""")
            while videoConfirm not in ['1', '2', '3', '4']:
                videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出m3u8
请输入选择的方式序号：""")
            if videoConfirm == '':
                videoConfirm = 1
            videoConfirm = int(videoConfirm)
            if videoConfirm == 1:
                self.startSingleDownload(fileResults)
            elif videoConfirm == 2:
                self.startMultSelectedDownload(fileResults)
            elif videoConfirm == 3:
                self.startMultSelectedDownload(fileResults, downloadAllFlag=True)
            else:
                self.startMultSelectedDownload(fileResults, exportFlag=True)
            exitConfirm = input("""
程序任务完成，是否退出程序？(默认为不退出)：
Yes(Y).退出    No(N).不退出
请输入方式：""")

if "__main__" == __name__:
    iqiyi = IQIYI().startDownload()

