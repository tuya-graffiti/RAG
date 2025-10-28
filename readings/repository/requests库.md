# requests

Python requests 是一个常用的 HTTP 请求库，可以方便地向网站发送 HTTP 请求，并获取响应结果。

requests 模块比 [urllib](https://www.runoob.com/python3/python-urllib.html) 模块更简洁。

使用 requests 发送 HTTP 请求需要先导入 requests 模块：

~~~
import requests
~~~

导入后就可以发送 HTTP 请求，使用 requests 提供的方法向指定 URL 发送 HTTP 请求，例如：

~~~
# 导入 requests 包
import requests

# 发送请求
x = requests.get('https://www.runoob.com/')

# 返回网页内容
print(x.text)
~~~

每次调用 requests 请求之后，会返回一个 response 对象，该对象包含了具体的响应信息，如状态码、响应头、响应内容等：

~~~
print(response.status_code)  # 获取响应状态码
print(response.headers)  # 获取响应头
print(response.content)  # 获取响应内容
~~~

