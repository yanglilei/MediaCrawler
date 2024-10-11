import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import emoji
import pymysql
import requests
import strgen

from base.base_crawler import DownloadScope, Platform
from config.base_config import BaseConfig
from constants import Constants
from proxy import IpInfoModel
from proxy.proxy_ip_pool import create_ip_pool
from tools import watermark_utils
from tools.utils import ConfigFileReader, ArticleFormatterUtils, LOG


class XHSNoteDownloader:
    def __init__(self, save_dir, db_config: dict, default_content_file_name="1.txt"):
        """
        初始化小红书笔记下载到本地类
        :param save_dir: 笔记保存的根目录
        :param db_config: 数据库配置
            参数例子：
            {"host": "localhost", "port": 3306,
             "user": "root", "password": "ying*#1234",
             "database": "media_crawler", "charset": "utf8mb4"}
             host: 主机
             port： 端口
             user: 用户名
             password：密码
             database: 数据库
             charset: 字符集

        :param default_content_file_name: 笔记内容文件的默认名称
        """
        # 笔记保存的根目录
        self.save_dir = save_dir
        # 数据库配置
        self.db_config = db_config
        self.default_content_file_name = default_content_file_name
        self.rest_interval = float(ConfigFileReader.get_val(Constants.ConfigFileKey.DM2L_IMG_DOWNLOAD_INTERVAL))

    def _make_save_dir(self, title) -> str:
        title = ArticleFormatterUtils.format_title(self._format_title_ignore_emoji(title))
        if Path(self.save_dir).joinpath(title).exists():
            # 目录已经存在，说明不同的笔记标题相同，需要重新命名
            title = f"{title}_{strgen.StringGenerator('[a-zA-Z0-9]{8}').render()}"
        base_dir = str(Path(self.save_dir).joinpath(title))
        os.makedirs(base_dir)
        return base_dir

    async def save_local(self):
        """
        保存到本地
        """
        records = self.query_note_info_from_db(*BaseConfig.XHS_SPECIFIED_ID_LIST if BaseConfig.XHS_DOWNLOAD_SCOPE==DownloadScope.CURRENT else "")
        if not records:
            LOG.info("没有需要保存的内容！")
        else:
            download_local_infos = []
            for record in records:
                download_local_info = {"id": 0, "download_local_flag": 1, "save_dir": ""}
                title = record[0]
                content = record[1]
                image_str = record[2]
                download_local_info["id"] = record[3]
                # ids.append(record[3])

                try:
                    save_dir = self._make_save_dir(title)
                    download_local_info["save_dir"] = save_dir
                    # 保存图片
                    await self.download_note_image(image_str.split(","), title, save_dir)
                    # 保存标题和正文
                    self.save_title_and_content(title, content, save_dir)
                except Exception as e:
                    LOG.exception(f"id={record[3]}【{title}】保存本地失败！")
                else:
                    LOG.info(f"id={record[3]}【{title}】整套内容保存成功！")
                    download_local_infos.append(download_local_info)

            self.update_download_local_info(download_local_infos)
            LOG.info(f"更新数据库下载本地标志为1，共【{len(download_local_infos)}】条数据！")

    def save_title_and_content(self, title, content, save_dir):
        save_file = os.path.join(save_dir, self.default_content_file_name)
        with open(save_file, "w", encoding="utf-8") as f:
            f.write(f"# {title}")
            f.write("\n")
            f.write("\n")
            if content:
                f.write(content)
            LOG.info(f"【{title}】的文本，保存成功！")

    def query_note_info_from_db(self, *xhs_note_ids):
        """
        获取笔记信息
        :return: (标题, 正文, 图片)，多张图片用,分割
        """
        ret = []
        query_stm = "select title, `desc`, image_list, id from xhs_note where download_local_flag=0"

        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                if xhs_note_ids:
                    if len(xhs_note_ids) == 1:
                        query_stm = f"{query_stm} and note_id=%s"
                        cursor.execute(query_stm, (xhs_note_ids[0],))
                    else:
                        query_stm = f"{query_stm} and note_id in %s"
                        cursor.execute(query_stm, (xhs_note_ids,))
                else:
                    cursor.execute(query_stm)
                ret.extend(cursor.fetchall())
                return ret
        finally:
            if conn:
                conn.close()

    def update_download_local_info(self, download_local_infos: List[Dict]):
        if download_local_infos:
            conn = None
            try:
                conn = pymysql.connect(**self.db_config)
                with conn.cursor() as cursor:
                    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    download_local_infos = [(1, info["save_dir"], update_time, info["id"]) for info in download_local_infos]

                    update_stm = "update xhs_note set download_local_flag=%s, save_dir=%s, update_time=%s where id=%s"

                    cursor.executemany(update_stm, download_local_infos)

                    # if len(ids) > 1:
                    #     query_stm = "update xhs_note set download_local_flag=%s, save_dir=%s, update_time=%s where id in %s"
                    #     id_val = ids
                    # else:
                    #     query_stm = "update xhs_note set download_local_flag=%s, save_dir=%s, update_time=%s where id=%s"
                    #     id_val = ids[0]
                    # cursor.execute(query_stm,
                    #                (download_local_flag, save_dir, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    #                 id_val))
            finally:
                if conn:
                    conn.commit()
                    conn.close()

    @staticmethod
    def format_proxy_info(ip_proxy_info: IpInfoModel) -> dict[str, str]:
        """format proxy info for httpx"""
        httpx_proxy = {
            f"{ip_proxy_info.protocol}": f"http://{ip_proxy_info.user}:{ip_proxy_info.password}@{ip_proxy_info.ip}:{ip_proxy_info.port}"
        }
        return httpx_proxy

    async def download_note_image(self, image_list: list, note_title, save_dir):
        if image_list:
            if BaseConfig.ENABLE_IP_PROXY:
                ip_proxy_pool = await create_ip_pool(BaseConfig.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
                ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
                httpx_proxy_format = self.format_proxy_info(ip_proxy_info)
            else:
                httpx_proxy_format = {}

            for idx, image_url in enumerate(image_list):
                result = requests.get(url=image_url.strip(), proxies=httpx_proxy_format)
                time.sleep(self.rest_interval)
                with open(os.path.join(save_dir, f"{idx + 1}.jpg"), "wb") as f:
                    f.write(result.content)
                LOG.info(f"【{note_title}】图片：{idx + 1}.jpg，保存成功！")

    def _format_title_ignore_emoji(self, title):
        if title:
            for char in title:
                if emoji.is_emoji(char):
                    title = title.replace(char, "")
        return title


def localize(original_function):
    """
    本地化处理
    :param original_function:
    :return:
    """
    async def _save_local(save_dir):
        try:
            LOG.info("开始保存到本地...")
            if BaseConfig.PLATFORM == Platform.XHS.value:
                d2l = XHSNoteDownloader(save_dir, {"host": ConfigFileReader.get_val(Constants.ConfigFileKey.DM2L_HOST),
                                                   "port": int(
                                                       ConfigFileReader.get_val(Constants.ConfigFileKey.DM2L_PORT)),
                                                   "user": ConfigFileReader.get_val(Constants.ConfigFileKey.DM2L_USER),
                                                   "password": ConfigFileReader.get_val(
                                                       Constants.ConfigFileKey.DM2L_PASSWORD),
                                                   "database": ConfigFileReader.get_val(
                                                       Constants.ConfigFileKey.DM2L_DATABASE),
                                                   "charset": ConfigFileReader.get_val(
                                                       Constants.ConfigFileKey.DM2L_CHARSET)})
                await d2l.save_local()
        except:
            LOG.exception("下载到本地出现异常")
        finally:
            LOG.info("下载到本地结束...")

    async def _xhs_cover_watermark():
        # 去掉小红书右下角的水印，思路：用一个小图片遮盖掉
        LOG.info("开始去除xhs图片的水印...")
        watermark_utils.recursive_handle_xhs_images_with_xhs_watermark(BaseConfig.DOWNLOAD_DIR, is_retain_origin_image=BaseConfig.XHS_SAVE_WATERMARK_ORIGIN_IMAGE)
        LOG.info("去除xhs图片的水印结束！")

    async def wrapper_function(*args, **kwargs):
        # 在原函数之前执行的代码
        result = await original_function(*args, **kwargs)
        # 在原函数之后执行的代码
        if BaseConfig.SAVE_LOCAL_FLAG:
            # 爬取结果直存本地
            await _save_local(BaseConfig.DOWNLOAD_DIR)
            if BaseConfig.PLATFORM == Platform.XHS.value and BaseConfig.XHS_COVER_WATERMARK:
                # 去小红书水印
                await _xhs_cover_watermark()

        return result

    return wrapper_function
