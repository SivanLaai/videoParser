 # 视频下载工具
 ## dependecny
  - [Python 3.10](https://www.python.org/downloads/)
  - [nodejs](http://nodejs.cn/download/)
  - [aria2 1.36.0](https://github.com/aria2/aria2/releases/tag/release-1.36.0)
  - [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases)
 ## release版本
 - 不想安装环境可以直接下载[release版本](https://github.com/SivanLaai/videoParser/releases/tag/1.1)，集成了所有的可执行文件
 ## PPTV
- 使用方法
```bash
git clone https://github.com/SivanLaai/videoParser.git
pip install -r requirements.txt
cd pptv
# 下载aria2c执行文件到pptv目录或者添加到系统环境变量
python pptv.py
# 根据提示会下载视频文件在同级目录下的Downloads
```
- 使用过程示例
```
请输入PPTV视频网址：https://v.pptv.com/show/ia926OKAGdrQXlf0.html
+------+---------------+----------+
| 序号 |      名称     |  视频ID  |
+------+---------------+----------+
|  0   |  迷局1931_1集 | 30721134 |
|  1   |  迷局1931_2集 | 30721136 |
|  2   |  迷局1931_3集 | 30721138 |
|  3   |  迷局1931_4集 | 30721142 |
|  4   |  迷局1931_5集 | 30721148 |
|  5   |  迷局1931_6集 | 30728318 |
|  6   |  迷局1931_7集 | 30728320 |
|  7   |  迷局1931_8集 | 30728321 |
|  8   |  迷局1931_9集 | 30728323 |
|  9   | 迷局1931_10集 | 30728324 |
|  10  | 迷局1931_11集 | 30728325 |
|  11  | 迷局1931_12集 | 30728319 |
|  12  | 迷局1931_13集 | 30728326 |
|  13  | 迷局1931_14集 | 30734830 |
|  14  | 迷局1931_15集 | 30734840 |
|  15  | 迷局1931_16集 | 30734843 |
|  16  | 迷局1931_17集 | 30734855 |
|  17  | 迷局1931_18集 | 30734866 |
|  18  | 迷局1931_19集 | 30734879 |
|  19  | 迷局1931_20集 | 30734886 |
|  20  | 迷局1931_21集 | 30734895 |
|  21  | 迷局1931_22集 | 30734901 |
|  22  | 迷局1931_23集 | 30751240 |
|  23  | 迷局1931_24集 | 30751252 |
|  24  | 迷局1931_25集 | 30750806 |
|  25  | 迷局1931_26集 | 30750929 |
|  26  | 迷局1931_27集 | 30750954 |
|  27  | 迷局1931_28集 | 30750980 |
|  28  | 迷局1931_29集 | 30751008 |
|  29  | 迷局1931_30集 | 30751079 |
|  30  | 迷局1931_31集 | 30751145 |
|  31  | 迷局1931_32集 | 30751184 |
+------+---------------+----------+

请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出
请输入选择的方式序号：1
请输入要下载的视频序号：1
+------+--------------+------+--------+----------+-----------+----------+
| 序号 |     片名     | 码率 | 清晰度 | 视频格式 |   分辨率  |   大小   |
+------+--------------+------+--------+----------+-----------+----------+
|  0   | 迷局1931_2集 | 271  |  标清  |   h264   |  480*272  |  87.61M  |
|  1   | 迷局1931_2集 | 861  |  高清  |   h264   |  720*404  | 278.04M  |
|  2   | 迷局1931_2集 | 1396 |  超清  |   h264   |  1280*720 | 450.66M  |
|  3   | 迷局1931_2集 | 2636 |  蓝光  |   h264   | 1920*1080 | 850.59M  |
|  4   | 迷局1931_2集 | 5090 |  原画  |   h264   | 1920*1080 | 1642.55M |
+------+--------------+------+--------+----------+-----------+----------+
请选择是否导出下载链接(1-表示导出，2-表示不导出，默认不导出):2
请输入要下载的视频分辨率:0
视频文件-迷局1931_2集_272P_bitrate_271.mp4[大小：87.61M],开始下载....
```
## 爱奇艺（不依赖浏览器使用cmd5x破解，支持解析4K画质）
- 使用方法
```bash
git clone https://github.com/SivanLaai/videoParser.git
pip install -r requirements.txt
cd iqiyi
# 配置cookies，直接在cookies.ini中配置相关值 
# 下载ffmpeg执行文件到iqiyi目录或者添加到系统环境变量
python iqiyi.py
# 根据提示会下载视频文件在同级目录下的Downloads
```
- 使用过程示例
```
请输入iqiyi视频网址：https://www.iqiyi.com/v_19ruzj8gv0.html
+------+--------------+
| 序号 |     名称     |
+------+--------------+
|  0   | 庆余年第1集  |
|  1   | 庆余年第2集  |
|  2   | 庆余年第3集  |
|  3   | 庆余年第4集  |
|  4   | 庆余年第5集  |
|  5   | 庆余年第6集  |
|  6   | 庆余年第7集  |
|  7   | 庆余年第8集  |
|  8   | 庆余年第9集  |
|  9   | 庆余年第10集 |
|  10  | 庆余年第11集 |
|  11  | 庆余年第12集 |
|  12  | 庆余年第13集 |
|  13  | 庆余年第14集 |
|  14  | 庆余年第15集 |
|  15  | 庆余年第16集 |
|  16  | 庆余年第17集 |
|  17  | 庆余年第18集 |
|  18  | 庆余年第19集 |
|  19  | 庆余年第20集 |
|  20  | 庆余年第21集 |
|  21  | 庆余年第22集 |
|  22  | 庆余年第23集 |
|  23  | 庆余年第24集 |
|  24  | 庆余年第25集 |
|  25  | 庆余年第26集 |
|  26  | 庆余年第27集 |
|  27  | 庆余年第28集 |
|  28  | 庆余年第29集 |
|  29  | 庆余年第30集 |
|  30  | 庆余年第31集 |
|  31  | 庆余年第32集 |
|  32  | 庆余年第33集 |
|  33  | 庆余年第34集 |
|  34  | 庆余年第35集 |
|  35  | 庆余年第36集 |
|  36  | 庆余年第37集 |
|  37  | 庆余年第38集 |
|  38  | 庆余年第39集 |
|  39  | 庆余年第40集 |
|  40  | 庆余年第41集 |
|  41  | 庆余年第42集 |
|  42  | 庆余年第43集 |
|  43  | 庆余年第44集 |
|  44  | 庆余年第45集 |
|  45  | 庆余年第46集 |
+------+--------------+

请选择下载方式(默认为单集下载)：
1.单集下载    2.多选下载      3.全集下载      4.批量导出m3u8
请输入选择的方式序号：2

当前是多选视频下载：
输入 1-4 会下载第1到第4个视频，如有多个区间则用逗号(逗号应为英文逗号)分开 如 1-3, 5-8
请输入要下载的多选视频序号：1-3
0 - 低清，1 - 流畅， 2 - 高清，3 - 超清，4 - 蓝光，5 - 4K
如果选择的分辨率没有，默认下载最高清的资源
请选择要下载的视频清晰度:5
+------+-------------+--------+----------+-----------+--------+
| 序号 |     片名    | 清晰度 | 视频格式 |   分辨率  |  大小  |
+------+-------------+--------+----------+-----------+--------+
|  0   | 庆余年第2集 |   4K   |   H265   | 3840x2160 | 1142MB |
|  1   | 庆余年第3集 |   4K   |   H265   | 3840x2160 | 973MB  |
|  2   | 庆余年第4集 |   4K   |   H265   | 3840x2160 | 946MB  |
+------+-------------+--------+----------+-----------+--------+
请选择是否导出m3u8文件到export.txt(1-表示导出，2-表示不导出，默认不导出):1
m3u8文件已经导入到export.txt
下载第1/3个文件：
./Downloads/庆余年第2集_4K_format_H265
庆余年第2集_4K_format_H265 00:45:52
  process:[39/311] [111.58MB/889.79MB] 12.54% speed:2.69MB/s eta:00:04:49
```
