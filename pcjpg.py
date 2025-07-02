import requests
import re
import time

dic = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
       'Cookie':'cf_clearance=fmyfqyy6m11XbOF55BB5.nVSkQu3vos5UHEZ6iFStMU-1745328675-1.2.1.1-OIi48umEP58Yl6ONnOUFUhsrKrndM.9L.PZACueHDxdsUHMOjRqtYeUSsgimmCf_jhTPkexoJWArfAp_sOMfKQiZyRi.uHokOIRBZ2WJIJ_S23_JHjLWbFPfHdKZDBH2TZIBAEybe3aO_RSj7kc8WtAZVgQkR1YXwbaAhJsuk0axm1dgNkVdQ0aIM5vx1i7anX54UPkolfDXMF8nNBOwzgO8EvY6yHpgx5_z2DduLvECd49WZejlT36QhFOFars30sjquI86xQdm.v42gZmZ28uRmPyLwyWgI7URx60eXeSJBAUEmBOgdtaXSEodZ352rqV2kWDzztfgjgHdRWJMvLo33zP7um6Jo.z.ezLSc.saNKRI8NeW_24Y7LR3m4dv; trenvecookieclassrecord=%2C19%2C'}
def Picture_Download(url_img_path, img_title):
    file_name = img_title.replace('/',' ').strip()
    try:
        result = requests.get(url_img_path.strip())
    except:
        print(url_img_path, 'Download failed')
    else:
        if result.status_code == 200:
            File = open('壁纸文件夹/' +file_name+ '.jpg','wb')
            File.write(result.content)
            File.close()

def Img_Url(url):
    result = requests.get(url,headers=dic)
    result.encoding = 'gbk'
    compile = re.compile(r'<img src="(.*?)" alt="(.*?)" />')
    all = compile.findall(result. text)
    for item in all:
        print(item[0], item[1])
        Picture_Download(item[0], item[1])

def main(y,z):
    for i in range(y,z):
        if i == 1:
            Img_Url(r'http://www.netbian.com/dongman/')
        else:
            Img_Url(r'http://www.netbian.com/dongman/index_%d.htm' % i)
            print("全部完成！！！")
            time.sleep(2)


if __name__  == '__main__':
    y = int(input("初始页数13："))
    z = int(input('末尾页数：'))
    main(y,z)