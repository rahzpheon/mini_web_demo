import time
import os
import re
import pymysql

# 模板路径
template_root = './template'

g_url_route = dict()

# 装饰器工厂:路由功能-用参数为路径绑定指定功能
def route(url):
    def func1(func):
        g_url_route[url] = func
        def func2(file_name):

            print(g_url_route)

            return func(file_name)
        return func2
    return func1

# 路由装饰器工厂: 为路径/index.html 绑定功能index(file_name)
# 伪静态:静态请求.html实际动态执行这里的函数
@route('/index.html')  # 等于执行index = route('/index.py')(index)
def index(file_name):
    '''返回index.py需要的页面内容'''

    # 打开模板,读取模板内容,并用动态内容替换 模板变量 最后将其作为响应体返回
    with open(template_root + file_name) as f:
        # file_name = file_name.replace('.py', '.html')  # 为什么要加.？避免文件名内可能的py字符被替换 实现伪静态后本局无效
        content = f.read()

        # 用动态内容(比如读取数据库得到的数据)替换 模板变量
        # 获取数据库内容
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='201011621111', database='stock_db', charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select * from info;')
        data_set = cursor.fetchall()
        data = ''  # 存储替换后的模板
        for line in data_set:
            # 对于每一条数据,加上响应的格式,让网页能够识别.要记得数据是元祖格式,bytes类型的。
            data_line = '''<tr>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td><input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="000007"></td>
                              </tr>'''  % line  # fetch返回的是((查询结果1), (查询结果2), ...)
            data += data_line
        conn.commit()
    except Exception as e:
        print('操作失败...', str(e))
        conn.rollback()
        pass
    else:
        # 用打好了格式的数据替换模板内容
        content = re.sub(r'\{%content%\}', data, content)
    finally:
        cursor.close()
        conn.close()
        print('完成.')

    # data_from_mysql = '数据准备中...'
    # content = re.sub(r'\{%content%\}', data_from_mysql, content)

    return content

@route('/center.html')
def center(file_name):
    '''返回center.py需要的页面内容'''
    # 这里使用try结构,在打不开页面时可以作处理
    # 打开模板并读取
    try:
        f = open(template_root + file_name)

    except Exception as ret:
        return '%s' % ret  # 作为响应体

    else:
        content = f.read()
        f.close()

    # 同上:从db获取动态数据 替换模板变量, 其中要为数据打上一定的格式.
    try:
        sql = 'select i.id, i.short, i.chg, i.turnover, i.price, i.highs, f.note_info from info i join focus f on i.id = f.info_id;'
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='201011621111', database='stock_db', charset='utf8')
        cursor = conn.cursor()
        cursor.execute(sql)
        data_set = cursor.fetchall()
        data = ''
        for line in data_set:
            # 为每条数据添加格式
            format_line = '''<tr>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td><a type="button" class="btn btn-default btn-xs" href="/update/300268.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a></td>
                            <td> <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="300268"></td>
                          </tr>''' % line
            data += format_line
        conn.commit()
    except Exception as e:
        print('操作失败...', str(e))
        conn.rollback()
    else:
        content = re.sub(r"\{%content%\}", data, content)
    finally:
        cursor.close()
        conn.close()
        print('完成.')
    return content


def wsgi_api(environ, start_response):

    print(g_url_route)

    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)

    # 根据environ:客户端发来的请求,作不同处理(返回不同的响应体)
    file_name = environ['PATH_INFO']
    print('888888888888888888888888888888888888888888888', file_name)

    try:
        print('请求的文件:', file_name)
        return g_url_route[file_name](file_name)
    except Exception as ret:
        return '%s' % ret