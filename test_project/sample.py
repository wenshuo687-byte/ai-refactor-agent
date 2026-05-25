"""
示例Python项目 - 用于演示AI智能重构Agent
"""

def calculate_total(items):
    """计算总价"""
    total = 0
    for item in items:
        if item['type'] == 'food':
            total += item['price'] * 1.1
        elif item['type'] == 'drink':
            total += item['price'] * 1.05
        elif item['type'] == 'dessert':
            total += item['price'] * 1.15
        else:
            total += item['price']
    return total

def process_order(order):
    """处理订单"""
    if order['status'] == 'pending':
        if order['amount'] > 0:
            if order['amount'] < 1000:
                discount = 0.05
            elif order['amount'] < 5000:
                discount = 0.10
            else:
                discount = 0.15
        else:
            discount = 0
    else:
        discount = 0

    final_amount = order['amount'] * (1 - discount)
    return final_amount

def validate_user(user):
    """验证用户"""
    if user['age'] >= 18:
        if user['email']:
            if '@' in user['email']:
                if user['phone']:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

def generate_report(data, format, include_charts, include_summary, include_details):
    """生成报告"""
    report = ""
    if format == "pdf":
        report += "PDF Report\n"
    elif format == "html":
        report += "<html>Report</html>"
    elif format == "csv":
        report += "CSV Report"

    if include_charts:
        report += "Charts included"
    if include_summary:
        report += "Summary included"
    if include_details:
        report += "Details included"

    return report

# 重复代码示例
def format_price(price):
    """格式化价格"""
    formatted = "${:.2f}".format(price)
    return formatted

def format_discount(discount):
    """格式化折扣"""
    formatted = "${:.2f}".format(discount)
    return formatted
