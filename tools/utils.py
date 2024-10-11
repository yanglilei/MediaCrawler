import argparse
import configparser
import logging
import sys
import uuid
from logging.handlers import RotatingFileHandler

import psutil
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKC
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_PKC
from PyQt5.QtCore import QThread, pyqtSignal

from base.base_ui import get_child_processes
from constants import Constants
from .crawler_util import *
from .slider_util import *
from .time_util import *


def init_loging_config():
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _logger = logging.getLogger("MediaCrawler")
    _logger.setLevel(level)
    return _logger


# logger = init_loging_config()

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class ArticleFormatterUtils:

    @classmethod
    def format_title(cls, title):
        if title:
            # 定义要删除的字符列表
            invalid_chars = ['\\', '/', '*', '<', '>', '|', '"', '\t']
            title = cls.remove_invalid_chars(title, invalid_chars).strip()
            if title:
                title = cls.switch_quota(title)
        return title

    @classmethod
    def one_key_2_chinese(cls, words):
        new_words = cls.switch_quota(words, 1)
        return new_words.replace("\r\n", "\n")

    @classmethod
    def switch_quota(cls, words, mode=1):
        """
        转换引号，单引号和双引号
        :param words: 文本
        :param mode: 1-英文标点符号转中文；2-中文标点符号转英文
        :return: str，转换后的文本
        """
        if mode != 1:
            raise ValueError("模式不支持")

        replaced_text = cls.switch_double_quota(words, mode)
        replaced_text = cls.switch_single_quota(replaced_text, mode)
        replaced_text = replaced_text.replace(",", "，")
        replaced_text = replaced_text.replace(":", "：")
        replaced_text = replaced_text.replace("?", "？")
        replaced_text = replaced_text.replace("!", "！")
        replaced_text = replaced_text.replace(";", "；")
        return replaced_text

    @staticmethod
    def remove_invalid_chars(words, invalid_chars: List[str]):
        # 将字符列表转换为正则表达式字符串
        # 使用re.escape来转义特殊字符
        invalid_chars_pattern = '[' + ''.join(re.escape(char) for char in invalid_chars) + ']'
        return re.sub(invalid_chars_pattern, '', words)

    @classmethod
    def switch_double_quota(cls, text, mode=1):
        # 假设我们有以下文本，我们想要替换掉引号
        # words = '"这是一个例子，引号需要被替换。"'

        # 使用正则表达式匹配双引号内的内容
        # 正则表达式解释：
        # (") 匹配前引号
        # (.*?) 非贪婪匹配任意字符，直到遇到第一个后引号
        # (") 匹配后引号
        pattern = r'(")(.*?)(")'

        # 替换引号
        # 我们使用一个函数来处理每个匹配项
        def replace_quotes(match):
            # match.group(1) 是第一个括号匹配的内容，即前引号
            # match.group(2) 是括号内的任意字符
            # match.group(3) 是第二个括号匹配的内容，即后引号
            # 这里我们用方括号[]来替换引号
            return f"“{match.group(2)}”"

        # 使用re.sub()函数进行替换
        replaced_text = re.sub(pattern, replace_quotes, text)
        return replaced_text

    @classmethod
    def switch_single_quota(cls, text, mode=1):
        if mode != 1:
            raise ValueError("模式不支持")

        import re

        # 假设我们有以下文本，我们想要替换掉引号
        # words = '"这是一个例子，引号需要被替换。"'

        # 使用正则表达式匹配双引号内的内容
        # 正则表达式解释：
        # (") 匹配前引号
        # (.*?) 非贪婪匹配任意字符，直到遇到第一个后引号
        # (") 匹配后引号
        pattern = r"(')(.*?)(')"

        # 替换引号
        # 我们使用一个函数来处理每个匹配项
        def replace_quotes(match):
            # match.group(1) 是第一个括号匹配的内容，即前引号
            # match.group(2) 是括号内的任意字符
            # match.group(3) 是第二个括号匹配的内容，即后引号
            # 这里我们用方括号[]来替换引号
            return f"‘{match.group(2)}’"

        # 使用re.sub()函数进行替换
        replaced_text = re.sub(pattern, replace_quotes, text)
        return replaced_text

    @classmethod
    def skip_blank_line(cls, text):
        import re
        pattern = r'(\n\s*)+'
        # 使用re.sub()替换空行为一个换行符
        return re.sub(pattern, '\n', text)


