from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import os
import requests
import random
import subprocess
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

url = 'https://www.wangfei.la/'
dic = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
porxiesvalue = [
    {'http':'http://121.232.18.26:9018'},
    {'http':'http://39.45.28.68:8118'},
    {'http':'http://190.168.16.223:8181'},
    {'http':'http://191.168.56.32:2643'},
    {'http':'http://156.14.12.45:6845'}]
#定义列表储存m3u8地址
lst = []
tit = []
# 遍历页面，生成HTML源代码

def htmlf():
    # 用户填写信息处
    lst1 = []
    lst1.append('#slide{1}')
    i = int(input("请输入电影编号："))
    print("注意：并不是所有的路线都可以，需要一个个去试！！！")
    m = int(input("路线请填1,2,3,4："))
    if m>=3:
        k = lst1[0]
        print("如果是电影则首和末都填1")
        p = int(input('请输入首集：'))
        e = int(input("请输入末集:"))
#        print("接下来交给程序请耐心等待！(‘’_‘’)")
        print("如果下载过慢试试其他线路吧")
        # 初始化Selenium浏览器
        browser = webdriver.Chrome()
        browser.minimize_window()
#        browser.quit()
        for j in range(p, e + 1):
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            url = lst[i] + f"-sid-{m}-nid-{j}"+f".html{k}"
            browser.get(url)
            yield browser.page_source
    else:
        print("！！！《如果是电影则初始和末尾都填1》！！！")
        p = int(input('初始页数：'))
        e = int(input("末尾页数:"))
        print("接下来交给程序请耐心等待！(‘’_‘’)")
        print("如果下载过慢试试其他线路吧！！！")
        # 初始化Selenium浏览器
        browser = webdriver.Chrome()
        browser.minimize_window()
#        browser.quit()
        for j in range(p, e + 1):
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            url = lst[i] + f"-sid-{m}-nid-{j}" + ".html"
            browser.get(url)
            yield browser.page_source

# 解析文件并下载资源
def m3u8():
    l = 0
    for html in htmlf():
        obj = re.compile(r'class="btn-grad".*? href="(.*?)"', re.S)
        matches = obj.findall(html)
        for match in matches:
            url = match.split('url=')[1]  # 假设URL是这样构造的
            try:
                response = requests.get(url, stream=True,headers=dic,proxies=random.choice(porxiesvalue))
                content = response.content.decode('utf-8')
                if content.startswith("#EXTM3U"):  # 检查是否为m3u8格式
                    # 处理m3u8文件中的.ts片段
                    for line in content.splitlines():
                        if not line.startswith('#'):
                            ts_url = line.strip()
                            ts_response = requests.get(ts_url,headers=dic,proxies=random.choice(porxiesvalue))
                            with open(f"电影抓取/{l}.ts", mode='wb') as f:
                                f.write(ts_response.content)
                                if l ==0 or l == 10:
                                    x = input("是否中断y/n：")
                                    if x == 'y':
                                        break
                                l += 1
                                time.sleep(2)  # 适当延时，避免请求过于频繁
            except Exception as e:
                print(f"下载过程中发生错误: {e}")
    print('全部下载完成！')


def z(url):
    i = input("请输入你想看的电影名称：")
    # 初始化浏览器
    brower = webdriver.Chrome()
    brower.minimize_window()
    brower.get(url)
#    brower.refresh()

    # 查找搜索框和提交按钮
    url_input = brower.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div/form/div/input')
    go_button = brower.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div/form/div/button[1]")

    # 输入搜索词并点击搜索
    url_input.send_keys(i)
    go_button.click()
#    brower.refresh()
    # 等待加载完成
    time.sleep(3)  # 根据实际情况调整等待时间
#    brower.back()
#    go_button.click()
    # 获取当前URL并发送请求
    current_url = brower.current_url
    response = requests.get(current_url,headers=dic,proxies=random.choice(porxiesvalue))
    brower.quit()
    pattern = re.compile(r'''
        <div\s+class="module-card-item\s+module-item">.*?
        <a\s+[^>]*href="(.*?)".*?>.*?
        <strong>(.*?)</strong>.*?
        </a>''', re.DOTALL | re.VERBOSE)
    matches = pattern.findall(response.text)
    return matches
