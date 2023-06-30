import pdfkit,csv,requests,time,re
import msvcrt#终端设置按任意键退出程序
from bs4 import BeautifulSoup
def time_master(func):
    def call_func(*args, **kwargs):
        print('-'*40)
        print(f"{func.__name__} start ...")
        #获取开始时间戳
        start=time.time()
        func(*args, **kwargs)
        #获取结束时间戳
        stop=time.time()
        print(f"{func.__name__}一共运行了{(stop-start):.2f}s")
        print(f"{func.__name__} over...")
    return call_func
@time_master
def html_to_pdf(value, key):
    # 将wkhtmltopdf.exe程序绝对路径传入config对象
    path_wkthmltopdf = r'D:\\tools\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    pdfkit_options = {'encoding': 'UTF-8'}
    # 生成pdf文件，to_file为文件路径
    pdfkit.from_string(value,key+'.pdf', configuration=config, options=pdfkit_options)
    print(key+'.pdf','完成')
@time_master
def get_from_url(url,headers,title,tag,class_=None,style=None):
    """ 
    爬取网站上的信息,导出为pdf
    url:网址
    headers:响应头
    title:文章标题
    tag:需要获取的html标签
    class_:html标签的属性
    style=None:html标签的属性
    """
    res = requests.get(url,headers=headers)
    res.encoding = 'utf-8' # 设置编码
    #bs4获取数据
    soup = BeautifulSoup(res.text, 'html.parser')
    #打开网站通过网页捕获获得对应的css条目
    #<div class="bookcont" style=" border:0px;">
    html= soup.find(tag,class_=class_,style=style)
    #去除隐藏标签
    html=str(html).replace("hidden","visible").replace("data-src","src")
    html_to_pdf(html,title)

class File_To_Pdf:
    def __init__(self,file_name,pdf_name=None,row_title=None,row_html=None):
        """ 
        读取文件,并将文件转换成pdf
        file_name:文件名
        pdf_name:pdf文件名
        row_title:csv文件中标题所在的行
        row_html:csv文件中html所在的行
        """
        self.file_name=file_name
        self.pdf_name=pdf_name
        self.content=None
        self.row_title=None
        self.row_html=None
    def content_to_pdf(self):
        if isinstance(self.content, dict):
            for key,value in dict.items():
                if("|" in key or"/" in key):
                    key=key.replace("|",":")
                    key=key.replace("/"," ")
                html_to_pdf(value, key)
        else:html_to_pdf(self.content,self.pdf_name)
    @time_master
    def get_content(self):
        file_type=self.file_name.split('.')[-1]
        if file_type=="html":
            with open(self.file_name,encoding="utf-8")as f:
                self.content=f.read()
        elif file_type=="csv":
            with open(self.file_name,encoding="utf-8") as f:
                reader_cars=next(csv.reader(f))#返回的不是列表而是一个可迭代对象(csv.reader)
                for row in reader_cars:
                    标题=row[self.row_title]
                    内容=row[self.row_html]
                    self.content[标题]=内容
    def __call__(self):
        self.get_content()
        self.content_to_pdf()

class SPIDER():
    def __init__(self,url,User_Agent,Cookie=None,title=None):
        self.url=url
        self.headers={"User-Agent":User_Agent,"Cookie":Cookie}
        self.title=title
    def get_pages_WeChat(self,pages,page_tag,page_class_=None,page_style=None):
        all=[]
        if self.headers["Cookie"]:raise TypeError("补充Cookie")
        for i in range(pages):
            response=requests.get(self.url,headers=self.headers)#得到响应内容
            response.encoding='utf-8'#设置响应内容为utf-8格式
            html=response.text#得到网页的文本形式
            #可以设置一个自定义的解析函数来对网页的文本数据进行解析
            title=re.findall('"title":"(.*?)"',html)#得到文章标题
            link=re.findall('"link":"(.*?)"',html)#得到文章链接
            
            tips=zip(title,link)#利用zip方法,将两个列表中的数据一一对应
            all.append(list(tips))#list是对zip方法得到的数据进行解压
        for data in all:
            for title,link in data:
                time.sleep(2)#每爬取一篇文章间隔3秒,以防触发反爬
                get_from_url(link,self.headers,title,page_tag,page_class_,page_style)
    def get_page_url(self,mode,tag=None,class_=None,style=None):
        if mode==None:
            get_from_url(self.url,self.headers,self.title,tag,class_=None,style=None)
        elif mode.lower()=="csdn":
            get_from_url(self.url,self.headers,self.title,tag='article',class_="baidu_pl")
        elif mode.lower()=="zhihu":
            get_from_url(self.url,self.headers,self.title,tag='div',class_="css-376mun")
        elif mode.lower()=="wechat":
            get_from_url(self.url,self.headers,self.title,tag="div",class_="rich_media_wrp")
    def html_to_file(self,file_name,pdf_name=None,row_title=None,row_html=None):
        HtmlToPdf=File_To_Pdf(file_name,pdf_name,row_title,row_html)
        HtmlToPdf()

url=input("请输入网址:")
User_Agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0'
title=input("请输入转换后的pdf名字:")
title='C:\\Users\\amin\\Downloads'+"\\"+title
spider=SPIDER(url,User_Agent,title=title)
mode=input("请输入下载的网站:wechat(微信),csdn,zhihu(知乎):")
spider.get_page_url(mode=mode)
print("按任意键退出程序...",end='')
print(ord(msvcrt.getch()))