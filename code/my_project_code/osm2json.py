# -*- coding:utf-8 -*-
'''
把osm文件经过清洗，按照一定格式整理成json格式，写入adelaide_sample.json文件。
json文件格式如下:
[
    {
    "id": "12345",
    "catogory": "node",
    "addr":{
    "building": shop,
    ...
         }
    },
    {
    "id": "238978",
    "catogory": "way",
    "addr":{
    "amendity": hospital,
    ...
    },
    ...

]
'''
import json
import re
import xml.etree.cElementTree as ET
from collections import defaultdict
import auditosm

OSMFILE = "adelaide_sample.osm"
JSONFILE = "adelaide_sample.json"
CREATED = ["version", "changeset", "timestamp", "user", "uid"]
LOWER = re.compile(r'^[a-z0-9_]*$')
LOWER_COLON = re.compile(r'^[a-z_]*:[a-z_]*')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
UPPER = re.compile(r'[A-Z]*')


def shape_created(doc, element):
    '''
    Arguments:
    doc -- 待修改的记录，函数会给doc字典添加created项
    element -- xml的一个节点元素
    
    '''
    doc["created"] = {}
    for item in CREATED:
        if item in element.attrib:
            doc["created"][item] = element.attrib[item]

def shape_regular(doc, element, key1, key2):
    '''
    如果key2属性存在，就建立映射 key1:element.attrib[key2]
    '''
    if key2 in element.attrib:
        doc[key1] = element.attrib[key2]
          
def shape_pos(doc, element):
    '''
    添加位置position
    '''
    if "lat" in element.attrib and "lon" in element.attrib:
        lat, lon = element.attrib["lat"], element.attrib["lon"]
        try:
            if float(lat) > -40 and float(lat) < -30 and float(lon) > 136 and float(lon) < 140:
                doc["postion"] = [float(element.attrib["lat"]), float(element.attrib["lon"])] 
            else:
                print "Postion value exceeds right range! latitude is {0}, longitude is {1}".format(lat, lon)
        except ValueError:
            print "Format wrong! Latitude or longtitude is not number!"
            print "latitude is {0}, longitude is {1}".format(lat, lon)
        finally:
            return None
               
def shape_node(doc, element):
    '''
    1. 处理tag标签
    2. 清洗phone数据
    3. 清洗postcode数据
    '''
    mapping = {"acma.gov.au": "acma",
     "building.source": "building_source", 
     "underconstruction?": "is_underconstruction"} #修改一些有问题的字段名称
    for tag in element.iter("tag"):
        key = tag.attrib["k"]
        value = tag.attrib["v"]

        if UPPER.match(key): #如果有大写的，先转换为小写
            key = key.lower()

        for item in mapping:
            if item in key:
                key = key.replace(item, mapping[item])
        
        if LOWER.match(key):
            if key == "phone":
                value = auditosm.audit_phone(value) #审查并整理phone的格式
            if key == "postal_code":       #审查postal_code数据，并把postal_code统一成postcode
                key = "postcode"
                value = auditosm.audit_postcode(value)
            if value != None:
                doc[key] = value


        elif LOWER_COLON.match(key):
            if key == "addr:postcode":
                value = auditosm.audit_postcode(value) #审查并整理postcode格式
            if key == "addr:street":
                value = auditosm.audit_street(value) #审查并整理street格式

            flist = key.split(":") #addr:building --> "addr":{"building": "aaa"}
            field = flist[0]
            

            subfield = "_".join(flist[1:])  #只划分到第一个冒号
            if type(doc[field])!=type({}): #如果field字段和之前的没有冒号的lower型字段重复，给当前field字段末尾加上"_"，避免字段重复。
                field = field+'_'
            assert type(doc[field])==type({}) #确保当前field不会与已有字段重复

            doc[field][subfield] = value 
               
        elif PROBLEMCHARS.match(key):
            print "problem key：%s，value:%s", (key, value)
            
            
        else: #一些特殊情况的处理
            print "Other key：{0}，value:{1}, tag name:{2}".format(key, value, element.tag) 

                
            
            
    

def shape_way(doc, element):
    '''
    添加node_refs字段
    '''
    node_refs = []
    [node_refs.append(nd.attrib['ref']) for nd in element.iter("nd")]
    if node_refs != []:
        doc["node_refs"] = node_refs

def shape_relation(doc, element):
    '''
    增加member字段
    '''
    mblist =[]
    for member in element.iter('member'):
        d = member.attrib
        for key, value in d.items():
            if value == "":
                d.pop(key)
        mblist.append(d)

    if mblist != []:
        doc["member"] = mblist
        



def shape_element(element):
    '''
    处理每个element，把xml变成字典列表
    '''
    if element.tag not in ["node", "way", "relation"]:
        return None
    
    doc = defaultdict(dict)
    shape_created(doc, element) #整理created字段
    shape_regular(doc, element, "id", "id") # 整理id字段
    shape_regular(doc, element, "visible", "visible") #整理visible字段
    shape_pos(doc, element) #整理postion字段
    doc["category"] = element.tag #整理
    
    shape_node(doc, element)
    if element.tag == "way":
        shape_way(doc, element)
    else:
        shape_relation(doc, element)
    return doc


def process_map(file_in, pretty=True):
    '''
    将xml转化成json格式，写入文件
    '''
    data = []
    file_out = open(JSONFILE, 'wb')
    file_out.write('[\n')
    count = 0
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            count += 1
            data.append(el)
            prefix = ('' if count==1 else ',') 
            if pretty:
                file_out.write(prefix+json.dumps(el, indent=2))
            else:
                file_out.write(prefix+json.dumps(el))
        
    file_out.write(']')
    file_out.close()
    return data
    



if __name__ == "__main__":
    process_map(OSMFILE)