def x(url):
    matches = z(url = url)
    for match in matches:
        href, title = match
        tit.append(title)
        href = str(href).split('/vod-detail')[1]
        href = url + 'vod-play' + href.split('.html')[0]
        lst.append(href)
        print(f"电影网址: {href}.html, 电影名称: {title} ")
        time.sleep(1)

def get_m3u8_non_comments(url):
    """
    获取m3u8文件中的非注释内容并返回为字符串
    :param url: m3u8文件的URL地址
    :return: 非注释内容组成的字符串（每行以换行符分隔）
    """
    try:
        # 添加必要的请求头，模拟浏览器行为
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Referer': urlparse(url).scheme + '://' + urlparse(url).netloc + '/'
        }

        # 发送GET请求获取m3u8内容
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP状态码

        # 验证是否为有效的m3u8文件
        if not response.text.startswith("#EXTM3U"):
            raise ValueError("URL内容不是有效的m3u8格式")

        # 提取非注释内容
        non_comments = []
        for line in response.text.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                non_comments.append(stripped)

        # 将非注释行连接为字符串
        return '\n'.join(non_comments)

    except requests.exceptions.RequestException as e:
        return f"网络请求失败: {str(e)}"
    except ValueError as e:
        return f"格式错误: {str(e)}"
    except Exception as e:
        return f"处理失败: {str(e)}"


def m3u8_2():
    l = 0
    for html in htmlf():
        obj = re.compile(r'class="btn-grad".*? href="(.*?)"', re.S)
        matches = obj.findall(html)
        for match in matches:
            query_start = match.find('?url=') + len('?url=')
            # 从 '?url=' 之后开始截取，直到 '/index.m3u8' 之前
            # 首先找到 '/index.m3u8' 的位置
            suffix_to_remove = '/index.m3u8'
            suffix_start = match.find(suffix_to_remove)
            # 切割出目标部分
            desired_part = match[query_start:suffix_start]
            url = match.split('url=')[1]  # 假设URL是这样构造的
            result = get_m3u8_non_comments(url)
            try:
                response = requests.get(url, stream=True, headers=dic, proxies=random.choice(porxiesvalue))
                content = response.content.decode('utf-8')
                if content.startswith("#EXTM3U"):  # 检查是否为m3u8格式
                    # 处理m3u8文件中的.ts片段
                    for line in content.splitlines():
                        if not line.startswith('#'):
#                            ts_url = line.strip()
                            urls = str(desired_part) + '/'+result
                            print(urls)
                            ts_response = requests.get(urls, headers=dic, proxies=random.choice(porxiesvalue))
                            with open(f"电影抓取/{l}.ts", mode='wb') as f:
                                f.write(ts_response.content)
                                if l == 0 or l == 10:
                                    x = input("是否中断y/n：")
                                    if x == 'y':
                                        break
                                l += 1
                                time.sleep(2)  # 适当延时，避免请求过于频繁
            except Exception as e:
                print(f"下载过程中发生错误: {e}")
        print('全部下载完成！')


os.makedirs("电影抓取", exist_ok=True)


def m3u8_3(url_1):
    l = 0
    try:
        response = requests.get(url_1, headers=dic, proxies=random.choice(porxiesvalue))
        response.raise_for_status()  # 检查请求是否成功
        content = response.text

        if not content.startswith("#EXTM3U"):
            print("错误：不是有效的M3U8文件！")
            return

        # 提取基础URL（确保以/结尾）
        base_url = url_1.rsplit('/', 1)[0] + '/'  # 例如：https://.../20250608/18744_1621d6c7/

        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # 处理.ts文件的URL
                if line.startswith(('http://', 'https://')):
                    ts_url = line  # 已经是完整URL
                else:
                    ts_url = base_url + line  # 拼接相对路径

                try:
                    ts_response = requests.get(ts_url, headers=dic, proxies=random.choice(porxiesvalue), stream=True)
                    ts_response.raise_for_status()

                    with open(f"电影抓取/{l}.ts", 'wb') as f:
                        for chunk in ts_response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # 每10个片段询问是否继续
                    if l % 10 == 0 and l != 0:
                        x = input("是否中断 (y/n): ")
                        if x.lower() == 'y':
                            break

                    l += 1
                    time.sleep(1)  # 避免请求过快

                except Exception as e:
                    print(f"下载失败 {ts_url}: {e}")
                    continue

    except Exception as e:
        print(f"全局错误: {e}")


