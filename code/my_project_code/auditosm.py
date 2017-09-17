# -*- coding:utf-8 -*-
import json
import re
import pprint

def audit_postcode(postcode):
	'''
    根据查询结果，不一致的情况是“SA 5608”。 如果后四位是数字，返回后四位。
    '''
	return postcode[-4:] if re.match(r'[\d]{4}$', postcode) else None

def audit_phone(phone):
    num_patt = re.compile('[\d]{1}')
    num_lst = num_patt.findall(phone)
    if len(num_lst) == 11:
        country_num = ''.join(num_lst[0:2])
        return "+" + country_num + ' '+ ''.join(num_lst[2:]) if country_num == '61' else None

    elif len(num_lst) == 10:
        district_num = ''.join(num_lst[0:2])
        return district_num + ' ' + ''.join(num_lst[2:]) if district_num  in ['02', '03', '04', '07', '08'] else None
        
    elif len(num_lst) == 9:
        return "+61" + ''.join(num_lst[:])
    else:
        return None

def audit_street(street):
    '''
    根据mapping结果， 返回规范的街道表示
    '''
    mapping = {
    "Rd": "Road",
    "Strert": "Street",
    "Street23": "Street"
    }
    [street.replace(item, mapping[item]) for item in mapping if item == street.split()[-1]]
    return street	
