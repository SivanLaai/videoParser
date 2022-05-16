#encoding:utf-8
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import requests
import json
from lxml import etree
from io import StringIO, BytesIO
import os
import time
from subprocess import Popen, PIPE, STDOUT
from prettytable import PrettyTable
import execjs
from concurrent.futures import ThreadPoolExecutor


header_str = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Cache-Control: max-age=0
Connection: keep-alive
Host: v.pptv.com
If-Modified-Since: Sat, 16 Apr 2022 11:12:31 GMT
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39'''


class PPTVCrawler:

    name = "PPTV视频下载"

    url = 'https://ksyun.vod.pptv.com/'

    def __init__(self):
        pass

    def format_header(self, header_str=header_str, referer=''):
        header = dict()
        for line in header_str.split('\n'):
            line = line.replace(": ", ":")
            header[line.split(':')[0]] = ":".join(line.split(':')[1:])
            #header[line.split(': ')[0]] = line.split(': ')[1]

        return header

    def getVideoSetsDetailInfo(self, psid):
        url = f'https://epg.api.pptv.com/detail.api?ppi=302c3532&appId=ik&appPlt=web&appVer=1.0.0&format=jsonp&vid={psid}&series=1&contentType=preview&ver=4&userLevel=1&cb=jsonp_1650194982899_20656'
        header = self.format_header(header_str='''Host:epg.api.pptv.com