def m3u8_4(url_1,tits ):
    output_file = str(tits)+'.mp4'

    l = 0
    ts_files = []  # 用于存储所有下载的TS文件路径

    try:
        # 确保目录存在
        os.makedirs("电影抓取", exist_ok=True)

        # 获取m3u8文件内容
        response = requests.get(url_1, stream=True, headers=dic, proxies=random.choice(porxiesvalue))
        content = response.content.decode('utf-8')

        if not content.startswith("#EXTM3U"):
            print("不是有效的M3U8文件")
            return

        # 获取基础URL（去掉index.m3u8部分）
        base_url = url_1.rsplit('/', 1)[0]

        # 获取所有TS文件链接
        ts_urls = [line.strip() for line in content.splitlines() if not line.startswith('#')]

        for ts_url in ts_urls:
            # 处理TS文件URL
            if ts_url.startswith('http'):
                # 已经是完整URL
                full_url = ts_url
            else:
                # 相对路径，拼接完整URL
                full_url = f"{base_url}/{ts_url}" if not ts_url.startswith(
                    '/') else f"{url_1.split('//')[0]}//{url_1.split('/')[2]}{ts_url}"


            try:
                ts_response = requests.get(full_url, headers=dic, proxies=random.choice(porxiesvalue), timeout=10)
                if ts_response.status_code == 200:
                    ts_path = f"电影抓取/{l}.ts"
                    with open(ts_path, 'wb') as f:
                        f.write(ts_response.content)
                    ts_files.append(ts_path)  # 记录下载的TS文件路径

                    # 每下载10个文件提示
                    if l == 1 or l == 10:
                        x = input(f"已下载{l}个文件，是否继续？(y/n): ")
                        if x.lower() != 'y':
                            break

                    l += 1
                    time.sleep(1)  # 适当延时
                else:
                    print(f"下载失败，状态码: {ts_response.status_code}")
            except Exception as e:
                print(f"下载TS文件出错: {e}")
                continue

        # 合并TS文件
        if ts_files:
            print("开始合并TS文件...")
            with open(output_file, 'wb') as merged:
                for ts_file in ts_files:
                    with open(ts_file, 'rb') as f:
                        merged.write(f.read())
            print(f"合并完成，输出文件: {output_file}")

            # 删除临时TS文件
            print("清理临时TS文件...")
            for ts_file in ts_files:
                try:
                    os.remove(ts_file)
                except Exception as e:
                    print(f"删除文件 {ts_file} 失败: {e}")
            print("清理完成")

    except Exception as e:
        print(f"处理M3U8文件出错: {e}")
        # 出错时也尝试清理已下载的文件
        if 'ts_files' in locals():
            for ts_file in ts_files:
                try:
                    os.remove(ts_file)
                except:
                    pass


