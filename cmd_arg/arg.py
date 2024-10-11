import argparse

from config.base_config import BaseConfig
from tools.utils import str2bool


async def parse_cmd():
    # 读取command arg
    parser = argparse.ArgumentParser(description='Media crawler program.')
    parser.add_argument('--platform', type=str,
                        help='Media platform select (xhs | dy | ks | bili | wb | tieba | zhihu)',
                        choices=["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"], default=BaseConfig.PLATFORM)
    parser.add_argument('--lt', type=str, help='Login type (qrcode | phone | cookie)',
                        choices=["qrcode", "phone", "cookie"], default=BaseConfig.LOGIN_TYPE)
    parser.add_argument('--type', type=str, help='crawler type (search | detail | creator)',
                        choices=["search", "detail", "creator"], default=BaseConfig.CRAWLER_TYPE)
    parser.add_argument('--start', type=int,
                        help='number of start page', default=BaseConfig.START_PAGE)
    parser.add_argument('--keywords', type=str,
                        help='please input keywords', default=BaseConfig.KEYWORDS)
    parser.add_argument('--get_comment', type=str2bool,
                        help='''whether to crawl level one comment, supported values case insensitive ('yes', 'true', 't', 'y', '1', 'no', 'false', 'f', 'n', '0')''',
                        default=BaseConfig.ENABLE_GET_COMMENTS)
    parser.add_argument('--get_sub_comment', type=str2bool,
                        help=''''whether to crawl level two comment, supported values case insensitive ('yes', 'true', 't', 'y', '1', 'no', 'false', 'f', 'n', '0')''',
                        default=BaseConfig.ENABLE_GET_SUB_COMMENTS)
    parser.add_argument('--save_data_option', type=str,
                        help='where to save the data (csv or db or json)', choices=['csv', 'db', 'json'],
                        default=BaseConfig.SAVE_DATA_OPTION)
    parser.add_argument('--cookies', type=str,
                        help='cookies used for cookie login type', default=BaseConfig.COOKIES)

    args = parser.parse_args()

    # override config
    BaseConfig.PLATFORM = args.platform
    BaseConfig.LOGIN_TYPE = args.lt
    BaseConfig.CRAWLER_TYPE = args.type
    BaseConfig.START_PAGE = args.start
    BaseConfig.KEYWORDS = args.keywords
    BaseConfig.ENABLE_GET_COMMENTS = args.get_comment
    BaseConfig.ENABLE_GET_SUB_COMMENTS = args.get_sub_comment
    BaseConfig.SAVE_DATA_OPTION = args.save_data_option
    BaseConfig.COOKIES = args.cookies