Connection:keep-alive
sec-ch-ua:" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"
sec-ch-ua-mobile:?0
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39
sec-ch-ua-platform:"Windows"
Accept:*/*
Sec-Fetch-Site:same-site
Sec-Fetch-Mode:no-cors
Sec-Fetch-Dest:script
Referer:https://v.pptv.com/
Accept-Encoding:gzip, deflate, br
Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6''')
        response = requests.get(url, headers=header)
        cxt = execjs.compile('''function jsonpToJson (datas) {
  let jsonData = null;
  // 下面是对获取到的数据进行处理，把jsonp格式的数据处理成json格式的数据
  if (typeof datas === 'string') {
    // 返回的是jsonp类型的数据，所以要用正则表达式来匹配截取json数据
    const reg = /^\w+\((\{[^()]+\})\)$/;
    const matches = datas.match(reg);
    // matches匹配到的是数组，数组第一个是所有正则表达式匹配的字符串，第二个是第一个小括号匹配到的字符串
    if (matches) {
      jsonData = JSON.parse(matches[1]);
    }
  }
  return jsonData;
};''' + f"\n var data = jsonpToJson('{response.text}');")
        data = cxt.eval('data')
        return data

    def getSeriesCIDAndTitle(self, psid, videoType=2):
        data = self.getVideoSetsDetailInfo(psid)
        title = data["v"]["title"]
        index = 1
        FilmResults = list()
        for episode in data["v"]["video_list"]["playlink2"]:
            curr = dict()
            #print(episode)
            curr['cid'] = episode["_attributes"]["id"]
            curr['videoType'] = videoType
            curr['title'] = f'{title}_{index}集'
            FilmResults.append(curr)
            index += 1
        return FilmResults

    def getFilmCIDAndTitle(self, PPTVUrl="http://v.pptv.com/show/hIbYV78lldM2tBw.html"):
        header = self.format_header()
        response = requests.get(PPTVUrl, headers=header)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(response.text), parser=parser)

        FilmResults = list()
        for node in tree.xpath("/html/body/script[1]/text()"):
            result = json.loads(str(node).replace('window.__INITIAL_STATE__= ', '')[:-1])
            channelType = result['channelType']
            if channelType == '电影':
                #curr = dict()
                #curr['cid'] = result['cid']
                #curr['title'] = result['detailContent']['baseInfo']['episodeTitle'].replace(' ', '')
                #curr['channelType'] = 1
                #FilmResults.append(curr)
                try:
                    FilmResults = self.getSeriesCIDAndTitle(result['detailContent']['baseInfo']['psid'], 1)
                except Exception as e:
                    curr = dict()
                    curr['cid'] = result['cid']
                    curr['title'] = result['detailContent']['baseInfo']['episodeTitle'].replace(' ', '')
                    curr['videoType'] = 1
                    FilmResults.append(curr)
            else:
                FilmResults = self.getSeriesCIDAndTitle(result['detailContent']['baseInfo']['psid'])
        return FilmResults

    def getFilmDownloadList(self, cid='32754820', videoName='爱情神话', videoType=1):
        apiUrl = f"http://play.api.cp61.ott.cibntv.net/boxplay.api?platform=launcher&contCoprChl=null&k_ver=1.1.1.11464&gslbversion=2&type=tv.android&userType=0&h265=0&content=need_drag&vvid=0&version=6&sv=6.3.0&id={cid}"
        #print (apiUrl)
        header = self.format_header(header_str='''Host: play.api.cp61.ott.cibntv.net
Proxy-Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6''')
        response = requests.get(apiUrl, headers=header)
        html=etree.HTML(response.content, etree.HTMLParser())

        #html = etree.parse('./test.html')
        file_list = list()
        tokens = list()

        for node in html.xpath('//file[@cur="1"]/item'):
            #print(node.attrib)
            file_list.append(node.attrib)
        for token in html.xpath('//dt/key'):
            tokens.append(token.text)
        for i in range(len(file_list)):
            file_list[i]['token'] = tokens[i]


        # todo_list
        # 修改名字为街道口的结果
        if videoType == 1:
            for node in html.xpath('//channel'):
                videoName = node.attrib['nm']
        download_list = list()
        for file in file_list:
            token = file["token"]
            name = file["rid"]
            bitrate = file["bitrate"]
            width = file["width"]
            height = file["height"]
            fileName = f"{videoName}_{height}P_bitrate_{bitrate}"
            fileSize = str(int(float(file["filesize"]) * 100 / (1024 * 1024)) / 100.0) + 'M'
            url = f"https://ksyun.vod.pptv.com/w/{name}?platform=launcher&type=tv.android&k={token}"
            curr = dict()
            curr['fileName'] = fileName
            curr['url'] = url
            curr['fileSize'] = fileSize
            curr['bitrate'] = bitrate
            curr['resolution'] = f"{width}*{height}"
            curr['format'] = file["format"]
            curr['name'] = videoName
            download_list.append(curr)
        return download_list


    def downloadVideo(self, url="000001", fileName="爱情神话", fileSize='100M'):
        # if (dataControl.FundIndustryExsits(fund_code)):
        #     return
        fileName = f"{fileName}.mp4"
        print(f"视频文件-{fileName}[大小：{fileSize}],开始下载....")
        if not os.path.exists("./Downloads"):
            os.mkdir("./Downloads")
        cmd = f'aria2c "{url}" -o "./Downloads/{fileName}"'
        #print(cmd)
        #stream = os.popen(cmd)
        #output = stream.read()
        code = self.exeCommand(cmd)
        if code == 0:
            print(f"文件-{fileName}[大小：{fileSize}],下载完成!")
        else:
            print(f"文件-{fileName}[大小：{fileSize}],下载失败!")

    def exeCommand(self, command):
        """
        执行 shell 命令并实时打印输出
        :param command: shell 命令
        :return: process, exitcode
        """
        process = subprocess.run(command, stderr=STDOUT, creationflags=subprocess.CREATE_NEW_CONSOLE)
        #process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        #with process.stdout:
        #    for line in iter(process.stdout.readline, b''):
        #        print(line.decode().strip())
        exitcode = process.returncode
        return exitcode

    def startSingleDownload(self, fileResults):
        videoIndex = int(input("请输入要下载的视频序号："))
        while videoIndex < 0 or videoIndex >= len(fileResults):
            print("输入序号错误，请重新输入！！！")
            videoIndex = int(input("请输入要下载的视频序号："))
        download_list = self.getFilmDownloadList(fileResults[videoIndex]['cid'], fileResults[videoIndex]['title'], fileResults[videoIndex]['videoType'])

        downloadTable = PrettyTable(["序号", "片名", "码率", "清晰度", "视频格式", "分辨率", "大小"])
        exportTable = PrettyTable(["序号", "片名", "分辨率", "码率", "下载链接"])
        definitions = ['标清', '高清', '超清', '蓝光', '原画']
        #print(download_list)
        for i in range(len(download_list)):
            downloadTable.add_row([i, download_list[i]['name'], download_list[i]['bitrate'], definitions[i], download_list[i]['format'], download_list[i]['resolution'], download_list[i]['fileSize']])
            exportTable.add_row([i, download_list[i]['name'], download_list[i]['bitrate'], download_list[i]['resolution'], download_list[i]['url']])
        print(downloadTable)
        exportConfirm = input("请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")
        resIndex = int(input("请输入要下载的视频分辨率:"))
        url = download_list[resIndex]['url']
        fileName = download_list[resIndex]['fileName']
        fileSize = download_list[resIndex]['fileSize']
        self.downloadVideo(url, fileName, fileSize)
        print()

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
        downloadTable = PrettyTable(["序号", "片名", "码率", "清晰度", "视频格式", "分辨率", "大小"])
        definitions = ['标清', '高清', '超清', '蓝光', '原画']
        if not exportFlag:
            resIndex = int(input("""0 - 标清， 1 - 高清，2 - 超清，3 - 蓝光，4 - 原画
如果选择的分辨率没有，默认下载最高清的资源
请选择要下载的视频清晰度:"""))

        else:
            resIndex = int(input("""0 - 标清， 1 - 高清，2 - 超清，3 - 蓝光，4 - 原画
如果选择的分辨率没有，默认导出最高清的资源
请选择要导出的视频清晰度:"""))
        num = 0
        exportTable = PrettyTable(["序号", "片名", "分辨率", "码率", "下载链接"])
        for videoIndex in videoIndexs:
            currDownlist = self.getFilmDownloadList(fileResults[videoIndex]['cid'], fileResults[videoIndex]['title'], fileResults[videoIndex]['videoType'])
            if len(currDownlist) == 0:
                print(f"cid = {fileResults[videoIndex]['cid']}，Title = {fileResults[videoIndex]['title']}：未从PPTV获取到接口资源。")
                continue

            currIndex = len(currDownlist) - 1
            if len(currDownlist) >= resIndex + 1:
                currIndex = resIndex
            downloadTable.add_row([num, currDownlist[currIndex]['name'], currDownlist[currIndex]['bitrate'], definitions[currIndex], currDownlist[currIndex]['format'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['fileSize']])
            exportTable.add_row([num, currDownlist[currIndex]['name'], currDownlist[currIndex]['bitrate'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['url']])
            num += 1
            download_list.append(currDownlist[currIndex])
            #print(download_list)
        print(downloadTable)
        if exportFlag:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")
            return
        exportConfirm = input("请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")

        downloadNums = int(input("马上进入下载，下载会弹出一个独占的aria2黑窗口进程，输入最大的同时下载个数，推荐5个:"))
        if downloadNums == "":
            downloadNums = 5
        threadPool = ThreadPoolExecutor(max_workers=downloadNums, thread_name_prefix="pptv_")
        for i in range(len(download_list)):
            url = download_list[i]['url']
            fileName = download_list[i]['fileName']
            fileSize = download_list[i]['fileSize']
            future = threadPool.submit(self.downloadVideo, url, fileName, fileSize)
            #self.downloadVideo(url, fileName, fileSize)
            print()
        threadPool.shutdown(wait=True)


    def startDownload(self):
        exitConfirm = 'N'
        while exitConfirm.lower() not in ['y', 'yes']:
            pptvurl = input("请输入PPTV视频网址：")
            fileResults = self.getFilmCIDAndTitle(PPTVUrl=pptvurl)
            videoTable = PrettyTable(["序号", "名称", "视频ID"])
            for i in range(len(fileResults)):
                videoTable.add_row([i, fileResults[i]['title'], fileResults[i]['cid']])
            print(videoTable)
            videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出
请输入选择的方式序号：""")
            while videoConfirm not in ['1', '2', '3', '4']:
                videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出
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


if __name__ == "__main__":
    PPTVCrawler().startDownload()
#encoding:utf-8
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import requests
import json
from lxml import etree
from io import StringIO, BytesIO
import os
import time
from subprocess import Popen, PIPE, STDOUT
from prettytable import PrettyTable
import execjs
from concurrent.futures import ThreadPoolExecutor


header_str = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Cache-Control: max-age=0
Connection: keep-alive
Host: v.pptv.com
If-Modified-Since: Sat, 16 Apr 2022 11:12:31 GMT
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39'''


class PPTVCrawler:

    name = "PPTV视频下载"

    url = 'https://ksyun.vod.pptv.com/'

    def __init__(self):
        pass

    def format_header(self, header_str=header_str, referer=''):
        header = dict()
        for line in header_str.split('\n'):
            line = line.replace(": ", ":")
            header[line.split(':')[0]] = ":".join(line.split(':')[1:])
            #header[line.split(': ')[0]] = line.split(': ')[1]

        return header

    def getVideoSetsDetailInfo(self, psid):
        url = f'https://epg.api.pptv.com/detail.api?ppi=302c3532&appId=ik&appPlt=web&appVer=1.0.0&format=jsonp&vid={psid}&series=1&contentType=preview&ver=4&userLevel=1&cb=jsonp_1650194982899_20656'
        header = self.format_header(header_str='''Host:epg.api.pptv.com
Connection:keep-alive
sec-ch-ua:" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"
sec-ch-ua-mobile:?0
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39
sec-ch-ua-platform:"Windows"
Accept:*/*
Sec-Fetch-Site:same-site
Sec-Fetch-Mode:no-cors
Sec-Fetch-Dest:script
Referer:https://v.pptv.com/
Accept-Encoding:gzip, deflate, br
Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6''')
        response = requests.get(url, headers=header)
        cxt = execjs.compile('''function jsonpToJson (datas) {
  let jsonData = null;
  // 下面是对获取到的数据进行处理，把jsonp格式的数据处理成json格式的数据
  if (typeof datas === 'string') {
    // 返回的是jsonp类型的数据，所以要用正则表达式来匹配截取json数据
    const reg = /^\w+\((\{[^()]+\})\)$/;
    const matches = datas.match(reg);
    // matches匹配到的是数组，数组第一个是所有正则表达式匹配的字符串，第二个是第一个小括号匹配到的字符串
    if (matches) {
      jsonData = JSON.parse(matches[1]);
    }
  }
  return jsonData;
};''' + f"\n var data = jsonpToJson('{response.text}');")
        data = cxt.eval('data')
        return data

    def getSeriesCIDAndTitle(self, psid, videoType=2):
        data = self.getVideoSetsDetailInfo(psid)
        title = data["v"]["title"]
        index = 1
        FilmResults = list()
        for episode in data["v"]["video_list"]["playlink2"]:
            curr = dict()
            #print(episode)
            curr['cid'] = episode["_attributes"]["id"]
            curr['videoType'] = videoType
            curr['title'] = f'{title}_{index}集'
            FilmResults.append(curr)
            index += 1
        return FilmResults

    def getFilmCIDAndTitle(self, PPTVUrl="http://v.pptv.com/show/hIbYV78lldM2tBw.html"):
        header = self.format_header()
        response = requests.get(PPTVUrl, headers=header)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(response.text), parser=parser)

        FilmResults = list()
        for node in tree.xpath("/html/body/script[1]/text()"):
            result = json.loads(str(node).replace('window.__INITIAL_STATE__= ', '')[:-1])
            channelType = result['channelType']
            if channelType == '电影':
                #curr = dict()
                #curr['cid'] = result['cid']
                #curr['title'] = result['detailContent']['baseInfo']['episodeTitle'].replace(' ', '')
                #curr['channelType'] = 1
                #FilmResults.append(curr)
                try:
                    FilmResults = self.getSeriesCIDAndTitle(result['detailContent']['baseInfo']['psid'], 1)
                except Exception as e:
                    curr = dict()
                    curr['cid'] = result['cid']
                    curr['title'] = result['detailContent']['baseInfo']['episodeTitle'].replace(' ', '')
                    curr['videoType'] = 1
                    FilmResults.append(curr)
            else:
                FilmResults = self.getSeriesCIDAndTitle(result['detailContent']['baseInfo']['psid'])
        return FilmResults

    def getFilmDownloadList(self, cid='32754820', videoName='爱情神话', videoType=1):
        apiUrl = f"http://play.api.cp61.ott.cibntv.net/boxplay.api?platform=launcher&contCoprChl=null&k_ver=1.1.1.11464&gslbversion=2&type=tv.android&userType=0&h265=0&content=need_drag&vvid=0&version=6&sv=6.3.0&id={cid}"
        #print (apiUrl)
        header = self.format_header(header_str='''Host: play.api.cp61.ott.cibntv.net
