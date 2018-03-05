import time
import os
import re
import pymysql
import urllib.parse

# 模板路径
template_root = './template'

g_url_route = list()


# 装饰器工厂:路由功能-用参数为路径绑定指定功能
def route(url):
    def func1(func):
        g_url_route.append((url, func))

        def func2(file_name):
            return func(file_name)
        return func2
    return func1


# 路由装饰器工厂: 为路径/index.html 绑定功能index(file_name)
# 伪静态:静态请求.html实际动态执行这里的函数
@route(r'/index.html')  # 等于执行index = route('/index.py')(index)
def index(file_name, url=None):
    '''返回index.py需要的页面内容'''

    print('index运行')

    # 打开模板,读取模板内容,并用动态内容替换 模板变量 最后将其作为响应体返回
    with open(template_root + file_name) as f:
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
                                <td><input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s"></td>
                              </tr>'''  % (*line, line[1])  # fetch返回的是((查询结果1), (查询结果2), ...)
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

    return content

@route(r'/center.html')
def center(file_name, url=None):
    '''返回center.py需要的页面内容'''
    print('center运行')
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
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='201011621111', database='stock_db', charset='utf8')
        cursor = conn.cursor()
        sql = """select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info
                  from focus f join info i
                  on f.info_id = i.id;"""
        cursor.execute(sql)
        data_set = cursor.fetchall()
        data = ''
        for line in data_set:
            # 为每条数据添加格式
            format_line = """<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td><a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a></td>
                <td> <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s"></td>
                </tr>
            """ % (line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[0],line[0])
            data += format_line
        conn.commit()
    except Exception as e:
        conn.rollback()
        return '操作失败' + str(e)
    else:
        content = re.sub(r"\{%content%\}", data, content)
        return content
    finally:
        cursor.close()
        conn.close()



@route(r'/add/(\d*)\.html')
def add(file_name, url):
    # 注意,该功能不需要打开模板,只返回一条信息
    # 从url中获取要操作的股票代码
    ret = re.match(url, file_name)
    stock_code = ret.group(1)

    # 进行sql语句操作,先判断是否存在,存在时添加,不存在时返回
    try:
        conn = pymysql.connect(host='localhost', port=3306, database='stock_db', user='root', password='201011621111', charset='utf8')
        cursor = conn.cursor()
        # 判断是否已经关注
        sql = '''select * from focus inner join info on focus.info_id=info.id where info.code=%s;'''
        count = cursor.execute(sql, [stock_code])
        if count > 0:
            return '该股票已经关注.'

        # 增加关注
        sql = '''insert into focus(info_id) (select info.id from info where info.code=%s);'''
        cursor.execute(sql, [stock_code])
        conn.commit()

    except Exception as e:
        conn.rollback()
        return '添加失败.' + str(e)  # 要知道什么时候用户需要网页,什么时候之返回一个字符串

    else:
        return '添加成功.'

    finally:
        cursor.close()
        conn.close()
        print('完毕.')

@route(r'/del/(\d+)\.html')
def delete(file_name, url):
    '''删除操作'''

    # 从地址中截取要删除的股票代码
    ret = re.match(url, file_name)
    stock_code = ret.group(1)

    # 进行数据库删除操作
    try:
        conn = pymysql.connect(host='localhost',
                               port=3306,
                               database='stock_db',
                               user='root',
                               password='201011621111',
                               charset='utf8')
        cursor = conn.cursor()
        # 增加关注
        sql = '''delete from focus where focus.info_id = (select info.id from info where info.code=%s);'''
        cursor.execute(sql, [stock_code])
        conn.commit()

    except Exception as e:
        conn.rollback()
        return '删除失败.' + str(e)  # 要知道什么时候用户需要网页,什么时候之返回一个字符串

    else:
        return '删除成功.'

    finally:
        cursor.close()
        conn.close()

@route(r'^/update/(\d*)\.html$')
def update(file_name, url):
    '''显示更新页面'''
    # 打开更新模板
    with open(template_root + '/update.html') as f:
        content = f.read()

    ret = re.match(url, file_name)

    # if ret:   # 在app中已经判断过一次
    stock_code = ret.group(1)

    # 通过分析模板代码,可知数据为{%code%}与{%note_info%}
    # 本方法是在模板中显示数据,更改功能应在另外的请求路径下
    try:
        conn = pymysql.connect(host='localhost',
                               port=3306,
                               database='stock_db',
                               user='root',
                               password='201011621111',
                               charset='utf8')
        cursor = conn.cursor()
        # 获取备注信息
        sql = '''select note_info from focus f join info i on i.id=f.info_id where i.code=%s;'''
        cursor.execute(sql, [stock_code])
        note_info = cursor.fetchone()[0]
        conn.commit()

        content = re.sub(r'{%code%}', stock_code, content)

    except Exception as e:

        content = re.sub(r'\{%note_info%\}', '获取信息失败', content)

    else:
        content = re.sub(r'\{%note_info%\}', note_info, content)

    finally:
        cursor.close()
        conn.close()

    return content

@route(r'^/update/(\d+)/(\S+)\.html$')
def update_note_info(file_name, url):

    # 获取要操作的代码与备注信息 重要:url中的汉字要进行编码!!
    ret = re.match(url, file_name)
    stock_code = ret.group(1)
    note_info = ret.group(2)
    note_info = urllib.parse.unquote(note_info)

    try:
        conn = pymysql.connect(host='localhost', port=3306, database='stock_db', user='root', password='201011621111',
                               charset='utf8')
        cursor = conn.cursor()
        sql = '''update focus f join info i
                  on f.info_id=i.id
                  set note_info=%s
                  where i.code = %s'''
        cursor.execute(sql, [note_info, stock_code])
        conn.commit()

    except Exception as e:
        conn.rollback()
        return '修改失败' + str(e)

    else:
        return '修改成功'
    finally:
        cursor.close()
        conn.close()

def wsgi_api(environ, start_response):

    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)

    # 根据environ:客户端发来的请求,作不同处理(返回不同的响应体)
    file_name = environ['PATH_INFO']

    try:
        for url, call_func in g_url_route:
            ret = re.match(url, file_name)
            if ret:
                print('匹配成功')
                return call_func(file_name, url)
        else:
            return '访问页面不存在---%s' % file_name

    except Exception as ret:
        return '%s' % ret

    else:
        return str(environ) + '---404---\n'