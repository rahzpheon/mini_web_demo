import time
import os
import re

# 模板路径
template_root = './templates'


def index(file_name):
    '''返回index.py需要的页面内容'''

    # 打开模板,读取模板内容,并用动态内容替换 模板变量 最后将其作为响应体返回
    try:
        file_name = file_name.replace('.py', '.html')  # 为什么要加.？避免文件名内可能的py字符被替换
        f = open(template_root + file_name)  # 打开模板

    except Exception as ret:
        return '%s' % ret  # 作为响应体

    else:
        content = f.read()
        f.close()

        # 用动态内容(比如读取数据库得到的数据)替换 模板变量
        data_from_mysql = '数据准备中...'
        content = re.sub(r'\{%content%\}', data_from_mysql, content)

        return content


def center(file_name):
    '''返回center.py需要的页面内容'''
    try:
        file_name = file_name.replace('.py', '.html')  # 为什么要加.？避免文件名内可能的py字符被替换
        f = open(template_root + file_name)

    except Exception as ret:
        return '%s' % ret  # 作为响应体

    else:
        content = f.read()
        f.close()

        data_from_mysql = "暂时没有数据,,,,~~~~(>_<)~~~~ "
        content = re.sub(r"\{%content%\}", data_from_mysql, content)

        return content


def wsgi_api(environ, start_response):

    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)

    # 根据environ:客户端发来的请求,作不同处理(返回不同的响应体)
    file_name = environ['PATH_INFO']
    print('888888888888888888888888888888888888888888888', file_name)

    if file_name == '/index.py':
        return index(file_name)

    elif file_name == '/center.py':
        return center(file_name)

    else:
        return 'This is a dynamic web site. %s' % (time.ctime())