def m3u8_5(url_1,tits, max_workers=6, batch_size=10):
    output_file = str(tits) + ".mp4"
    """
    优化后的M3U8下载合并函数

    参数:
    - url_1: m3u8文件URL
    - output_file: 输出文件名
    - max_workers: 并发下载线程数
    - batch_size: 每下载多少个文件提示一次
    """
    ts_files = []  # 用于存储所有下载的TS文件路径
    downloaded_count = 0  # 已下载文件计数

    try:
        # 确保目录存在
        os.makedirs("电影抓取", exist_ok=True)

        # 获取m3u8文件内容
        response = requests.get(url_1, stream=True, headers=dic, proxies=random.choice(porxiesvalue))
        response.raise_for_status()  # 如果请求失败抛出异常
        content = response.content.decode('utf-8')

        if not content.startswith("#EXTM3U"):
            print("不是有效的M3U8文件")
            return

        # 获取基础URL（去掉index.m3u8部分）
        base_url = url_1.rsplit('/', 1)[0]

        # 获取所有TS文件链接
        ts_urls = [line.strip() for line in content.splitlines() if not line.startswith('#')]
        if not ts_urls:
            print("没有找到TS文件链接")
            return

        # 下载单个TS文件的函数
        def download_ts(ts_url, index):
            nonlocal downloaded_count
            try:
                # 处理TS文件URL
                if ts_url.startswith('http'):
                    full_url = ts_url
                else:
                    full_url = f"{base_url}/{ts_url}" if not ts_url.startswith(
                        '/') else f"{url_1.split('//')[0]}//{url_1.split('/')[2]}{ts_url}"

                ts_response = requests.get(full_url, headers=dic, proxies=random.choice(porxiesvalue), timeout=10)
                ts_response.raise_for_status()

                ts_path = f"电影抓取/{index}.ts"
                with open(ts_path, 'wb') as f:
                    f.write(ts_response.content)

                return ts_path
            except Exception as e:
                print(f"下载TS文件 {ts_url} 出错: {e}")
                return None

        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(download_ts, ts_url, i): i for i, ts_url in enumerate(ts_urls)}

            for future in as_completed(futures):
                ts_path = future.result()
                if ts_path:
                    ts_files.append(ts_path)
                    downloaded_count += 1

                    # 每下载batch_size个文件提示
                    if downloaded_count  == 10:
                        x = input(f"已下载{downloaded_count}个文件，是否继续？(y/n): ")
                        if x.lower() != 'y':
                            executor.shutdown(wait=False, cancel_futures=True)
                            break

        # 合并TS文件
        if ts_files:
            print(f"开始合并{len(ts_files)}个TS文件...")
            # 按数字顺序排序文件
            ts_files.sort(key=lambda x: int(x.split('/')[-1].split('.')[0]))

            with open(output_file, 'wb') as merged:
                for ts_file in ts_files:
                    try:
                        with open(ts_file, 'rb') as f:
                            merged.write(f.read())
                    except Exception as e:
                        print(f"合并文件 {ts_file} 时出错: {e}")
                        continue

            print(f"合并完成，输出文件: {output_file}")

            # 删除临时TS文件
            print("清理临时TS文件...")
            for ts_file in ts_files:
                try:
                    os.remove(ts_file)
                except Exception as e:
                    print(f"删除文件 {ts_file} 失败: {e}")
            print("清理完成")

    except Exception as e:
        print(f"处理M3U8文件出错: {e}")
        # 出错时也尝试清理已下载的文件
        if 'ts_files' in locals():
            for ts_file in ts_files:
                try:
                    os.remove(ts_file)
                except:
                    pass

