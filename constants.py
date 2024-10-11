from enum import Enum


class SignUpSituation(Enum):
    """
    已注册
    未注册的情况，有两种
    """
    # 已注册
    COMPLETE_SIGN_UP = 0
    # 学校未知
    SCHOOL_UNKNOWN = 1
    # 信息未完善
    INFO_UNCOMPLETED = 2


class MsgCmd(Enum):
    """
    消息指令
    """
    # 切换课程
    CHANGE_COURSE = 1
    # 切换目录
    CHANGE_CONTENT = 2
    # 学习线程强制退出的指令。当目录切换线程异常退出的时候，通知学习线程强制退出
    LEARNING_THREAD_FORCE_EXIT = 3
    # 学习线收到线程强制退出指令的回复指令。学习线程收到目录切换线程的强制退出信号之后，给目录切换线程发出响应，确认收到强制退出的信号了
    LEARNING_THREAD_FORCE_EXIT_RESPONSE = 4
    # 目录切换线程退出的指令。当主线程（课程切换线）异常退出的时候，通知目录切换线程强制退出
    CHANGE_CONTENT_THREAD_FROCE_EXIT = 5
    # 目录切换收到线程强制退出指令的回复指令。
    CHANGE_CONTENT_THREAD_FORCE_EXIT_RESPONSE = 6
    # 课程切换线程退出
    CHANGE_COURSE_THREAD_FORCE_EXIT = 7
    # 目录切换线程需要重启的标志，当该线程异常退出的时候，会向父线程发送我需要重启的标志
    # 父线程收到该信息，会去重启子线程
    CHANGE_CONTENT_THREAD_NEED_TO_RESTART = 8
    # 学习线程需要重启的标志
    LEARNING_THREAD_NEED_TO_RESTART = 9
    # 任务监控线退出指令
    TASK_MONITOR_THREAD_EXIT = 10
    # 切换课程回复
    CHANGE_COURSE_RESPONSE = 11
    # 做作业
    FJRC_EXERCISE_MONITOR_THREAD_EXIT = 12
    # 跳过该课程
    SKIP_COURSE = 99
    # 工作线程退出指令
    WORK_THREAD_EXIT = 13


class QueueMsg():

    def __init__(self, msg_cmd: MsgCmd, *args):
        self.msg_cmd = msg_cmd
        self.args = args

    def get_args(self):
        return self.args

    def get_msg_cmd(self):
        return self.msg_cmd


class HXCourseType(Enum):
    """
    海西课程类型
    """
    PUB_COURSE = (1, "公需课")
    PRO_COURSE = (2, "专业课")


class Constants:
    """
    常量存放的位置
    """

    class ConfigFileKey:
        # 激活状态
        ACTIVATE_STATUS = "activate_status"
        # 用户信息文件路径
        DATA_FILE_DIR = "data_file_dir"
        # 日志记录在本地文件的标志，1-记录
        LOG_LOCAL_FLAG = "log_local_flag"
        # 工作表名称
        WORKSHEET_NAME = "worksheet_name"
        # 文章信息表起始单元格
        ARTICLE_INFO_START_CELL_POSITION = "article_info_start_cell_position"
        # 文章信息表截止单元格
        ARTICLE_INFO_END_CELL_POSITION = "article_info_end_cell_position"
        # 标点符号
        PUNCTUATION_MARKS = "punctuation_marks"
        # cookie
        MC_COOKIE = "mc_cookie"
        # 主机地址
        DM2L_HOST = "dm2l_host"
        # 端口
        DM2L_PORT = "dm2l_port"
        # 用户名
        DM2L_USER = "dm2l_user"
        # 密码
        DM2L_PASSWORD = "dm2l_password"
        # 数据库
        DM2L_DATABASE = "dm2l_database"
        # 字符集
        DM2L_CHARSET = "dm2l_charset"
        # 图片下载时间间隔，单位秒
        DM2L_IMG_DOWNLOAD_INTERVAL = "dm2l_img_download_interval"
        # 下载笔记的目录
        DM2L_DOWNLOAD_DIR = "dm2l_download_dir"
        # 快代理用户名
        KDL_USER_NAME = "kdl_user_name"
        # 快代理密码
        KDL_USER_PWD = "kdl_user_pwd"
        # 快代理的SecretId
        KDL_SECRET_ID = "kdl_secret_id"
        # 快代理的SecretKey
        KDL_SECRET_KEY = "kdl_secret_key"
        # 无头模式
        HEADLESS_MODE = "headless_mode"
        # 代理ip池的容量
        IP_PROXY_POOL_COUNT = "ip_proxy_pool_count"

