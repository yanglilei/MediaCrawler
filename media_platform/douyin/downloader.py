"""
抖音下载器
图文下载器
视频下载器
"""


class BaseDyDownloader:
    def __init__(self, cookies: str):
        self.cookies = cookies


class ImageDownloader(BaseDyDownloader):
    def __init__(self, cookies: str):
        """
        图文下载器，有待验证！
        TODO 待完成
        :param cookies: cookie字符串
        """
        super().__init__(cookies)


class VideoDownloader(BaseDyDownloader):
    def __init__(self, cookies: str):
        """
        视频下载器
        :param cookies: cookie字符串
        """
        super().__init__(cookies)