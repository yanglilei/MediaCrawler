import asyncio
import sys
from urllib import parse

from PyQt5.QtCore import QThread, pyqtSignal
from openpyxl.utils import column_index_from_string

import cmd_arg
import db
from base.base_crawler import AbstractCrawler, InterfaceParams, CrawlerConfigInfo, CrawlerConfigInfoWrapper, Platform, \
    CrawlerType
from config.base_config import BaseConfig
from constants import Constants
from media_platform.bilibili import BilibiliCrawler
from media_platform.douyin import DouYinCrawler
from media_platform.kuaishou import KuaishouCrawler
from media_platform.tieba import TieBaCrawler
from media_platform.weibo import WeiboCrawler
from media_platform.xhs import XiaoHongShuCrawler
from media_platform.zhihu import ZhihuCrawler
from tools.utils import ExcelPositionUtils, LOG, ConfigFileReader
from tools.xlsx_util import XLSXOperator


class CrawlerFactory:
    CRAWLERS = {
        "xhs": XiaoHongShuCrawler,
        "dy": DouYinCrawler,
        "ks": KuaishouCrawler,
        "bili": BilibiliCrawler,
        "wb": WeiboCrawler,
        "tieba": TieBaCrawler,
        "zhihu": ZhihuCrawler
    }

    @staticmethod
    def create_crawler(platform: str) -> AbstractCrawler:
        crawler_class = CrawlerFactory.CRAWLERS.get(platform)
        if not crawler_class:
            raise ValueError("Invalid Media Platform Currently only supported xhs or dy or ks or bili ...")
        return crawler_class()


def init_base_config():
    headless_mode = ConfigFileReader.get_val(Constants.ConfigFileKey.HEADLESS_MODE)
    if headless_mode is None or headless_mode == "1":
        BaseConfig.HEADLESS = True
    else:
        BaseConfig.HEADLESS = False

    ip_proxy_pool_count = ConfigFileReader.get_val(Constants.ConfigFileKey.IP_PROXY_POOL_COUNT)
    # 默认1个
    BaseConfig.IP_PROXY_POOL_COUNT = int(ip_proxy_pool_count) if ip_proxy_pool_count else 1


async def main():
    # parse cmd
    await cmd_arg.parse_cmd()

    # init base config
    init_base_config()

    # init db
    if BaseConfig.SAVE_DATA_OPTION == "db":
        await db.init_db()

    crawler = CrawlerFactory.create_crawler(platform=BaseConfig.PLATFORM)
    await crawler.start()

    if BaseConfig.SAVE_DATA_OPTION == "db":
        await db.close()


if __name__ == '__main__':
    try:
        # asyncio.run(main())
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit()


class CrawlerConfigInfoOperator(XLSXOperator):
    def __init__(self, workbook_path: str, sheet_name, start_cell_pos, end_cell_pos):
        start_column, start_row_no = ExcelPositionUtils.parse_excel_position(start_cell_pos)
        end_column, end_row_no = ExcelPositionUtils.parse_excel_position(end_cell_pos)
        super().__init__(workbook_path, sheet_name, start_column, end_column, start_row_no, end_row_no)

    def get_data(self) -> CrawlerConfigInfoWrapper:
        """
        获取重写文章信息
        :return: [CrawlerConfigInfo, ..., ]
        """
        ret = None
        crawler_config_info = []
        try:
            self.open()
        except Exception as e:
            LOG.exception("打开文档失败！")
        else:
            # 默认输出目录在A1单元格中！
            default_output_dir = self.worksheet["A1"].value

            min_col = column_index_from_string(self.start_column)
            max_col = column_index_from_string(self.end_column)
            if max_col - min_col + 1 < 1:
                raise Exception(f"至少需要选取1列【小红薯地址】数据，请检查文档！")

            for row in self.worksheet.iter_rows(min_row=self.start_line_no,
                                                max_row=self.end_line_no,
                                                min_col=min_col,
                                                max_col=max_col):
                xhs_url_cell = row[0]
                xhs_url = xhs_url_cell.value
                if not xhs_url:
                    # 忽略该行
                    LOG.error(f"第{xhs_url_cell.row}行记录的url为空，忽略该行！")
                    continue

                # xhs_output_dir_cell = row[3]
                # xhs_output_dir = xhs_output_dir_cell.value if xhs_output_dir_cell.value else default_output_dir
                # if not xhs_output_dir:
                #     LOG.error(f"第{xhs_output_dir_cell.row}行记录的存放目录为空，忽略该行！")
                #     continue
                # if not os.path.exists(xhs_output_dir):
                #     LOG.error(f"第{xhs_output_dir_cell.row}行记录的存放目录不存在，忽略该行！")
                #     continue

                crawler_config_info.append(CrawlerConfigInfo(xhs_url, "",
                                                             xhs_url_cell.row,
                                                             xhs_url_cell.column))

            ret = CrawlerConfigInfoWrapper(crawler_config_info)
        finally:
            self.close()

        return ret