Proxy-Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6''')
        response = requests.get(apiUrl, headers=header)
        html=etree.HTML(response.content, etree.HTMLParser())

        #html = etree.parse('./test.html')
        file_list = list()
        tokens = list()

        for node in html.xpath('//file[@cur="1"]/item'):
            #print(node.attrib)
            file_list.append(node.attrib)
        for token in html.xpath('//dt/key'):
            tokens.append(token.text)
        for i in range(len(file_list)):
            file_list[i]['token'] = tokens[i]


        # todo_list
        # 修改名字为街道口的结果
        if videoType == 1:
            for node in html.xpath('//channel'):
                videoName = node.attrib['nm']
        download_list = list()
        for file in file_list:
            token = file["token"]
            name = file["rid"]
            bitrate = file["bitrate"]
            width = file["width"]
            height = file["height"]
            fileName = f"{videoName}_{height}P_bitrate_{bitrate}"
            fileSize = str(int(float(file["filesize"]) * 100 / (1024 * 1024)) / 100.0) + 'M'
            url = f"https://ksyun.vod.pptv.com/w/{name}?platform=launcher&type=tv.android&k={token}"
            curr = dict()
            curr['fileName'] = fileName
            curr['url'] = url
            curr['fileSize'] = fileSize
            curr['bitrate'] = bitrate
            curr['resolution'] = f"{width}*{height}"
            curr['format'] = file["format"]
            curr['name'] = videoName
            download_list.append(curr)
        return download_list


    def downloadVideo(self, url="000001", fileName="爱情神话", fileSize='100M'):
        # if (dataControl.FundIndustryExsits(fund_code)):
        #     return
        fileName = f"{fileName}.mp4"
        print(f"视频文件-{fileName}[大小：{fileSize}],开始下载....")
        if not os.path.exists("./Downloads"):
            os.mkdir("./Downloads")
        cmd = f'aria2c "{url}" -o "./Downloads/{fileName}"'
        #print(cmd)
        #stream = os.popen(cmd)
        #output = stream.read()
        code = self.exeCommand(cmd)
        if code == 0:
            print(f"文件-{fileName}[大小：{fileSize}],下载完成!")
        else:
            print(f"文件-{fileName}[大小：{fileSize}],下载失败!")

    def exeCommand(self, command):
        """
        执行 shell 命令并实时打印输出
        :param command: shell 命令
        :return: process, exitcode
        """
        process = subprocess.run(command, stderr=STDOUT, creationflags=subprocess.CREATE_NEW_CONSOLE)
        #process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        #with process.stdout:
        #    for line in iter(process.stdout.readline, b''):
        #        print(line.decode().strip())
        exitcode = process.returncode
        return exitcode

    def startSingleDownload(self, fileResults):
        videoIndex = int(input("请输入要下载的视频序号："))
        while videoIndex < 0 or videoIndex >= len(fileResults):
            print("输入序号错误，请重新输入！！！")
            videoIndex = int(input("请输入要下载的视频序号："))
        download_list = self.getFilmDownloadList(fileResults[videoIndex]['cid'], fileResults[videoIndex]['title'], fileResults[videoIndex]['videoType'])

        downloadTable = PrettyTable(["序号", "片名", "码率", "清晰度", "视频格式", "分辨率", "大小"])
        exportTable = PrettyTable(["序号", "片名", "分辨率", "码率", "下载链接"])
        definitions = ['标清', '高清', '超清', '蓝光', '原画']
        #print(download_list)
        for i in range(len(download_list)):
            downloadTable.add_row([i, download_list[i]['name'], download_list[i]['bitrate'], definitions[i], download_list[i]['format'], download_list[i]['resolution'], download_list[i]['fileSize']])
            exportTable.add_row([i, download_list[i]['name'], download_list[i]['bitrate'], download_list[i]['resolution'], download_list[i]['url']])
        print(downloadTable)
        exportConfirm = input("请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")
        resIndex = int(input("请输入要下载的视频分辨率:"))
        url = download_list[resIndex]['url']
        fileName = download_list[resIndex]['fileName']
        fileSize = download_list[resIndex]['fileSize']
        self.downloadVideo(url, fileName, fileSize)
        print()

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
        downloadTable = PrettyTable(["序号", "片名", "码率", "清晰度", "视频格式", "分辨率", "大小"])
        definitions = ['标清', '高清', '超清', '蓝光', '原画']
        if not exportFlag:
            resIndex = int(input("""0 - 标清， 1 - 高清，2 - 超清，3 - 蓝光，4 - 原画
如果选择的分辨率没有，默认下载最高清的资源
请选择要下载的视频清晰度:"""))

        else:
            resIndex = int(input("""0 - 标清， 1 - 高清，2 - 超清，3 - 蓝光，4 - 原画
如果选择的分辨率没有，默认导出最高清的资源
请选择要导出的视频清晰度:"""))
        num = 0
        exportTable = PrettyTable(["序号", "片名", "分辨率", "码率", "下载链接"])
        for videoIndex in videoIndexs:
            currDownlist = self.getFilmDownloadList(fileResults[videoIndex]['cid'], fileResults[videoIndex]['title'], fileResults[videoIndex]['videoType'])
            if len(currDownlist) == 0:
                print(f"cid = {fileResults[videoIndex]['cid']}，Title = {fileResults[videoIndex]['title']}：未从PPTV获取到接口资源。")
                continue

            currIndex = len(currDownlist) - 1
            if len(currDownlist) >= resIndex + 1:
                currIndex = resIndex
            downloadTable.add_row([num, currDownlist[currIndex]['name'], currDownlist[currIndex]['bitrate'], definitions[currIndex], currDownlist[currIndex]['format'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['fileSize']])
            exportTable.add_row([num, currDownlist[currIndex]['name'], currDownlist[currIndex]['bitrate'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['url']])
            num += 1
            download_list.append(currDownlist[currIndex])
            #print(download_list)
        print(downloadTable)
        if exportFlag:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")
            return
        exportConfirm = input("请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")

        downloadNums = int(input("马上进入下载，下载会弹出一个独占的aria2黑窗口进程，输入最大的同时下载个数，推荐5个:"))
        if downloadNums == "":
            downloadNums = 5
        threadPool = ThreadPoolExecutor(max_workers=downloadNums, thread_name_prefix="pptv_")
        for i in range(len(download_list)):
            url = download_list[i]['url']
            fileName = download_list[i]['fileName']
            fileSize = download_list[i]['fileSize']
            future = threadPool.submit(self.downloadVideo, url, fileName, fileSize)
            #self.downloadVideo(url, fileName, fileSize)
            print()
        threadPool.shutdown(wait=True)


    def startDownload(self):
        exitConfirm = 'N'
        while exitConfirm.lower() not in ['y', 'yes']:
            pptvurl = input("请输入PPTV视频网址：")
            fileResults = self.getFilmCIDAndTitle(PPTVUrl=pptvurl)
            videoTable = PrettyTable(["序号", "名称", "视频ID"])
            for i in range(len(fileResults)):
                videoTable.add_row([i, fileResults[i]['title'], fileResults[i]['cid']])
            print(videoTable)
            videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出
请输入选择的方式序号：""")
            while videoConfirm not in ['1', '2', '3', '4']:
                videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出
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


if __name__ == "__main__":
    PPTVCrawler().startDownload()
#encoding:utf-8
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import requests
import json
from lxml import etree
from io import StringIO, BytesIO
import os
import time
from subprocess import Popen, PIPE, STDOUT
from prettytable import PrettyTable
import execjs
from concurrent.futures import ThreadPoolExecutor


header_str = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Cache-Control: max-age=0
Connection: keep-alive
Host: v.pptv.com
If-Modified-Since: Sat, 16 Apr 2022 11:12:31 GMT
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39'''