class ExcelPositionUtils:
    @classmethod
    def parse_excel_position(cls, excel_position: str) -> tuple:
        if not cls._validate_position(excel_position):
            raise ValueError("位置信息不合法")

        position_length = len(excel_position)
        column_letters = []
        line_no = []
        for i in range(position_length):
            if excel_position[i].isalpha():
                column_letters.append(excel_position[i])
            elif excel_position[i].isnumeric():
                line_no.append(excel_position[i])
        return "".join(column_letters), int("".join(line_no))

    @classmethod
    def _validate_position(cls, excel_position: str):
        ret = True
        if not excel_position or len(excel_position) < 2 or not excel_position[0].isalpha() or not excel_position[
            len(excel_position) - 1].isnumeric():
            # raise ValueError("位置信息不合法")
            ret = False
        return ret


class MACUtils:

    # @staticmethod
    # def get_mac_address():
    #     mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    #     return "-".join([mac[e:e + 2] for e in range(0, 11, 2)]).upper()

    @staticmethod
    def get_mac_address():
        node = uuid.getnode()
        mac = uuid.UUID(int=node).hex[-12:]
        return mac


class RSAUtils:

    @classmethod
    def create_rsa_key(cls):
        """
        创建RSA密钥
        步骤说明：
        1、从 Crypto.PublicKey 包中导入 RSA，创建一个密码
        2、生成 1024/2048 位的 RSA 密钥
        3、调用 RSA 密钥实例的 exportKey 方法，传入密码、使用的 PKCS 标准以及加密方案这三个参数。
        4、将私钥写入磁盘的文件。
        5、使用方法链调用 publickey 和 exportKey 方法生成公钥，写入磁盘上的文件。
        """

        # 伪随机数生成器
        random_gen = Random.new().read
        # 生成秘钥对实例对象：1024是秘钥的长度
        rsa = RSA.generate(1024, random_gen)

        # Server的秘钥对的生成
        private_pem = rsa.exportKey()
        with open("server_private.pem", "wb") as f:
            f.write(private_pem)

        public_pem = rsa.publickey().exportKey()
        with open("server_public.pem", "wb") as f:
            f.write(public_pem)

        # Client的秘钥对的生成
        # private_pem = rsa.exportKey()
        # with open("client_private.pem", "wb") as f:
        #     f.write(private_pem)
        #
        # public_pem = rsa.publickey().exportKey()
        # with open("client_public.pem", "wb") as f:
        #     f.write(public_pem)

    @classmethod
    # Server使用Client的公钥对内容进行rsa 加密
    def encrypt(cls, plaintext):
        """
        client 公钥进行加密
        plaintext:需要加密的明文文本，公钥加密，私钥解密
        """

        # 加载公钥
        rsa_key = RSA.import_key(open("client_public.pem").read())

        # 加密
        cipher_rsa = Cipher_PKC.new(rsa_key)
        en_data = cipher_rsa.encrypt(plaintext.encode("utf-8"))  # 加密

        # base64 进行编码
        base64_text = base64.b64encode(en_data)

        return base64_text.decode()  # 返回字符串

    @classmethod
    # Client使用自己的私钥对内容进行rsa 解密
    def decrypt(cls, en_data):
        """
        en_data:加密过后的数据，传进来是一个字符串
        """
        # base64 解码
        base64_data = base64.b64decode(en_data.encode("utf-8"))

        # 读取私钥
        private_key = RSA.import_key(open("client_private.pem").read())

        # 解密
        cipher_rsa = Cipher_PKC.new(private_key)
        data = cipher_rsa.decrypt(base64_data, None)

        return data.decode()

    @classmethod
    def signature(cls, data: str, server_private_key_path: str):
        """
         RSA私钥签名
         Server使用自己的私钥对内容进行签名
        :param data: 明文数据
        :param server_private_key_path: 服务端私钥路径
        :return: 签名后的字符串sign
        """
        with open(server_private_key_path) as f:
            # 读取私钥
            private_key = RSA.import_key(f.read())
        # 根据SHA256算法处理签名内容data
        sha_data = SHA256.new(data.encode("utf-8"))  # byte类型

        # 私钥进行签名
        signer = Signature_PKC.new(private_key)
        sign = signer.sign(sha_data)

        # 将签名后的内容，转换为base64编码
        sign_base64 = base64.b64encode(sign)
        return sign_base64.decode()

    @classmethod
    def verify(cls, data: str, signature_file_path: str, server_public_key_path: str):
        """
        RSA公钥验签
        Client使用Server的公钥对内容进行验签
        :param data: 明文数据
        :param signature_file_path: 签名文件路径
        :param server_public_key_path: 服务端公钥路径
        :return: 验签结果,布尔值
        """
        with open(signature_file_path, "r") as f:
            signature = f.read()

        with open(server_public_key_path, "r") as f:
            server_public_key = f.read()
        return cls._verify(data, signature, server_public_key)

    @classmethod
    def _verify(cls, data: str, signature: str, server_public_key: str) -> bool:
        """
        RSA公钥验签
        Client使用Server的公钥对内容进行验签
        :param data: 明文数据,签名之前的数据
        :param signature: 接收到的sign签名
        :param server_public_key: 服务端公钥
        :return: 验签结果,布尔值
        """
        # 接收到的sign签名 base64解码
        sign_data = base64.b64decode(signature.encode("utf-8"))
        # 加载公钥
        public_key = RSA.importKey(server_public_key)

        # 根据SHA256算法处理签名之前内容data
        sha_data = SHA256.new(data.encode("utf-8"))  # byte类型

        # 验证签名
        signer = Signature_PKC.new(public_key)
        is_verify = signer.verify(sha_data, sign_data)

        return is_verify