class CrawlerBusiHandler(QThread):
    reset_buttons_signal = pyqtSignal(bool)

    def __init__(self, ):
        super().__init__()
        self._interface_params = None

    @property
    def interface_params(self):
        return self._interface_params

    @interface_params.setter
    def interface_params(self, interface_params: InterfaceParams):
        self._interface_params = interface_params

    async def run_busi(self):
        try:
            # 初始化配置信息，利用从页面传递过来的参数进行初始化
            self.init_config_info(self.interface_params)
            # init db
            if BaseConfig.SAVE_DATA_OPTION == "db":
                await db.init_db()

            crawler = CrawlerFactory.create_crawler(platform=BaseConfig.PLATFORM)
            await crawler.start()
        except Exception as e:
            LOG.exception("意外退出")
        finally:
            self.reset_buttons_signal.emit(True)
            if BaseConfig.SAVE_DATA_OPTION == "db":
                await db.close()

    def run(self):
        try:
            # 在本地环境可以运行，打包出去后，无法运行
            # asyncio.get_event_loop().run_until_complete(self.run_busi())

            # 打包出来后，需要使用下面的代码
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_busi())
        except:
            LOG.exception("意外退出")
        else:
            LOG.info("狩猎结束！")

    def init_config_info(self, interface_params: InterfaceParams):

        def check_params(interface_params: InterfaceParams):
            if not interface_params:
                raise ValueError("参数缺失")

            # if not interface_params.xlsx_path and not os.path.exists(interface_params.xlsx_path):
            #     raise ValueError("文件路径不合法")
            #
            # if interface_params.xlsx_path and not interface_params.sheet_name:
            #     raise ValueError("表格名称不合法")

            # if not interface_params.platform:
            #     raise ValueError("平台缺失")

            # if interface_params.crawler_type == CrawlerType.SEARCH and not interface_params.start_page:
            #     raise ValueError("起始页数缺失")

            # if interface_params.crawler_type == CrawlerType.SEARCH and not interface_params.keywords:
            #     raise ValueError("关键词缺失")

            # if interface_params.login_type == LoginType.COOKIE and not interface_params.cookies:
            #     raise ValueError("cookies缺失")

        def get_specified_id_from_url(platform, url):
            specified_id = None
            url = url.strip()
            parsed_url = parse.urlparse(url)

            if platform == Platform.XHS:
                url_path = parsed_url.path
                url_path.strip("/")
                specified_id = url_path[url_path.rfind("/") + 1:]
            elif platform == Platform.BILI:
                pass
            elif platform == Platform.TIEBA:
                pass
            elif platform == Platform.KS:
                pass
            elif platform == Platform.DY:
                pass
            elif platform == Platform.WEIBO:
                pass
            return specified_id

        check_params(interface_params)
        crawler_config_info_operator = CrawlerConfigInfoOperator(interface_params.xlsx_path,
                                                                 interface_params.sheet_name,
                                                                 interface_params.url_info_start_cell,
                                                                 interface_params.url_info_end_cell)

        crawler_config_info: CrawlerConfigInfoWrapper = crawler_config_info_operator.get_data()

        specified_ids = [get_specified_id_from_url(interface_params.platform, item.url_info) for item in
                         crawler_config_info.payloads]

        if interface_params.crawler_type == CrawlerType.DETAIL and not specified_ids:
            raise ValueError("note id未指定")

        if interface_params.platform == Platform.XHS:
            if interface_params.crawler_type == CrawlerType.DETAIL:
                # 指定ID
                BaseConfig.XHS_SPECIFIED_ID_LIST = specified_ids
            elif InterfaceParams.crawler_type == CrawlerType.CREATOR:
                BaseConfig.XHS_CREATOR_ID_LIST = specified_ids

        if interface_params.platform == Platform.DY:
            if interface_params.crawler_type == CrawlerType.DETAIL:
                # 指定ID
                BaseConfig.DY_SPECIFIED_ID_LIST = specified_ids
            elif InterfaceParams.crawler_type == CrawlerType.CREATOR:
                BaseConfig.DY_CREATOR_ID_LIST = specified_ids

        if interface_params.platform == Platform.KS:
            if interface_params.crawler_type == CrawlerType.DETAIL:
                # 指定ID
                BaseConfig.KS_SPECIFIED_ID_LIST = specified_ids
            elif InterfaceParams.crawler_type == CrawlerType.CREATOR:
                BaseConfig.KS_CREATOR_ID_LIST = specified_ids

        if interface_params.platform == Platform.BILI:
            if interface_params.crawler_type == CrawlerType.DETAIL:
                # 指定ID
                BaseConfig.BILI_SPECIFIED_ID_LIST = specified_ids
            elif InterfaceParams.crawler_type == CrawlerType.CREATOR:
                BaseConfig.BILI_CREATOR_ID_LIST = specified_ids

        if interface_params.platform == Platform.WEIBO and interface_params.crawler_type == CrawlerType.DETAIL:
            # 指定ID
            BaseConfig.WEIBO_SPECIFIED_ID_LIST = specified_ids

        if interface_params.platform == Platform.TIEBA and interface_params.crawler_type == CrawlerType.DETAIL:
            # 指定ID
            BaseConfig.TIEBA_SPECIFIED_ID_LIST = specified_ids

        BaseConfig.KEYWORDS = interface_params.keywords
        BaseConfig.COOKIES = interface_params.cookies
        BaseConfig.PLATFORM = interface_params.platform.value
        BaseConfig.LOGIN_TYPE = interface_params.login_type.value
        BaseConfig.CRAWLER_TYPE = interface_params.crawler_type.value
        BaseConfig.START_PAGE = interface_params.start_page
        BaseConfig.ENABLE_GET_COMMENTS = interface_params.enable_get_comments
        BaseConfig.ENABLE_GET_SUB_COMMENTS = interface_params.enable_get_sub_comments
        BaseConfig.SAVE_DATA_OPTION = interface_params.save_data_option.value
        BaseConfig.FILE_SAVE_DIR = interface_params.file_save_dir
        BaseConfig.SAVE_LOCAL_FLAG = interface_params.save_local_flag
        BaseConfig.DOWNLOAD_DIR = interface_params.download_dir
        BaseConfig.ENABLE_IP_PROXY = interface_params.enable_proxy
        BaseConfig.XHS_COVER_WATERMARK = interface_params.xhs_cover_watermark
        BaseConfig.XHS_SAVE_WATERMARK_ORIGIN_IMAGE = interface_params.xhs_save_watermark_origin_image
        BaseConfig.XHS_DOWNLOAD_SCOPE = interface_params.xhs_download_scope
