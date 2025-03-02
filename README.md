# gpx_converter
## 简介
在网站或地图软件中导出gpx文件时，如果地图文件为 __中国国内数据__ 。则会采用gcj02坐标系。而谷歌地图等国际地图软件一般采用wgs84坐标，这就导致了文件在国内外不同地图软件上显示时产生偏差。本仓库使用python编写了一份简易的转换脚本，便于gpx文件在各种坐标系之间的转换。
## 用法
克隆仓库后，在仓库目录中执行
```
python main.py [源文件路径] [源文件坐标系] [目标坐标系] -o [转换结果文件路径] 
```
> 注命令中的坐标系代号统一为小写字符

__支持的坐标系__

 1. wgs84
 2. gcj02
 3. bd09
