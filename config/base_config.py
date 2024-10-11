class BaseConfig:
    # 基础配置
    PLATFORM = "xhs"
    KEYWORDS = "文案"
    LOGIN_TYPE = "cookie"  # qrcode or phone or cookie
    COOKIES = "abRequestId=3644d200-862b-5419-8e58-dfe27f6b5e25; xsecappid=xhs-pc-web; a1=190fc92d62e0fkiqbp7qafb82toa8t1oxxuzw1nzz50000340440; webId=247b0eef6eb526082ee4ae70c40d8ffa; gid=yjyyYfqJ40CSyj8iSjJfKCyIJd8iT3ADUWA07uuiDYJ9lu280Y9ylE888q484488qWq4W88K; webBuild=4.34.0; unread={%22ub%22:%2266e2aaef00000000120132dc%22%2C%22ue%22:%2266e119490000000026033353%22%2C%22uc%22:22}; web_session=040069b368f57b12afd2cc93d6344b064da82d; acw_tc=57f199946dc962ba20ff641703c0b317eef7179a0f65356180ecb50467ba69a9; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=2b6d67d0-76b1-4574-a9bd-60fd2f1e0b6d"
    # 具体值参见media_platform.xxx.field下的枚举值，暂时只支持小红书
    SORT_TYPE = "popularity_descending"
    # 具体值参见media_platform.xxx.field下的枚举值，暂时只支持抖音
    PUBLISH_TIME_TYPE = 0
    CRAWLER_TYPE = "search"  # 爬取类型，search(关键词搜索) | detail(帖子详情)| creator(创作者主页数据)

    # 是否开启 IP 代理
    ENABLE_IP_PROXY = True

    # 代理IP池数量
    IP_PROXY_POOL_COUNT = 1

    # 代理IP提供商名称
    IP_PROXY_PROVIDER_NAME = "kuaidaili"

    # 设置为True不会打开浏览器（无头浏览器）
    # 设置False会打开一个浏览器
    # 小红书如果一直扫码登录不通过，打开浏览器手动过一下滑动验证码
    # 抖音如果一直提示失败，打开浏览器看下是否扫码登录之后出现了手机号验证，如果出现了手动过一下再试。
    HEADLESS = False

    # 是否保存登录状态
    SAVE_LOGIN_STATE = True

    # 数据保存类型选项配置,支持三种类型：csv、db、json, 最好保存到DB，有排重的功能。
    SAVE_DATA_OPTION = "db"  # csv or db or json

    # csv、json文件存储目录
    FILE_SAVE_DIR = "data/xhs"

    # 用户浏览器缓存的浏览器文件配置
    USER_DATA_DIR = "%s_user_data_dir"  # %s will be replaced by platform name

    # 爬取开始页数 默认从第一页开始
    START_PAGE = 1

    # 爬取视频/帖子的数量控制
    CRAWLER_MAX_NOTES_COUNT = 100

    # 并发爬虫数量控制
    MAX_CONCURRENCY_NUM = 1

    # 是否开启爬图片模式, 默认不开启爬图片
    ENABLE_GET_IMAGES = False

    # 是否开启爬评论模式, 默认不开启爬评论
    ENABLE_GET_COMMENTS = False

    # 是否开启爬二级评论模式, 默认不开启爬二级评论
    # 老版本项目使用了 db, 则需参考 schema/tables.sql line 287 增加表字段
    ENABLE_GET_SUB_COMMENTS = False

    # 直存本地标志，True-狩猎完后直接保存到本地；False-不保存到本地
    SAVE_LOCAL_FLAG = False

    # xhs是否遮水印，True-遮掉水印；False-不遮水印
    XHS_COVER_WATERMARK = False

    # xhs水印原图是否保留，True-保留；False-不保留
    XHS_SAVE_WATERMARK_ORIGIN_IMAGE = False

    # xhs下载范围。查看DownloadScope枚举类
    XHS_DOWNLOAD_SCOPE = 1

    # 直存本地目录
    DOWNLOAD_DIR = ""

    # 指定小红书需要爬虫的笔记ID列表
    XHS_SPECIFIED_ID_LIST = [
        "668d40ea0000000005006252",
        "66d87db3000000001f019c66",
    ]

    # 指定抖音需要爬取的ID列表
    DY_SPECIFIED_ID_LIST = [
        "7190600830188391718"
        # ........................
    ]

    # 指定快手平台需要爬取的ID列表
    KS_SPECIFIED_ID_LIST = [
        "3xf8enb8dbj6uig",
        "3x6zz972bchmvqe"
    ]

    # 指定B站平台需要爬取的视频bvid列表
    BILI_SPECIFIED_ID_LIST = [
        "BV1d54y1g7db",
        "BV1Sz4y1U77N",
        "BV14Q4y1n7jz",
        # ........................
    ]

    # 指定微博平台需要爬取的帖子列表
    WEIBO_SPECIFIED_ID_LIST = [
        "4982041758140155",
        # ........................
    ]

    # 指定weibo创作者ID列表
    WEIBO_CREATOR_ID_LIST = [
        "5533390220",
        # ........................
    ]

    # 指定贴吧需要爬取的帖子列表
    TIEBA_SPECIFIED_ID_LIST = [

    ]

    # 指定贴吧名称列表，爬取该贴吧下的帖子
    TIEBA_NAME_LIST = [
        # "盗墓笔记"
    ]

    TIEBA_CREATOR_URL_LIST = [
        "https://tieba.baidu.com/home/main/?id=tb.1.7f139e2e.6CyEwxu3VJruH_-QqpCi6g&fr=frs",
        # ........................
    ]

    # 指定小红书创作者ID列表
    XHS_CREATOR_ID_LIST = [
        "63e36c9a000000002703502b",
        # ........................
    ]

    # 指定Dy创作者ID列表(sec_id)
    DY_CREATOR_ID_LIST = [
        "MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE",
        # ........................
    ]

    # 指定bili创作者ID列表(sec_id)
    BILI_CREATOR_ID_LIST = [
        "20813884",
        # ........................
    ]

    # 指定快手创作者ID列表
    KS_CREATOR_ID_LIST = [
        "3x4sm73aye7jq7i",
        # ........................
    ]

    # 词云相关
    # 是否开启生成评论词云图
    ENABLE_GET_WORDCLOUD = False
    # 自定义词语及其分组
    # 添加规则：xx:yy 其中xx为自定义添加的词组，yy为将xx该词组分到的组名。
    CUSTOM_WORDS = {
        '零几': '年份',  # 将“零几”识别为一个整体
        '高频词': '专业术语'  # 示例自定义词
    }

    # 停用(禁用)词文件路径
    STOP_WORDS_FILE = "./docs/hit_stopwords.txt"

    # 中文字体文件路径
    FONT_PATH = "./docs/STZHONGS.TTF"