def gen_pri_key():
    # print(list(range(1, 11)))
    # mac_addr = "aca3687be2e6"
    mac_addr = "00e01bb46250"
    # mac_addr = "d4e98a126e10"
    # signature = RSAUtils.signature(f"文章抓取机器人{mac_addr}", "server_private.pem")
    # signature = RSAUtils.signature(f"直写机器人{mac_addr}", "server_private.pem")
    # signature = RSAUtils.signature(f"图片创作机器人（升级版）{mac_addr}", "server_private.pem")
    # signature = RSAUtils.signature(f"媒体下载器{mac_addr}", "server_private.pem")
    signature = RSAUtils.signature(f"媒体狩猎者{mac_addr}", "server_private.pem")
    # signature = RSAUtils.signature(f"betgoat{mac_addr}", "server_private.pem")
    with open("./signature.txt", "w", encoding="utf-8") as f:
        f.write(signature)


class ConfigFileReader:
    base_section_name = "Base"  # 基本配置分段名称
    busi_section_name = "Busi"  # 业务配置分段名称
    config_file_name = "config.ini"
    file_encode = "utf-8-sig"
    config_parser = configparser.RawConfigParser()
    config_file_dir = os.path.join(os.getcwd(), "config")
    config_file_full_path = os.path.join(config_file_dir, config_file_name)
    config_parser.read(config_file_full_path, encoding=file_encode)

    def __init__(self, *args):
        pass
        # 读取配置文件
        # self.load_config_file()

    # @staticmethod
    # def load_config_file():
    #     ConfigFileReader.config_parser.read(ConfigFileReader.config_file_full_path, encoding=ConfigFileReader.file_encode)

    @staticmethod
    def get_val(key, section_name="Base"):
        ret = None
        if ConfigFileReader.config_parser.has_section(ConfigFileReader.base_section_name):
            ret = ConfigFileReader.config_parser.get(section_name, key, fallback=None)
        return ret

    @staticmethod
    def set_val(key, value, section_name="Base"):
        if not ConfigFileReader.config_parser.has_section(section_name):
            ConfigFileReader.config_parser.add_section(section_name)
        ConfigFileReader.config_parser.set(section_name, key, value)
        with open(ConfigFileReader.config_file_full_path, "w", encoding=ConfigFileReader.file_encode) as f:
            ConfigFileReader.config_parser.write(f)

    @staticmethod
    def get_options(section_name) -> List:
        return ConfigFileReader.config_parser.options(section_name)