class PPTVCrawler:

    name = "PPTV视频下载"

    url = 'https://ksyun.vod.pptv.com/'

    def __init__(self):
        pass

    def format_header(self, header_str=header_str, referer=''):
        header = dict()
        for line in header_str.split('\n'):
            line = line.replace(": ", ":")
            header[line.split(':')[0]] = ":".join(line.split(':')[1:])
            #header[line.split(': ')[0]] = line.split(': ')[1]

        return header

    def getVideoSetsDetailInfo(self, psid):
        url = f'https://epg.api.pptv.com/detail.api?ppi=302c3532&appId=ik&appPlt=web&appVer=1.0.0&format=jsonp&vid={psid}&series=1&contentType=preview&ver=4&userLevel=1&cb=jsonp_1650194982899_20656'
        header = self.format_header(header_str='''Host:epg.api.pptv.com
Connection:keep-alive
sec-ch-ua:" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"
sec-ch-ua-mobile:?0
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39
sec-ch-ua-platform:"Windows"
Accept:*/*
Sec-Fetch-Site:same-site
Sec-Fetch-Mode:no-cors
Sec-Fetch-Dest:script
Referer:https://v.pptv.com/
Accept-Encoding:gzip, deflate, br
Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6''')
        response = requests.get(url, headers=header)
        cxt = execjs.compile('''function jsonpToJson (datas) {
  let jsonData = null;
  // 下面是对获取到的数据进行处理，把jsonp格式的数据处理成json格式的数据
  if (typeof datas === 'string') {
    // 返回的是jsonp类型的数据，所以要用正则表达式来匹配截取json数据
    const reg = /^\w+\((\{[^()]+\})\)$/;
    const matches = datas.match(reg);
    // matches匹配到的是数组，数组第一个是所有正则表达式匹配的字符串，第二个是第一个小括号匹配到的字符串
    if (matches) {
      jsonData = JSON.parse(matches[1]);
    }
  }
  return jsonData;
};''' + f"\n var data = jsonpToJson('{response.text}');")
        data = cxt.eval('data')
        return data

    def getSeriesCIDAndTitle(self, psid, videoType=2):
        data = self.getVideoSetsDetailInfo(psid)
        title = data["v"]["title"]
        index = 1
        FilmResults = list()
        for episode in data["v"]["video_list"]["playlink2"]:
            curr = dict()
            #print(episode)
            curr['cid'] = episode["_attributes"]["id"]
            curr['videoType'] = videoType
            curr['title'] = f'{title}_{index}集'
            FilmResults.append(curr)
            index += 1
        return FilmResults

    def getFilmCIDAndTitle(self, PPTVUrl="http://v.pptv.com/show/hIbYV78lldM2tBw.html"):
        header = self.format_header()
        response = requests.get(PPTVUrl, headers=header)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(response.text), parser=parser)

        FilmResults = list()
        for node in tree.xpath("/html/body/script[1]/text()"):
            result = json.loads(str(node).replace('window.__INITIAL_STATE__= ', '')[:-1])
            channelType = result['channelType']
            if channelType == '电影':
                #curr = dict()
                #curr['cid'] = result['cid']
                #curr['title'] = result['detailContent']['baseInfo']['episodeTitle'].replace(' ', '')
                #curr['channelType'] = 1
                #FilmResults.append(curr)
                try:
                    FilmResults = self.getSeriesCIDAndTitle(result['detailContent']['baseInfo']['psid'], 1)
                except Exception as e:
                    curr = dict()
                    curr['cid'] = result['cid']
                    curr['title'] = result['detailContent']['baseInfo']['episodeTitle'].replace(' ', '')
                    curr['videoType'] = 1
                    FilmResults.append(curr)
            else:
                FilmResults = self.getSeriesCIDAndTitle(result['detailContent']['baseInfo']['psid'])
        return FilmResults

    def getFilmDownloadList(self, cid='32754820', videoName='爱情神话', videoType=1):
        apiUrl = f"http://play.api.cp61.ott.cibntv.net/boxplay.api?platform=launcher&contCoprChl=null&k_ver=1.1.1.11464&gslbversion=2&type=tv.android&userType=0&h265=0&content=need_drag&vvid=0&version=6&sv=6.3.0&id={cid}"
        #print (apiUrl)
        header = self.format_header(header_str='''Host: play.api.cp61.ott.cibntv.net
Proxy-Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6''')
        response = requests.get(apiUrl, headers=header)
        html=etree.HTML(response.content, etree.HTMLParser())

        #html = etree.parse('./test.html')
        file_list = list()
        tokens = list()

        for node in html.xpath('//file[@cur="1"]/item'):
            #print(node.attrib)
            file_list.append(node.attrib)
        for token in html.xpath('//dt/key'):
            tokens.append(token.text)
        for i in range(len(file_list)):
            file_list[i]['token'] = tokens[i]


        # todo_list
        # 修改名字为街道口的结果
        if videoType == 1:
            for node in html.xpath('//channel'):
                videoName = node.attrib['nm']
        download_list = list()
        for file in file_list:
            token = file["token"]
            name = file["rid"]
            bitrate = file["bitrate"]
            width = file["width"]
            height = file["height"]
            fileName = f"{videoName}_{height}P_bitrate_{bitrate}"
            fileSize = str(int(float(file["filesize"]) * 100 / (1024 * 1024)) / 100.0) + 'M'
            url = f"https://ksyun.vod.pptv.com/w/{name}?platform=launcher&type=tv.android&k={token}"
            curr = dict()
            curr['fileName'] = fileName
            curr['url'] = url
            curr['fileSize'] = fileSize
            curr['bitrate'] = bitrate
            curr['resolution'] = f"{width}*{height}"
            curr['format'] = file["format"]
            curr['name'] = videoName
            download_list.append(curr)
        return download_list


    def downloadVideo(self, url="000001", fileName="爱情神话", fileSize='100M'):
        # if (dataControl.FundIndustryExsits(fund_code)):
        #     return
        fileName = f"{fileName}.mp4"
        print(f"视频文件-{fileName}[大小：{fileSize}],开始下载....")
        if not os.path.exists("./Downloads"):
            os.mkdir("./Downloads")
        cmd = f'aria2c "{url}" -o "./Downloads/{fileName}"'
        #print(cmd)
        #stream = os.popen(cmd)
        #output = stream.read()
        code = self.exeCommand(cmd)
        if code == 0:
            print(f"文件-{fileName}[大小：{fileSize}],下载完成!")
        else:
            print(f"文件-{fileName}[大小：{fileSize}],下载失败!")

    def exeCommand(self, command):
        """
        执行 shell 命令并实时打印输出
        :param command: shell 命令
        :return: process, exitcode
        """
        process = subprocess.run(command, stderr=STDOUT, creationflags=subprocess.CREATE_NEW_CONSOLE)
        #process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        #with process.stdout:
        #    for line in iter(process.stdout.readline, b''):
        #        print(line.decode().strip())
        exitcode = process.returncode
        return exitcode

    def startSingleDownload(self, fileResults):
        videoIndex = int(input("请输入要下载的视频序号："))
        while videoIndex < 0 or videoIndex >= len(fileResults):
            print("输入序号错误，请重新输入！！！")
            videoIndex = int(input("请输入要下载的视频序号："))
        download_list = self.getFilmDownloadList(fileResults[videoIndex]['cid'], fileResults[videoIndex]['title'], fileResults[videoIndex]['videoType'])

        downloadTable = PrettyTable(["序号", "片名", "码率", "清晰度", "视频格式", "分辨率", "大小"])
        exportTable = PrettyTable(["序号", "片名", "分辨率", "码率", "下载链接"])
        definitions = ['标清', '高清', '超清', '蓝光', '原画']
        #print(download_list)
        for i in range(len(download_list)):
            downloadTable.add_row([i, download_list[i]['name'], download_list[i]['bitrate'], definitions[i], download_list[i]['format'], download_list[i]['resolution'], download_list[i]['fileSize']])
            exportTable.add_row([i, download_list[i]['name'], download_list[i]['bitrate'], download_list[i]['resolution'], download_list[i]['url']])
        print(downloadTable)
        exportConfirm = input("请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")
        resIndex = int(input("请输入要下载的视频分辨率:"))
        url = download_list[resIndex]['url']
        fileName = download_list[resIndex]['fileName']
        fileSize = download_list[resIndex]['fileSize']
        self.downloadVideo(url, fileName, fileSize)
        print()

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
        downloadTable = PrettyTable(["序号", "片名", "码率", "清晰度", "视频格式", "分辨率", "大小"])
        definitions = ['标清', '高清', '超清', '蓝光', '原画']
        if not exportFlag:
            resIndex = int(input("""0 - 标清， 1 - 高清，2 - 超清，3 - 蓝光，4 - 原画
如果选择的分辨率没有，默认下载最高清的资源
请选择要下载的视频清晰度:"""))

        else:
            resIndex = int(input("""0 - 标清， 1 - 高清，2 - 超清，3 - 蓝光，4 - 原画
如果选择的分辨率没有，默认导出最高清的资源
请选择要导出的视频清晰度:"""))
        num = 0
        exportTable = PrettyTable(["序号", "片名", "分辨率", "码率", "下载链接"])
        for videoIndex in videoIndexs:
            currDownlist = self.getFilmDownloadList(fileResults[videoIndex]['cid'], fileResults[videoIndex]['title'], fileResults[videoIndex]['videoType'])
            if len(currDownlist) == 0:
                print(f"cid = {fileResults[videoIndex]['cid']}，Title = {fileResults[videoIndex]['title']}：未从PPTV获取到接口资源。")
                continue

            currIndex = len(currDownlist) - 1
            if len(currDownlist) >= resIndex + 1:
                currIndex = resIndex
            downloadTable.add_row([num, currDownlist[currIndex]['name'], currDownlist[currIndex]['bitrate'], definitions[currIndex], currDownlist[currIndex]['format'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['fileSize']])
            exportTable.add_row([num, currDownlist[currIndex]['name'], currDownlist[currIndex]['bitrate'], currDownlist[currIndex]['resolution'], currDownlist[currIndex]['url']])
            num += 1
            download_list.append(currDownlist[currIndex])
            #print(download_list)
        print(downloadTable)
        if exportFlag:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")
            return
        exportConfirm = input("请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):")
        if exportConfirm == "":
            exportConfirm = 2
        if int(exportConfirm) == 1:
            with open('export.txt', 'w') as pptv:
                pptv.write(exportTable.get_string())
            print("下载链接已经导入到export.txt")

        downloadNums = int(input("马上进入下载，下载会弹出一个独占的aria2黑窗口进程，输入最大的同时下载个数，推荐5个:"))
        if downloadNums == "":
            downloadNums = 5
        threadPool = ThreadPoolExecutor(max_workers=downloadNums, thread_name_prefix="pptv_")
        for i in range(len(download_list)):
            url = download_list[i]['url']
            fileName = download_list[i]['fileName']
            fileSize = download_list[i]['fileSize']
            future = threadPool.submit(self.downloadVideo, url, fileName, fileSize)
            #self.downloadVideo(url, fileName, fileSize)
            print()
        threadPool.shutdown(wait=True)


    def startDownload(self):
        exitConfirm = 'N'
        while exitConfirm.lower() not in ['y', 'yes']:
            pptvurl = input("请输入PPTV视频网址：")
            fileResults = self.getFilmCIDAndTitle(PPTVUrl=pptvurl)
            videoTable = PrettyTable(["序号", "名称", "视频ID"])
            for i in range(len(fileResults)):
                videoTable.add_row([i, fileResults[i]['title'], fileResults[i]['cid']])
            print(videoTable)
            videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出
请输入选择的方式序号：""")
            while videoConfirm not in ['1', '2', '3', '4']:
                videoConfirm = input("""
请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出
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


if __name__ == "__main__":
    PPTVCrawler().startDownload()

