"""
媒体狩猎者
"""
import atexit
import functools
import os
import re
import sys
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor, QColor
from PyQt5.QtWidgets import QWidget, QGroupBox, QPushButton, QLineEdit, QFileDialog, QHBoxLayout, QLabel, QVBoxLayout, \
    QGridLayout, QTextBrowser, QMessageBox, QApplication, QGraphicsDropShadowEffect, \
    QComboBox

from base.base_crawler import InterfaceParams, Platform, LoginType, CrawlerType, SaveDataOption, DownloadScope
from constants import Constants
from main import CrawlerBusiHandler
from tools.utils import MACUtils, RSAUtils, QtLogRedirector, ConfigFileReader, release


class ShadowButton(QPushButton):
    def __init__(self, text, parent=None):
        super(ShadowButton, self).__init__(text, parent)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.red)
        shadow.setOffset(2, 2)
        self.setGraphicsEffect(shadow)

    #     self.default_color = self.palette().color(QPalette.Button)
    #     self.clicked.connect(self.toggle_color)
    #
    # def toggle_color(self):
    #     # 切换按钮颜色
    #     if self.palette().color(QPalette.Button) == self.default_color:
    #         self.setPalette(QPalette(QColor('lightgray')))
    #     else:
    #         self.setPalette(QPalette(self.default_color))


