from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, List

from playwright.async_api import BrowserContext, BrowserType


class AbstractCrawler(ABC):
    @abstractmethod
    async def start(self):
        """
        start crawler
        """
        pass

    @abstractmethod
    async def search(self):
        """
        search
        """
        pass

    @abstractmethod
    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[str],
                             headless: bool = True) -> BrowserContext:
        """
        launch browser
        :param chromium: chromium browser
        :param playwright_proxy: playwright proxy
        :param user_agent: user agent
        :param headless: headless mode
        :return: browser context
        """
        pass


class AbstractLogin(ABC):
    @abstractmethod
    async def begin(self):
        pass

    @abstractmethod
    async def login_by_qrcode(self):
        pass

    @abstractmethod
    async def login_by_mobile(self):
        pass

    @abstractmethod
    async def login_by_cookies(self):
        pass


class AbstractStore(ABC):
    @abstractmethod
    async def store_content(self, content_item: Dict):
        pass

    @abstractmethod
    async def store_comment(self, comment_item: Dict):
        pass

    # TODO support all platform
    # only xhs is supported, so @abstractmethod is commented
    @abstractmethod
    async def store_creator(self, creator: Dict):
        pass


class AbstractStoreImage(ABC):
    # TODO: support all platform
    # only weibo is supported
    # @abstractmethod
    async def store_image(self, image_content_item: Dict):
        pass


class AbstractApiClient(ABC):
    @abstractmethod
    async def request(self, method, url, **kwargs):
        pass

    @abstractmethod
    async def update_cookies(self, browser_context: BrowserContext):
        pass


class DownloadScope(Enum):
    # 下载范围，在XHS中，当下载笔记到本地时，可以选择只下载当前抓取到的记录和库中所有未下载的记录
    # 当前记录
    CURRENT = 1
    # 所有记录
    ALL = 2


class CrawlerType(Enum):
    # 爬取类型，search(关键词搜索) | detail(帖子详情)| creator(创作者主页数据)
    SEARCH = "search"
    DETAIL = "detail"
    CREATOR = "creator"


class Platform(Enum):
    # 小红书
    XHS = "xhs"
    # 抖音
    DY = "dy"
    # 快手
    KS = "ks"
    # 哔哩哔哩
    BILI = "bili"
    # 微博
    WEIBO = "wb"
    # 贴吧
    TIEBA = "tieba"
    # 知乎
    ZHIHU = "zhihu"


class LoginType(Enum):
    # 二维码登录
    QRCODE = "qrcode"
    # 手机号登录
    MOBILE = "phone"
    # cookie登录
    COOKIE = "cookie"


class SaveDataOption(Enum):
    DB = "db"
    CSV = "csv"
    JSON = "json"


@dataclass
class InterfaceParams:
    # url文件路径
    xlsx_path: str
    # 表格名称
    sheet_name: str
    # 起始单元格
    url_info_start_cell: str
    # 截止单元格
    url_info_end_cell: str
    # 搜索关键词
    keywords: str
    # 使用cookie登录时，要指定的cookie字符串
    cookies: str
    # csv、json文件存储的目录
    file_save_dir: str
    # 直存本地标志，True-狩猎完后直接保存到本地；False-不保存到本地
    save_local_flag: bool = False
    # 直存本地的目录
    download_dir: str = ""
    # 是否开启代理
    enable_proxy: bool = False
    # xhs是否遮水印
    xhs_cover_watermark: bool = False
    # xhs水印原图是否保留
    xhs_save_watermark_origin_image: bool = False
    # xhs下载范围。1-当前；2-所有
    xhs_download_scope: DownloadScope = DownloadScope.CURRENT
    # if url_info_start_cell:
    #     start_column, start_row_no = ExcelPositionUtils.parse_excel_position(url_info_start_cell)
    # if url_info_end_cell:
    #     end_column, end_row_no = ExcelPositionUtils.parse_excel_position(url_info_end_cell)
    # 抓取平台
    platform: Platform = Platform.XHS
    # 登录方式
    login_type: LoginType = LoginType.COOKIE
    # 抓取类型
    crawler_type: CrawlerType = CrawlerType.DETAIL
    # 抓取起始页
    start_page: int = 1
    # 是否获取评论
    enable_get_comments: bool = False
    # 是否获取子评论
    enable_get_sub_comments: bool = False
    # 数据存储方式
    save_data_option: SaveDataOption = SaveDataOption.DB


class CrawlerConfigInfo:
    def __init__(self, url: str, save_dir: str, row_no: int, max_colum_no: int):
        """
        配置信息
        :param url: url地址
        :param save_dir: 存放目录
        :param row_no: int, 行号，数字
        :param max_colum_no: int, 最后一列，数字
        """
        self.url_info = url
        self.save_dir = save_dir
        self.row_no = row_no
        self.max_colum_no = max_colum_no


class CrawlerConfigInfoWrapper:
    def __init__(self, payloads: List[CrawlerConfigInfo], *args):
        """
        文章重写信息包装器
        :param payloads: 重写信息
        """
        self.payloads = payloads
        self.args = args
