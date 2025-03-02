import math
import xml.etree.ElementTree as ET
from copy import deepcopy

# 注册GPX命名空间
ET.register_namespace('', 'http://www.topografix.com/GPX/1/1')

# ----------------------
# 坐标系转换核心算法
# ----------------------
def bd09_to_gcj02(lng, lat):
    """百度坐标系 -> 火星坐标系"""
    x = lng - 0.0065
    y = lat - 0.006
    z = math.sqrt(x*x + y*y) - 0.00002*math.sin(y*math.pi)
    theta = math.atan2(y, x) - 0.000003*math.cos(x*math.pi)
    return z*math.cos(theta), z*math.sin(theta)

def gcj02_to_bd09(lng, lat):
    """火星坐标系 -> 百度坐标系"""
    z = math.sqrt(lng*lng + lat*lat) + 0.00002*math.sin(lat*math.pi)
    theta = math.atan2(lat, lng) + 0.000003*math.cos(lng*math.pi)
    return z*math.cos(theta) + 0.0065, z*math.sin(theta) + 0.006

def gcj02_to_wgs84(lng, lat):
    """火星坐标系 -> WGS84坐标系"""
    a = 6378245.0
    ee = 0.00669342162296594323

    def _transform_lat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transform_lng(lng, lat):
        ret = lng + 300.0 + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * math.pi) + 40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
        return ret



    def _transform(lng, lat):
        dlat = _transform_lat(lng - 105.0, lat - 35.0)
        dlng = _transform_lng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * math.pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
        return dlng, dlat

    dlng, dlat = _transform(lng, lat)
    return lng*2 - (lng + dlng), lat*2 - (lat + dlat)

def wgs84_to_gcj02(lng, lat):
    """WGS84坐标系 -> 火星坐标系"""
    a = 6378245.0
    ee = 0.00669342162296594323
    def _transform_lat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transform_lng(lng, lat):
        ret = lng + 300.0 + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * math.pi) + 40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    def _transform(lng, lat):
        dlat = _transform_lat(lng - 105.0, lat - 35.0)
        dlng = _transform_lng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * math.pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
        return dlng, dlat

    if not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271):
        return lng, lat

    dlng, dlat = _transform(lng, lat)
    return lng + dlng, lat + dlat

# ----------------------
# 转换路由配置
# ----------------------
CONVERSION_CHAINS = {
    # 简单转换
    ('bd09', 'gcj02'): [bd09_to_gcj02],
    ('gcj02', 'bd09'): [gcj02_to_bd09],
    ('gcj02', 'wgs84'): [gcj02_to_wgs84],
    ('wgs84', 'gcj02'): [wgs84_to_gcj02],
    
    # 复合转换
    ('bd09', 'wgs84'): [bd09_to_gcj02, gcj02_to_wgs84],
    ('wgs84', 'bd09'): [wgs84_to_gcj02, gcj02_to_bd09],
    
    # 空转换
    ('bd09', 'bd09'): [],
    ('gcj02', 'gcj02'): [],
    ('wgs84', 'wgs84'): []
}

# ----------------------
# 文件处理模块
# ----------------------
def convert_gpx(input_file, output_file, src_cs, dst_cs):
    """执行GPX文件转换
    
    :param input_file: 输入文件名
    :param output_file: 输出文件名
    :param src_cs: 源坐标系 (bd09/gcj02/wgs84)
    :param dst_cs: 目标坐标系 (bd09/gcj02/wgs84)
    """
    # 验证坐标系有效性
    if src_cs not in ['bd09', 'gcj02', 'wgs84'] or dst_cs not in ['bd09', 'gcj02', 'wgs84']:
        raise ValueError("无效坐标系，可选值: bd09/gcj02/wgs84")

    # 获取转换链
    conversion_chain = CONVERSION_CHAINS.get((src_cs.lower(), dst_cs.lower()))
    if conversion_chain is None:
        raise ValueError(f"不支持的转换方向: {src_cs} -> {dst_cs}")

    try:
        # 读取原始文件
        tree = ET.parse(input_file)
    except ET.ParseError as e:
        raise ValueError(f"无法解析输入文件: {e}")

    root = tree.getroot()
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    # 执行坐标转换
    for trkpt in root.findall('.//gpx:trkpt', ns):
        # 读取原始坐标
        lng = float(trkpt.get('lon'))
        lat = float(trkpt.get('lat'))
        
        # 链式转换
        current_lng, current_lat = lng, lat
        for converter in conversion_chain:
            current_lng, current_lat = converter(current_lng, current_lat)
        
        # 更新坐标值（保留6位小数）
        trkpt.set('lon', f"{current_lng:.6f}")
        trkpt.set('lat', f"{current_lat:.6f}")

    # 写入新文件
    tree.write(output_file,
               encoding='utf-8',
               xml_declaration=True,
               short_empty_elements=False)

# ----------------------
# 用户交互模块
# ----------------------
if __name__ == '__main__':
    import argparse

    # 配置命令行参数
    parser = argparse.ArgumentParser(description='GPX坐标系转换工具')
    parser.add_argument('input', help='输入GPX文件路径')
    parser.add_argument('src', choices=['bd09', 'gcj02', 'wgs84'], 
                       help='源坐标系类型')
    parser.add_argument('dst', choices=['bd09', 'gcj02', 'wgs84'], 
                       help='目标坐标系类型')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')

    # 解析参数
    args = parser.parse_args()
    
    # 生成输出文件名
    output_path = args.output or \
        f"{args.input.rsplit('.', 1)[0]}_{args.dst}.gpx"

    # 执行转换
    try:
        convert_gpx(args.input, output_path, args.src, args.dst)
        print(f"转换成功！输出文件: {output_path}")
    except Exception as e:
        print(f"转换失败: {str(e)}")