class QtLogRedirector(QThread):
    signal = pyqtSignal(str)

    # qt_log_redirector = QtLogRedirector()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(QtLogRedirector, "_instance"):
            QtLogRedirector._instance = QtLogRedirector(*args, **kwargs)
        return QtLogRedirector._instance

    def __init__(self, *args, **kwargs):
        super().__init__()
        # 备份标准输出
        self.saved_stdout = sys.stderr
        # 由该类输出
        sys.stderr = self

    def write(self, log_text):
        self.signal.emit(log_text)
        # print(log_text, file=sys.stdout, sep="")
        # if self.tb_log_info is not None:
        #     self.tb_log_info.append(log_text)
        #     self.tb_log_info.moveCursor(QTextCursor.End)

    def restore(self):
        sys.stderr = self.saved_stdout

    def flush(self):
        pass

    def create_logger(self, log_full_path_name: str, log_name=__name__, output_local_flag=True,
                      output_console_flag=True) -> logging.Logger:
        """
        创建日志类
        :param log_full_path_name:日志存放路径
        :param log_name:日志名，区分日志
        :param output_local_flag:True-输出到本地日志文件，路径由log_path_name指定；False-不输出到本地日志文件
        :param output_console_flag:True-输出到到控制台；False-不输出到控制台
        :return:logging.Logger对象
        """
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        if not logger.hasHandlers():
            log_format = '[%(asctime)s][%(levelname)s]%(module)s:%(lineno)s-%(message)s'
            formatter = logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")
            if output_local_flag:
                # 根据文件大小来滚动日志，100M一个文件
                file_handler = RotatingFileHandler(log_full_path_name, "a", 100 * 1024 * 1024, 5, encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            if output_console_flag:
                # logging.StreamHandler.terminator = ""
                console_handler = logging.StreamHandler()
                # console_handler.terminator = ""
                # 控制台输出INFO级别及以上的日志
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
        return logger


def create_path_if_not_exit(cur_path: str) -> str:
    if not os.path.exists(cur_path):
        os.mkdir(cur_path)
    return cur_path


LOG = QtLogRedirector.instance().create_logger(
    os.path.join(create_path_if_not_exit(cur_path=os.path.join(os.getcwd(), "logs")),
                 "user_score_log.log"),
    output_local_flag=True if ConfigFileReader.get_val(Constants.ConfigFileKey.LOG_LOCAL_FLAG,
                                                       section_name=ConfigFileReader.base_section_name) != "0" else False,
    output_console_flag=True)

logger = LOG
# logger = init_loging_config()


def release():
    LOG.info("退出前释放资源")
    cur_pid = os.getpid()
    if os.name == "nt":
        cmd = "taskkill /f /t /pid %s" % cur_pid
        LOG.info("执行命令：%s杀死所有相关进程" % cmd)
        os.system(cmd)
    elif os.name == "posix":
        child_processes: List[psutil.Process] = list()
        get_child_processes(cur_pid, child_processes)
        if len(child_processes) > 0:
            for child_process in child_processes:
                if psutil.pid_exists(child_process.pid):
                    LOG.info("杀死子进程：%s，进程ID：%d，父进程ID：%d" % (
                        child_process.name(), child_process.pid, child_process.ppid()))
                    cmd = "kill -9 %s" % child_process.pid
                    os.system(cmd)
