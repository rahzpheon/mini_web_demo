#! /usr/bin/python3

import socket
import multiprocessing
import re
import os
import sys
import time


class WSGIServer(object):

    # 服务器初始化
    def __init__(self,port, documents_root, app):

        # 初始化服务器套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', port))
        server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server_socket.listen()
        self.server_socket = server_socket

        # 设定文件资源路径
        self.documents_root = documents_root

        # 设定web框架可以调用的函数(对象)
        self.app = app

    # 运行服务器
    def run_server_forever(self):

        print('server is running')

        # 永久运行,接受客户端请求并建立子进程处理
        while True:

            client_socket, client_addr = self.server_socket.accept()
            print('来自', client_addr, '的连接请求')
            client_socket.settimeout(3)  # 阻塞等待3秒  ？？
            pro = multiprocessing.Process(target=self.handle_client, args=(client_socket, ))
            pro.start()

            # 因为子进程会自己复制一份,关闭主进程中的套接字
            client_socket.close()

    # 处理单个客户端请求
    def handle_client(self, client_socket):

        # 使用长连接
        while True:
            request_data = client_socket.recv(4096).decode('utf-8')

            # 如果客户端关闭连接
            if not request_data:
                print('连接已关闭')
                client_socket.close()

            # 使用正则表达式获取客户请求内容
            request_lines = request_data.splitlines()
            request_line = request_lines[0]
            ret = re.match(r'([^/]*)(/[^ ]*)', request_line)
            # 正则匹配成功
            if not ret:
                print('获取用户请求失败')
                client_socket.close()

            file_name = ret.group(2)

            # 当请求根目录时,返回指定主页
            if file_name == '/':
                file_name = self.documents_root + '/index.html'
            # else:
            #     file_name = self.documents_root + file_name

            # 如果客户端请求的是静态内容，返回指定的静态页面或处理错误
            if not file_name.endswith('.py'):

                if not os.path.exists(file_name):

                    response_header = 'HTTP/1.1 404 NoT FoUnD\r\n'
                    response_header += '\r\n'
                    response_body = 'Your request is InVaIlD.>'

                else:
                    with open(file_name, 'rb') as f:
                        content = f.read()

                    response_body = content.decode('utf-8')
                    response_header = 'HTTP/1.1 200 OK\r\n'
                    response_header += '\r\n'

                response_data = (response_header + response_body).encode('utf-8')

                client_socket.send(response_data)

            # 客户端要求的是动态内容
            else:
                env = {}
                env['PATH_INFO'] = file_name

                # app在由用户指定的.py文件中,在服务器初始化时作为参数传进来。
                # 命令行运行服务器时用sys.argv传入.py文件的路径,并且进行操作,提取WSGI接口函数
                # 而set..header是由服务器提供的函数,用于设置HTTP响应头并存于self.header中
                # 在app中会:(0)接受发送过来的请求environ (1)调用set...header (2)(根据environ)生成动态内容并返回
                # 通过这种调用方式,实现了server-app的对接.
                response_body = self.app(env, self.set_respsonse_header)  # 存储web返回的动态数据

                # 编写header并合并
                response_header = 'HTTP/1.1 {status}\r\n'.format(status=self.header[0])  # 关键字赋值
                response_header += 'Content-Type: text/html; charset=utf-8\r\n'
                response_header += 'Content-Length: %d\r\n' % len(response_body)
                for temp_head in self.header[1]:    # 使用format格式化,接收多个参数并用{下标}为字符串赋值
                    response_header += '{0}:{1}\r\n'.format(*temp_head)

                response = response_header + '\r\n'
                response += response_body

                client_socket.send(response.encode('utf-8'))

    # 由服务器负责的HTTP响应函数,会提供给wsgi函数
    def set_respsonse_header(self, status, headers):
        '''该方法在web框架中被默认调用'''
        response_header_default = [
            ('Data', time.ctime()),
            ('Server', 'Mini Web Server Demo')
        ]

        # 将状态码/响应头信息存储起来
        # [字符串, [xxxxx, xxx2]]
        self.header = [status, response_header_default + headers]

g_static_document_root = './static'   # 注意,以本服务器文件所在路径为.
g_dynamic_document_root = './dynamic'


def main():

    # 接受命令行参数运行服务器,格式为python3 xxxx.py port xxx:application
    if len(sys.argv) == 3:
        # 获取服务器port
        port = sys.argv[1]
        if port.isdigit():
            port = int(port)
        else:
            print('非法端口号.')
            return

        # 用户输入负责为web服务器提供动态资源的web框架名字:应用名,随后用正则分割
        web_frame_module_app_name = sys.argv[2]

    else:
        print('运行方式:python3 xxx.py 8080 my_web_frame_name:application')
        return

    # 将动态路径(web框架存放路径)配置至python的import路径中
    sys.path.append(g_dynamic_document_root)

    # 获取web框架名 与 接口函数app的名字,再import该框架(.py文件),从中取出wsgi接口函数app
    # 切记import不能加上.py
    ret = re.match(r'([^:]*):(.*)', web_frame_module_app_name)

    if ret:
        web_frame_module_name = ret.group(1)
        app_name = ret.group(2)

    else:
        print('web框架指定错误...')
        return

    # 重要,导入模块,获取app
    web_frame_module = __import__(web_frame_module_name)
    app = getattr(web_frame_module, app_name)

    # 运行服务器
    my_wsgi = WSGIServer(port, g_static_document_root, app)
    my_wsgi.run_server_forever()

if __name__ == '__main__':
    main()