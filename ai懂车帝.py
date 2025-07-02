from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import os


def configure_chrome_options():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 调试时可注释掉
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
    return chrome_options


# 初始化浏览器
def initialize_driver(options):
    # 指定ChromeDriver的路径 - 请替换为你的实际路径
    chromedriver_path = "D:\webhref\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # 修改为你电脑上的实际路径

    # 创建服务对象
    service = Service(executable_path=chromedriver_path)

    # 初始化浏览器
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# 提取车辆信息 - 优化版本，只提取已知信息
def extract_car_info(car_element):
    try:
        # 1. 提取标题
        title = ""
        try:
            title_element = car_element.find_element(By.CSS_SELECTOR, 'dt.tw-font-semibold p.line-1')
            title = title_element.text.strip()
        except:
            pass

        # 2. 提取年份 - 从标题中提取
        year = ""
        if title:
            year_match = re.search(r'(\d{4})款', title)
            if year_match:
                year = year_match.group(1)

        # 3. 提取地区
        location = ""
        try:
            # 使用更精确的选择器定位地区元素
            location_element = car_element.find_element(By.CSS_SELECTOR, 'dd.tw-mt-4.tw-text-color-gray-800')
            location_text = location_element.text.strip()
            # 从文本中提取地区
            location_match = re.search(r'\|(.*?)$', location_text)
            if location_match:
                location = location_match.group(1).strip()
            else:
                location = location_text
        except:
            pass

        # 4. 提取价格
        price = ""
        try:
            # 使用更精确的选择器定位价格元素
            price_element = car_element.find_element(By.CSS_SELECTOR, 'dd.tw-mt-12.tw-font-bold')
            price = price_element.text.strip()
        except:
            pass

        # 5. 提取新车指导价
        new_price = ""
        try:
            # 使用更精确的选择器定位新车指导价元素
            new_price_element = car_element.find_element(By.CSS_SELECTOR, 'div.tw-text-xs.tw-text-auxiliary')
            new_price = new_price_element.text.replace('新车指导价:', '').strip()
        except:
            pass

        # 6. 提取标签信息（检测报告、过户次数等）
        tags = []
        try:
            # 使用更精确的选择器定位标签容器
            tag_container = car_element.find_element(By.CSS_SELECTOR, 'dd.tw-mt-4.tw-flex')
            tag_elements = tag_container.find_elements(By.TAG_NAME, 'span')
            for tag in tag_elements:
                tags.append(tag.text.strip())
        except:
            pass

        # 7. 提取车辆详情页链接
        link = ""
        try:
            link_element = car_element.find_element(By.TAG_NAME, 'a')
            link = link_element.get_attribute('href')
        except:
            pass

        return {
            "标题": title,
            "年份": year,
            "地区": location,
            "价格": price,
            "新车指导价": new_price,
            "标签": ", ".join(tags),
            "链接": link
        }

    except Exception as e:
        print(f"提取车辆信息时出错: {str(e)}")
        return None


# 主爬虫函数
def crawl_dongchedi_cars():
    print("启动懂车帝二手车爬虫...")

    # 配置浏览器
    chrome_options = configure_chrome_options()

    try:
        driver = initialize_driver(chrome_options)

        # 目标URL
        url = "https://www.dongchedi.com/usedcar/x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-4-145-450100-1-x-x-x-x-x"
        print(f"正在访问: {url}")
        driver.get(url)

        # 等待页面加载
        print("等待页面加载完成...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.tw-grid"))
        )
        time.sleep(3)  # 确保所有内容加载完成

        # 滚动页面加载更多内容
        print("滚动页面加载更多车辆...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # 滚动3次加载更多内容
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print("页面加载完成，开始提取车辆信息...")

        # 查找所有车辆元素
        car_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.tw-grid > li')
        print(f"找到 {len(car_elements)} 辆车辆")

        cars_data = []

        # 提取每辆车的信息
        for index, car in enumerate(car_elements, 1):
            print(f"正在处理第 {index}/{len(car_elements)} 辆车...")
            car_info = extract_car_info(car)
            if car_info:
                cars_data.append(car_info)
                # 打印当前车辆信息
                print(f"  > 标题: {car_info['标题']}")
                print(f"  > 年份: {car_info['年份']}, 地区: {car_info['地区']}")
                print(f"  > 价格: {car_info['价格']}, 新车指导价: {car_info['新车指导价']}")
                print(f"  > 标签: {car_info['标签']}")

        # 保存数据
        if cars_data:
            # 创建输出目录
            output_dir = "懂车帝数据"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 生成带时间戳的文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/宝马3系二手车_{timestamp}.xlsx"

            # 保存为Excel
            df = pd.DataFrame(cars_data)
            df.to_excel(filename, index=False)
            print(f"\n成功爬取 {len(cars_data)} 条数据，已保存到: {os.path.abspath(filename)}")
        else:
            print("未提取到有效的车辆数据")

        return cars_data

    except Exception as e:
        print(f"爬取过程中出错: {str(e)}")
        return []

    finally:
        if 'driver' in locals():
            driver.quit()
            print("浏览器已关闭")


# 执行爬虫
if __name__ == "__main__":
    start_time = time.time()
    crawl_dongchedi_cars()
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f}秒")