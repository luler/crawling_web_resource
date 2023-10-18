import os
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright
from regex import regex


# 下载文件
def download_file(url, base_dir='download_dir'):
    print('正在下载:' + url)
    try:
        match_obj = regex.match(r'http[s]?:\/\/([^\?]*)', url)
        if not match_obj:
            return
        destination = match_obj.group(1)
        destination = './' + base_dir + '/' + destination.replace(':', '_')
        dir = os.path.dirname(destination)
        if not os.path.exists(dir):
            os.makedirs(dir)
        urllib.request.urlretrieve(url, destination)
        print('下载完成:' + url)
    except urllib.error.HTTPError as e:
        print(f"下载失败: {e}")


files = []


def handle_request(route, request):
    global files
    # print('Intercepted', request.resource_type, 'request:', request.url)
    if request.url not in files and request.resource_type in ['script', 'stylesheet', 'image', ]:
        download_file(request.url)
        files.append(request.url)
    route.continue_()


url = ''
while True:
    url = input('请输入链接：')
    if regex.match(r"http(s)?://[^\s]+", url):
        break
    else:
        print('链接无效，请重新输入！')

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.route("**/*", handle_request)

    page.goto(url)

    page.wait_for_timeout(1000 * 60 * 60 * 24)