class MediaCrawlerInterface(QWidget):
    signal = pyqtSignal(bool)

    def __init__(self, media_crawler_busi_handler: CrawlerBusiHandler):
        super().__init__(flags=Qt.MSWindowsFixedSizeDialogHint)
        self.xhs_download_scope = DownloadScope.CURRENT
        self.cb_xhs_download_scope = None

        self.cb_xhs_save_watermark_origin_image = None
        self.xhs_save_watermark_origin_image = None
        self.cb_xhs_cover_watermark = None
        self.xhs_cover_watermark_flag = None
        self.enable_proxy = None
        self.le_download_dir = None
        self.cb_save_local_flag = None
        self.save_local_flag = None
        self.btn_active = None
        self.btn_copy = None
        self.mac_label = None
        self.btn_startup = None
        self.le_url_info_end_cell = None
        self.le_url_info_start_cell = None
        self.le_sheet_name = None
        self.btn_open_file = None
        self.le_url_info_file_path = None
        self.log_info_text_browser = None
        self.gb_configure = QGroupBox("配置信息")
        self.gb_log_info = QGroupBox("日志")
        self.media_crawler_busi_handler = media_crawler_busi_handler
        self.media_crawler_busi_handler.reset_buttons_signal.connect(self.reset_btn)

        self.cb_proxy_mode = None
        self.cb_get_sub_comments = None
        self.cb_get_comments = None
        self.le_start_page = None
        self.get_sub_comments_flag = False
        self.get_comments_flag = False
        self.cb_crawler_type = None
        self.cb_login_type = None
        self.cb_save_data_option = None
        self.save_data_option = None
        self.login_type = None
        self.crawler_type = None
        self.le_file_save_dir = None
        self.le_keywords = None
        self.le_cookies = None
        self.cb_platform = None
        self.platform = None
        self.content_color: Optional[QColor] = None
        self.title_color: Optional[QColor] = None
        self.btn_update_content_info = None
        self.lb_content_total_word_count = None
        self.lb_content_predict_word_count_per_line = None
        self.lb_content_predict_line_count = None
        self.le_content_paragraph_spacing = None
        self.le_content_line_spacing = None
        self.btn_choose_content_color = None
        self.f_content_color_show = None
        self.le_content_font_size = None
        self.cb_content_start_y_follow = None
        self.le_content_start_y = None
        self.le_content_start_x = None
        self.btn_choose_title_color = None
        self.f_title_color_show = None
        self.le_title_font_size = None
        self.le_title_start_y = None
        self.le_title_start_x = None
        # 日志重定向器
        self.qt_log_redirector = QtLogRedirector.instance()
        # 绑定日志重定向器
        self.qt_log_redirector.signal.connect(self.update_text_browser)
        # 初始化基础UI元素
        self._init_common_ui_elements()
        # 编排公共的ui
        self.ly_mac, self.ly_file_path, self.ly_sheet_name, self.ly_article_info, self.ly_tips = self._arrange_common_ui()
        # 初始化自定义UI元素
        self._init_custom_ui_elements()
        # 编排自定义的ui
        self.ly_custom_ui = self._arrage_custom_ui()

        # 编排主界面ui
        self._arrange_main_ui(self.ly_mac, self.ly_file_path, self.ly_sheet_name, self.ly_article_info, self.ly_tips,
                              self.ly_custom_ui)

    def _arrange_main_ui(self, *layouts):
        # 设置配置信息分组的布局
        ly_configure = QVBoxLayout()
        if layouts:
            for layout in layouts:
                ly_configure.addLayout(layout)
        # ly_configure.addLayout(self.ly_mac)
        # ly_configure.addLayout(self.ly_file_path)
        # ly_configure.addLayout(self.ly_sheet_name)
        # ly_configure.addLayout(self.ly_article_info)
        # ly_configure.addLayout(self.ly_custom_ui)
        self.gb_configure.setLayout(ly_configure)

        # 设置日志信息的布局
        ly_log_info = QHBoxLayout()
        ly_log_info.addWidget(self.log_info_text_browser)
        self.gb_log_info.setLayout(ly_log_info)

        main_window_layout = QVBoxLayout()
        main_window_layout.addWidget(self.gb_configure)
        main_window_layout.addWidget(self.gb_log_info)
        main_window_layout.setStretch(0, 1)
        main_window_layout.setStretch(1, 5)

        self.setLayout(main_window_layout)
        self.setFixedSize(1000, 1200)

        activate_status = ConfigFileReader.get_val(Constants.ConfigFileKey.ACTIVATE_STATUS)
        title = f"{self.get_title()}（未激活）"
        if activate_status == "1" and os.path.exists("signature.txt"):
            # 签名文件存在
            title = f"{self.get_title()}（已激活）"

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(self.get_icon()))

    def _arrange_common_ui(self):
        # 编排公众的ui
        #### mac ui ####
        ly_mac = QHBoxLayout()
        ly_mac.setAlignment(Qt.AlignLeft)
        ly_mac.addWidget(QLabel("识 别 码："))

        # mac地址
        ly_mac.addWidget(self.mac_label)
        ly_mac.addWidget(self.btn_copy)
        ly_mac.addWidget(self.btn_active)

        #### 文件ui ####
        ly_file_path = QHBoxLayout()
        ly_file_path.addWidget(QLabel("URL文件："))
        ly_file_path.addWidget(self.le_url_info_file_path)
        ly_file_path.addWidget(self.btn_open_file)

        #### 表格名称ui ####
        ly_sheet_name = QHBoxLayout()
        ly_sheet_name.addWidget(QLabel("表格名称："))
        ly_sheet_name.addWidget(self.le_sheet_name)

        #### 数据ui ####
        ly_article_info = QGridLayout()
        ly_article_info.addWidget(QLabel("URL列表："), 0, 0)
        ly_article_info.addWidget(self.le_url_info_start_cell, 0, 1)
        ly_article_info.addWidget(QLabel(":"), 0, 2)
        ly_article_info.addWidget(self.le_url_info_end_cell, 0, 3)
        ly_article_info.addWidget(self.btn_startup, 0, 4)

        #### 提示内容ui ###
        ly_tips = QVBoxLayout()
        lb_tips = QLabel('至少需要选取1列【小红薯地址】')
        lb_tips.setStyleSheet("QLabel { color: red; }")  # 设置字体颜色为红色
        ly_tips.addWidget(lb_tips)

        return ly_mac, ly_file_path, ly_sheet_name, ly_article_info, ly_tips

    def _init_common_ui_elements(self):
        # 重定向日志信息
        # 日志信息输出到该位置
        self.log_info_text_browser = QTextBrowser()
        self.log_info_text_browser.document().setMaximumBlockCount(1000)

        self.le_url_info_file_path = QLineEdit()
        self.le_url_info_file_path.setPlaceholderText("小红薯目标笔记xlsx")

        self.btn_open_file = QPushButton("打开文件")
        self.btn_open_file.clicked.connect(self._open_file)

        self.le_sheet_name = QLineEdit()
        self.le_sheet_name.setText(ConfigFileReader.get_val(Constants.ConfigFileKey.WORKSHEET_NAME))

        self.le_url_info_start_cell = QLineEdit(
            ConfigFileReader.get_val(Constants.ConfigFileKey.ARTICLE_INFO_START_CELL_POSITION))
        self.le_url_info_start_cell.setPlaceholderText("起始单元格，例如A1")
        self.le_url_info_end_cell = QLineEdit(
            ConfigFileReader.get_val(Constants.ConfigFileKey.ARTICLE_INFO_END_CELL_POSITION))
        self.le_url_info_end_cell.setPlaceholderText("截止单元格，例如A20")

        self.btn_startup = ShadowButton("行动")
        self.btn_startup.clicked.connect(self._startup)

        self.mac_label = QLabel(MACUtils.get_mac_address())
        self.btn_copy = QPushButton("复制")
        self.btn_copy.clicked.connect(self.copy_text)
        self.btn_active = QPushButton("激活")
        self.btn_active.clicked.connect(self.active)

    def _arrage_custom_ui(self):
        ly_config_1 = QGridLayout()
        ly_config_1.addWidget(QLabel("平台："), 0, 0)
        ly_config_1.addWidget(self.cb_platform, 0, 1)
        ly_config_1.addWidget(QLabel("狩猎方式："), 0, 2)
        ly_config_1.addWidget(self.cb_crawler_type, 0, 3)
        ly_config_1.addWidget(QLabel("登录方式："), 0, 4)
        ly_config_1.addWidget(self.cb_login_type, 0, 5)
        ly_config_1.addWidget(QLabel("直存本地："), 0, 6)
        ly_config_1.addWidget(self.cb_save_local_flag, 0, 7)

        ly_config_1.addWidget(QLabel("获取评论："), 1, 0)
        ly_config_1.addWidget(self.cb_get_comments, 1, 1)
        ly_config_1.addWidget(QLabel("获取子评论："), 1, 2)
        ly_config_1.addWidget(self.cb_get_sub_comments, 1, 3)
        ly_config_1.addWidget(QLabel("存储方式："), 1, 4)
        ly_config_1.addWidget(self.cb_save_data_option, 1, 5)
        ly_config_1.addWidget(QLabel("起始页："), 1, 6)
        ly_config_1.addWidget(self.le_start_page, 1, 7)
        ly_config_1.addWidget(QLabel("开启代理："), 2, 0)
        ly_config_1.addWidget(self.cb_proxy_mode, 2, 1)
        ly_config_1.addWidget(QLabel("xhs去水印："), 2, 2)
        ly_config_1.addWidget(self.cb_xhs_cover_watermark, 2, 3)
        ly_config_1.addWidget(QLabel("xhs保留原图："), 2, 4)
        ly_config_1.addWidget(self.cb_xhs_save_watermark_origin_image, 2, 5)
        ly_config_1.addWidget(QLabel("下载范围："), 2, 6)
        ly_config_1.addWidget(self.cb_xhs_download_scope, 2, 7)

        ly_config_2 = QVBoxLayout()

        ly_config_2_1 = QHBoxLayout()
        ly_config_2_1.addWidget(QLabel("搜索关键词："))
        ly_config_2_1.addWidget(self.le_keywords)

        ly_config_2_2 = QHBoxLayout()
        ly_config_2_2.addWidget(QLabel("cookie："))
        ly_config_2_2.addWidget(self.le_cookies)

        ly_config_2_3 = QHBoxLayout()
        ly_config_2_3.addWidget(QLabel("数据文件保存目录："))
        ly_config_2_3.addWidget(self.le_file_save_dir)

        ly_config_2_4 = QHBoxLayout()
        ly_config_2_4.addWidget(QLabel("本地下载目录："))
        ly_config_2_4.addWidget(self.le_download_dir)

        ly_config_2.addLayout(ly_config_2_1)
        ly_config_2.addLayout(ly_config_2_2)
        ly_config_2.addLayout(ly_config_2_3)
        ly_config_2.addLayout(ly_config_2_4)
        ly_config = QVBoxLayout()
        ly_config.addLayout(ly_config_1)
        ly_config.addLayout(ly_config_2)
        return ly_config

    def _init_custom_ui_elements(self):
        self.le_keywords = QLineEdit()
        self.le_keywords.setPlaceholderText("搜索关键词，多个关键词以,分割")
        self.le_cookies = QLineEdit(ConfigFileReader.get_val(Constants.ConfigFileKey.MC_COOKIE))
        self.le_cookies.setPlaceholderText("cookie串，选择cookie登录必填")

        self.le_file_save_dir = QLineEdit()
        self.le_file_save_dir.setPlaceholderText("csv、json文件存储目录，存储方式为csv、json时必填")

        self.le_download_dir = QLineEdit(ConfigFileReader.get_val(Constants.ConfigFileKey.DM2L_DOWNLOAD_DIR))
        self.le_download_dir.setPlaceholderText("直存本地时必填")

        self.cb_platform = QComboBox()
        self.cb_platform.addItem("小红薯", Platform.XHS)
        self.cb_platform.addItem("百度贴吧", Platform.TIEBA)
        self.cb_platform.addItem("抖音", Platform.DY)
        self.cb_platform.addItem("快手", Platform.KS)
        self.cb_platform.addItem("知乎", Platform.ZHIHU)
        self.cb_platform.addItem("哔哩哔哩", Platform.BILI)
        # 当选项改变时调用的方法
        self.cb_platform.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_platform))
        self.cb_platform.setCurrentIndex(0)
        self.platform = Platform.XHS

        self.cb_login_type = QComboBox()
        self.cb_login_type.addItem("cookie", LoginType.COOKIE)
        self.cb_login_type.addItem("二维码", LoginType.QRCODE)
        self.cb_login_type.addItem("手机号", LoginType.MOBILE)
        # 当选项改变时调用的方法
        self.cb_login_type.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_login_type))
        self.cb_login_type.setCurrentIndex(0)
        self.login_type = LoginType.COOKIE

        self.cb_save_local_flag = QComboBox()
        self.cb_save_local_flag.addItem("是", True)
        self.cb_save_local_flag.addItem("否", False)
        # 当选项改变时调用的方法
        self.cb_save_local_flag.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_save_local_flag))
        self.cb_save_local_flag.setCurrentIndex(0)
        self.save_local_flag = True

        self.cb_crawler_type = QComboBox()
        self.cb_crawler_type.addItem("指定ID", CrawlerType.DETAIL)
        self.cb_crawler_type.addItem("关键词搜索", CrawlerType.SEARCH)
        self.cb_crawler_type.addItem("创作者主页", CrawlerType.CREATOR)
        # 当选项改变时调用的方法
        self.cb_crawler_type.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_crawler_type))
        self.cb_crawler_type.setCurrentIndex(0)
        self.crawler_type = CrawlerType.DETAIL

        self.cb_save_data_option = QComboBox()
        self.cb_save_data_option.addItem("数据库", SaveDataOption.DB)
        self.cb_save_data_option.addItem("csv文本", SaveDataOption.CSV)
        self.cb_save_data_option.addItem("json文本", SaveDataOption.JSON)
        # 当选项改变时调用的方法
        self.cb_save_data_option.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_save_data_option))
        self.cb_save_data_option.setCurrentIndex(0)
        self.save_data_option = SaveDataOption.DB

        self.le_start_page = QLineEdit("1")

        self.cb_get_comments = QComboBox()
        self.cb_get_comments.addItem("否", False)
        self.cb_get_comments.addItem("是", True)
        # 当选项改变时调用的方法
        self.cb_get_comments.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_get_comments_flag))
        self.cb_get_comments.setCurrentIndex(0)
        self.get_comments_flag = False

        self.cb_get_sub_comments = QComboBox()
        self.cb_get_sub_comments.addItem("否", False)
        self.cb_get_sub_comments.addItem("是", True)
        # 当选项改变时调用的方法
        self.cb_get_sub_comments.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_get_sub_comments_flag))
        self.cb_get_sub_comments.setCurrentIndex(0)
        self.get_sub_comments_flag = False

        self.cb_proxy_mode = QComboBox()
        self.cb_proxy_mode.addItem("是", True)
        self.cb_proxy_mode.addItem("否", False)
        self.cb_proxy_mode.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_proxy_mode))
        self.cb_proxy_mode.setCurrentIndex(0)
        self.enable_proxy = True

        self.cb_xhs_cover_watermark = QComboBox()
        self.cb_xhs_cover_watermark.addItem("是", True)
        self.cb_xhs_cover_watermark.addItem("否", False)
        self.cb_xhs_cover_watermark.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_xhs_cover_watermark_flag))
        self.cb_xhs_cover_watermark.setCurrentIndex(0)
        self.xhs_cover_watermark_flag = True

        self.cb_xhs_save_watermark_origin_image = QComboBox()
        self.cb_xhs_save_watermark_origin_image.addItem("否", False)
        self.cb_xhs_save_watermark_origin_image.addItem("是", True)
        self.cb_xhs_save_watermark_origin_image.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_xhs_save_watermark_origin_image))
        self.cb_xhs_save_watermark_origin_image.setCurrentIndex(0)
        self.xhs_save_watermark_origin_image = False

        self.cb_xhs_download_scope = QComboBox()
        self.cb_xhs_download_scope.addItem("当前", DownloadScope.CURRENT)
        self.cb_xhs_download_scope.addItem("所有", DownloadScope.ALL)
        self.cb_xhs_download_scope.currentIndexChanged.connect(
            functools.partial(self.on_current_index_changed, self.set_xhs_download_scope))
        self.cb_xhs_download_scope.setCurrentIndex(0)
        self.xhs_download_scope = DownloadScope.CURRENT

    def set_xhs_download_scope(self, index):
        self.xhs_download_scope = self.cb_xhs_download_scope.itemData(index)

    def set_xhs_save_watermark_origin_image(self, index):
        self.xhs_save_watermark_origin_image = self.cb_xhs_save_watermark_origin_image.itemData(index)

    def set_xhs_cover_watermark_flag(self, index):
        self.xhs_cover_watermark_flag = self.cb_xhs_cover_watermark.itemData(index)

    def set_proxy_mode(self, index):
        self.enable_proxy = self.cb_proxy_mode.itemData(index)

    def set_platform(self, index):
        self.platform = self.cb_platform.itemData(index)

    def set_crawler_type(self, index):
        self.crawler_type = self.cb_crawler_type.itemData(index)

    def set_save_local_flag(self, index):
        self.save_local_flag = self.cb_save_local_flag.itemData(index)

    def set_login_type(self, index):
        self.login_type = self.cb_login_type.itemData(index)

    def set_save_data_option(self, index):
        self.save_data_option = self.cb_save_data_option.itemData(index)

    def set_get_comments_flag(self, index):
        self.get_comments_flag = self.cb_get_comments.itemData(index)

    def set_get_sub_comments_flag(self, index):
        self.get_sub_comments_flag = self.cb_get_sub_comments.itemData(index)

    def on_current_index_changed(self, callback_method, index):
        callback_method(index)

    def reset_btn(self, flag: bool):
        self.btn_startup.setEnabled(True)
        self.btn_startup.setText("行动")
        self.btn_open_file.setEnabled(True)
        self.le_url_info_start_cell.setEnabled(True)
        self.le_url_info_end_cell.setEnabled(True)
        self.le_sheet_name.setEnabled(True)

    def active(self):
        """
        激活
        :return:
        """
        # 打开文件
        # 选择文件
        # 读取文件
        file_path, filter = QFileDialog.getOpenFileName(self, "打开秘钥", "c:", "格式 (*.txt)")
        if file_path:
            # 复制文件到当前路径
            signature_file_path = os.path.join(os.getcwd(), "signature.txt")
            with open(file_path, "rb") as source_file:
                with open(signature_file_path, "wb") as target_file:
                    target_file.write(source_file.read())

            try:
                # 激活
                if RSAUtils.verify(f"{self.get_signature_prefix()}{self.mac_label.text()}", signature_file_path,
                                   os.path.join(os.getcwd(), "server_public.pem")):
                    # 激活成功
                    # 弹出消息框提示激活成功
                    QMessageBox.information(self, "信息", "激活成功", QMessageBox.Ok)
                    if ConfigFileReader.get_val(Constants.ConfigFileKey.ACTIVATE_STATUS) == "0":
                        ConfigFileReader.set_val(Constants.ConfigFileKey.ACTIVATE_STATUS, "1")

                    self.setWindowTitle(f"{self.get_title()}（已激活）")
                else:
                    QMessageBox.information(self, "警告", "激活失败", QMessageBox.Ok)
                    self.setWindowTitle(f"{self.get_title()}（未激活）")
            except:
                # 激活失败
                QMessageBox.information(self, "警告", "激活失败", QMessageBox.Ok)

    def copy_text(self):
        # 获取剪贴板
        clipboard = QApplication.clipboard()
        # 设置剪贴板文本内容
        clipboard.setText(self.mac_label.text())
        # 弹出消息框提示复制成功
        QMessageBox.information(self, '信息', '文本已复制到剪贴板', QMessageBox.Ok)

    def _open_file(self):
        path = ConfigFileReader.get_val(Constants.ConfigFileKey.DATA_FILE_DIR)
        if path is None:
            path = os.getcwd()
        file_path, filter = QFileDialog.getOpenFileName(self, "打开文件", path, "格式 (*.xlsx)")
        if file_path:
            ConfigFileReader.set_val(Constants.ConfigFileKey.DATA_FILE_DIR,
                                     file_path[0:(file_path.rindex("/") + 1)])
            self.le_url_info_file_path.setText(file_path)

    def _is_active(self) -> bool:
        return True if ConfigFileReader.get_val(Constants.ConfigFileKey.ACTIVATE_STATUS) == "1" and RSAUtils.verify(
            f"{self.get_signature_prefix()}{self.mac_label.text()}", "signature.txt", "server_public.pem") else False

    def _manual_startup(self):
        self.media_crawler_busi_handler.startup_flag = True
        self.btn_startup.setEnabled(False)

    def _on_recursive_mode_toggled(self, is_checked):
        self.recursive_mode = True if is_checked else False
        # if is_checked:
        #     print("Checkbox is checked")
        # else:
        #     print("Checkbox is unchecked")

    def _startup(self):
        """
        开始学习
        :return:
        """
        try:
            if not self._is_active():
                QMessageBox.warning(self, "警告", "未激活，联系管理员激活！", QMessageBox.Ok)
                self.setWindowTitle(f"{self.get_title()}（未激活）")
                return
        except Exception as e:
            QMessageBox.warning(self, "警告", "未激活，联系管理员激活！", QMessageBox.Ok)
            self.setWindowTitle(f"{self.get_title()}（未激活）")
            return

        if self._check_params():
            # 保存参数
            self._save_params()
            # 参数合格了
            self.btn_startup.setText("运行中...")
            self.enabled_widget(False)
            self.log_info_text_browser.clear()

            interface_params = InterfaceParams(xlsx_path=self.le_url_info_file_path.text(),
                                               sheet_name=self.le_sheet_name.text(),
                                               url_info_start_cell=self.le_url_info_start_cell.text(),
                                               url_info_end_cell=self.le_url_info_end_cell.text(),
                                               keywords=self.le_keywords.text(),
                                               cookies=self.le_cookies.text(),
                                               platform=self.platform,
                                               login_type=self.login_type,
                                               crawler_type=self.crawler_type,
                                               start_page=int(self.le_start_page.text()),
                                               enable_get_comments=self.get_comments_flag,
                                               enable_get_sub_comments=self.get_sub_comments_flag,
                                               save_data_option=self.save_data_option,
                                               file_save_dir=self.le_file_save_dir.text(),
                                               save_local_flag=self.save_local_flag,
                                               download_dir=self.le_download_dir.text(),
                                               enable_proxy=self.enable_proxy,
                                               xhs_cover_watermark=self.xhs_cover_watermark_flag,
                                               xhs_save_watermark_origin_image=self.xhs_save_watermark_origin_image,
                                               xhs_download_scope=self.xhs_download_scope
                                               )
            self.media_crawler_busi_handler.interface_params = interface_params
            self.media_crawler_busi_handler.start()

    def _save_params(self):
        ConfigFileReader.set_val(Constants.ConfigFileKey.WORKSHEET_NAME, self.le_sheet_name.text())
        ConfigFileReader.set_val(Constants.ConfigFileKey.ARTICLE_INFO_START_CELL_POSITION,
                                 self.le_url_info_start_cell.text())
        ConfigFileReader.set_val(Constants.ConfigFileKey.ARTICLE_INFO_END_CELL_POSITION,
                                 self.le_url_info_end_cell.text())

        if self.login_type == LoginType.COOKIE:
            ConfigFileReader.set_val(Constants.ConfigFileKey.MC_COOKIE,
                                     self.le_cookies.text())
        if self.save_local_flag:
            ConfigFileReader.set_val(Constants.ConfigFileKey.DM2L_DOWNLOAD_DIR, self.le_download_dir.text())

    def enabled_widget(self, status):
        self.btn_startup.setEnabled(status)
        self.le_url_info_start_cell.setEnabled(status)
        self.le_url_info_end_cell.setEnabled(status)
        self.btn_open_file.setEnabled(status)
        self.le_sheet_name.setEnabled(status)

    def update_text_browser(self, text):
        self.log_info_text_browser.append(text)
        self.log_info_text_browser.moveCursor(QTextCursor.End)

    def update_progress(self):
        # print("结束")
        self.btn_startup.setText("打开网址")
        self.enabled_widget(True)

    def is_cell_input_legal(self, input_text: str):
        ret = False
        if input_text is not None and isinstance(input_text, str) and len(input_text) > 0:
            pattern = "^[a-zA-Z]+[1-9][0-9]*$"
            if re.match(pattern, input_text):
                ret = True
        return ret

    def _check_params(self):
        error_desc = ""
        ret = True
        if self.crawler_type == CrawlerType.DETAIL:
            if not self.le_url_info_file_path.text().strip():
                # 弹窗警告
                error_desc = "excel路径不能为空"
            elif not self.le_sheet_name.text().strip():
                # 弹窗警告
                error_desc = "表格名称不能为空"
            elif not self.is_cell_input_legal(self.le_url_info_start_cell.text().strip()):
                # 弹窗警告
                error_desc = "起始位置输入格式有误"
            elif not self.is_cell_input_legal(self.le_url_info_end_cell.text().strip()):
                # 弹窗警告
                error_desc = "截止位置输入格式有误"

        if self.login_type == LoginType.COOKIE and not self.le_cookies.text().strip():
            error_desc = "cookie不能为空"
        if (
                self.crawler_type == CrawlerType.SEARCH or self.crawler_type == CrawlerType.CREATOR) and not self.le_start_page.text().isdigit():
            error_desc = "起始页输入有误"
        if self.crawler_type == CrawlerType.SEARCH and not self.le_keywords.text().strip():
            error_desc = "关键词输入有误"
        if self.save_data_option in (SaveDataOption.CSV, SaveDataOption.JSON) and (
                not self.le_file_save_dir.text().strip() or not os.path.exists(self.le_file_save_dir.text().strip())):
            error_desc = "文件保存目录有误"

        if self.save_local_flag and (
                not self.le_download_dir.text().strip() or not os.path.exists(self.le_download_dir.text().strip())):
            error_desc = "本地下载目录有误"

        if error_desc:
            QMessageBox.critical(self, "输入错误", error_desc, QMessageBox.Yes)
            ret = False
        return ret

    def get_title(self):
        return "媒体狩猎者V1.0.2"

    def get_icon(self):
        return "media_crawler.ico"

    def get_signature_prefix(self) -> str:
        return "媒体狩猎者"


if __name__ == "__main__":
    try:
        atexit.register(release)
        app = QApplication([])
        main_window = MediaCrawlerInterface(CrawlerBusiHandler())
        main_window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(e)
    finally:
        # 释放资源
        pass
