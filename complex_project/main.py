"""
复杂项目示例 - 包含多种代码问题
"""

import os
import sys
import json
import re
from typing import List, Dict, Any

# 过长的函数
def process_data(data_list):
    """处理数据列表 - 这个函数太长了"""
    results = []
    
    for item in data_list:
        if item['type'] == 'A':
            if item['value'] > 100:
                if item['status'] == 'active':
                    processed = item['value'] * 1.1
                    if processed > 200:
                        processed = processed * 0.9
                    results.append({
                        'id': item['id'],
                        'value': processed,
                        'category': 'high'
                    })
                else:
                    results.append({
                        'id': item['id'],
                        'value': item['value'],
                        'category': 'inactive'
                    })
            else:
                results.append({
                    'id': item['id'],
                    'value': item['value'],
                    'category': 'low'
                })
        elif item['type'] == 'B':
            if item['value'] > 50:
                processed = item['value'] * 1.2
                results.append({
                    'id': item['id'],
                    'value': processed,
                    'category': 'medium'
                })
            else:
                results.append({
                    'id': item['id'],
                    'value': item['value'],
                    'category': 'low'
                })
        elif item['type'] == 'C':
            processed = item['value'] * 0.8
            results.append({
                'id': item['id'],
                'value': processed,
                'category': 'special'
            })
        else:
            results.append({
                'id': item['id'],
                'value': item['value'],
                'category': 'unknown'
            })
    
    return results

# 高圈复杂度
def validate_config(config):
    """验证配置 - 圈复杂度过高"""
    if 'database' in config:
        if config['database']['host']:
            if config['database']['port']:
                if config['database']['username']:
                    if config['database']['password']:
                        if config['database']['database']:
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

# 参数过多
def create_user(name, email, age, phone, address, city, state, zip_code, country):
    """创建用户 - 参数过多"""
    return {
        'name': name,
        'email': email,
        'age': age,
        'phone': phone,
        'address': address,
        'city': city,
        'state': state,
        'zip_code': zip_code,
        'country': country
    }

# 重复代码
def format_price(price):
    """格式化价格"""
    formatted = "${:.2f}".format(price)
    return formatted

def format_discount(discount):
    """格式化折扣"""
    formatted = "${:.2f}".format(discount)
    return formatted

def format_tax(tax):
    """格式化税费"""
    formatted = "${:.2f}".format(tax)
    return formatted

# 过大的类
class DataProcessor:
    """数据处理器 - 类太大"""
    
    def __init__(self):
        self.data = []
        self.config = {}
        self.cache = {}
        self.stats = {}
    
    def load_data(self, file_path):
        """加载数据"""
        with open(file_path, 'r') as f:
            self.data = json.load(f)
    
    def save_data(self, file_path):
        """保存数据"""
        with open(file_path, 'w') as f:
            json.dump(self.data, f)
    
    def process_item(self, item):
        """处理单个项目"""
        return item
    
    def process_all(self):
        """处理所有数据"""
        return [self.process_item(item) for item in self.data]
    
    def filter_data(self, condition):
        """过滤数据"""
        return [item for item in self.data if condition(item)]
    
    def sort_data(self, key):
        """排序数据"""
        return sorted(self.data, key=lambda x: x[key])
    
    def aggregate(self, field):
        """聚合数据"""
        return sum(item[field] for item in self.data)
    
    def statistics(self):
        """统计信息"""
        return {
            'count': len(self.data),
            'sum': self.aggregate('value'),
            'avg': self.aggregate('value') / len(self.data) if self.data else 0
        }
    
    def transform(self, func):
        """转换数据"""
        return [func(item) for item in self.data]
    
    def validate(self):
        """验证数据"""
        return all(isinstance(item, dict) for item in self.data)
    
    def export_csv(self, file_path):
        """导出CSV"""
        pass
    
    def export_json(self, file_path):
        """导出JSON"""
        pass
    
    def import_csv(self, file_path):
        """导入CSV"""
        pass
    
    def import_json(self, file_path):
        """导入JSON"""
        pass
    
    def clear_cache(self):
        """清空缓存"""
        self.cache = {}
    
    def update_stats(self):
        """更新统计"""
        self.stats = self.statistics()
    
    def get_report(self):
        """获取报告"""
        return {
            'data': self.data,
            'stats': self.stats,
            'cache_size': len(self.cache)
        }

# 魔法数字
def calculate_shipping(weight):
    """计算运费 - 包含魔法数字"""
    if weight < 10:
        return 5.99
    elif weight < 50:
        return 12.99
    elif weight < 100:
        return 24.99
    else:
        return weight * 0.35

# 重复的逻辑
def validate_email(email):
    """验证邮箱"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """验证电话"""
    pattern = r'^[0-9]{10,11}$'
    return re.match(pattern, phone) is not None

def validate_zip(zip_code):
    """验证邮编"""
    pattern = r'^[0-9]{5,6}$'
    return re.match(pattern, zip_code) is not None