def m3u8_6(url_1,tits , max_workers=8, batch_size=10):
    output_file = str(tits) + ".MP4"
    ts_files = []  # 用于存储所有下载的TS文件路径
    downloaded_count = 0  # 已下载文件计数
    temp_dir = "电影抓取"  # 临时目录名称

    try:
        # 确保目录存在
        os.makedirs(temp_dir, exist_ok=True)

        # 获取m3u8文件内容
        response = requests.get(url_1, stream=True, headers=dic, proxies=random.choice(porxiesvalue))
        response.raise_for_status()
        content = response.content.decode('utf-8')

        if not content.startswith("#EXTM3U"):
            print("不是有效的M3U8文件")
            return

        # 获取基础URL（去掉index.m3u8部分）
        base_url = url_1.rsplit('/', 1)[0]

        # 获取所有TS文件链接
        ts_urls = [line.strip() for line in content.splitlines() if not line.startswith('#')]
        if not ts_urls:
            print("没有找到TS文件链接")
            return

        # 下载单个TS文件的函数（优化版）
        def download_ts(ts_url, index):
            nonlocal downloaded_count
            try:
                # 处理TS文件URL
                if ts_url.startswith('http'):
                    full_url = ts_url
                else:
                    full_url = f"{base_url}/{ts_url}" if not ts_url.startswith(
                        '/') else f"{url_1.split('//')[0]}//{url_1.split('/')[2]}{ts_url}"

                ts_response = requests.get(full_url, headers=dic, proxies=random.choice(porxiesvalue), timeout=20)
                ts_response.raise_for_status()

                ts_path = f"{temp_dir}/{index:05d}.ts"  # 使用5位数字填充，便于排序
                with open(ts_path, 'wb') as f:
                    f.write(ts_response.content)

                # 检查文件完整性
                if os.path.getsize(ts_path) < 1024:  # 假设每个TS文件至少1KB
                    print(f"警告: {ts_path} 文件大小异常小")
                    os.remove(ts_path)
                    return None

                return ts_path
            except Exception as e:
                print(f"下载TS文件 {ts_url} 出错: {e}")
                return None

        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(download_ts, ts_url, i): i for i, ts_url in enumerate(ts_urls)}

            for future in as_completed(futures):
                ts_path = future.result()
                if ts_path:
                    ts_files.append(ts_path)
                    downloaded_count += 1

                    # 每下载10个文件提示一次
                    if downloaded_count == 10:
                        print(f"已下载{downloaded_count}/{len(ts_urls)}个文件")
                        x = input("是否继续？(y/n): ")
                        if x.lower() != 'y':
                            executor.shutdown(wait=False, cancel_futures=True)
                            break

        # 合并TS文件（使用FFmpeg优化）
        if ts_files:
            print(f"开始合并{len(ts_files)}个TS文件...")

            # 按数字顺序排序文件
            ts_files.sort(key=lambda x: int(os.path.basename(x).split('.')[0]))

            # 生成文件列表
            file_list_path = f"{temp_dir}/file_list.txt"
            with open(file_list_path, "w", encoding='utf-8') as f:
                for ts_file in ts_files:
                    f.write(f"file '{os.path.abspath(ts_file)}'\n")

            # 使用FFmpeg合并
            try:
                subprocess.run([
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", file_list_path,
                    "-c", "copy",
                    "-movflags", "faststart",  # 优化网络播放
                    output_file
                ], check=True)
                print(f"合并完成，输出文件: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg合并失败: {e}")
                # 尝试传统合并方式作为后备
                print("尝试传统方式合并...")
                with open(output_file, 'wb') as merged:
                    for ts_file in ts_files:
                        try:
                            with open(ts_file, 'rb') as f:
                                merged.write(f.read())
                        except Exception as e:
                            print(f"合并文件 {ts_file} 时出错: {e}")
                            continue
                print(f"传统方式合并完成，输出文件: {output_file}")

            # 删除临时文件
            print("清理临时文件...")
            for ts_file in ts_files:
                try:
                    os.remove(ts_file)
                except Exception as e:
                    print(f"删除文件 {ts_file} 失败: {e}")
            try:
                os.remove(file_list_path)
            except:
                pass
            print("清理完成")

    except Exception as e:
        print(f"处理M3U8文件出错: {e}")
        # 出错时也尝试清理已下载的文件
        if 'ts_files' in locals():
            for ts_file in ts_files:
                try:
                    os.remove(ts_file)
                except:
                    pass
            try:
                os.remove(f"{temp_dir}/file_list.txt")
            except:
                pass
def pd():
    j = 0
    for i in tit:
        print('电影名称：',i,' 编号：',j)
        j+=1

def paixu():
    print("1，2测试；3，4稳定；5，6高速")
    f = input("输入使用爬取的方案/有（1，2，3,4,5，6）：")
    if f =="2":
        pd()
        m3u8_2()
    elif f == "3":
        pd()
        urls = str(input('输入m3u8文件地址：'))
        m3u8_3(url_1=urls)
    elif f =="4":
        pd()
        urls = str(input('输入m3u8文件地址：'))
        tit = str(input("视频名称："))
        m3u8_5(url_1=urls, tits=tit)
    elif f =="5":
        pd()
        urls = str(input('输入m3u8文件地址：'))
        tit = str(input("视频名称："))
        m3u8_5(url_1=urls,tits = tit)
    elif f =="6":
        pd()
        urls = str(input('输入m3u8文件地址：'))
        tit = str(input("视频名称："))
        m3u8_5(url_1=urls, tits=tit)
    else:
        j = input("是否从新搜索y/n：")
        if j == 'y':
            x(url=url)
            pd()
            m3u8()
        else:
            pd()
            m3u8()

# 主程序入口
if __name__ == "__main__":
    x(url=url)
    paixu()
    while True:
        k = input("是否结束程序?y/n:")
        if k == 'y':
            quit()
        else:
            paixu()