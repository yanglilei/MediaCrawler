# -*- coding: utf-8 -*-
import asyncio
import functools
import sys
from typing import Optional

from playwright.async_api import BrowserContext, Page
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

from base.base_crawler import AbstractLogin
from config.base_config import BaseConfig
from tools import utils


class ZhiHuLogin(AbstractLogin):

    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext,
                 context_page: Page,
                 login_phone: Optional[str] = "",
                 cookie_str: str = ""
                 ):
        BaseConfig.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self) -> bool:
        """
        Check if the current login status is successful and return True otherwise return False
        Returns:

        """
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        current_web_session = cookie_dict.get("z_c0")
        if current_web_session:
            return True
        return False

    async def begin(self):
        """Start login zhihu"""
        utils.logger.info("[ZhiHu.begin] Begin login zhihu ...")
        if BaseConfig.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif BaseConfig.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif BaseConfig.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[ZhiHu.begin]I nvalid Login Type Currently only supported qrcode or phone or cookies ...")

    async def login_by_mobile(self):
        """Login zhihu by mobile"""
        # todo implement login by mobile

    async def login_by_qrcode(self):
        """login zhihu website and keep webdriver login state"""
        utils.logger.info("[ZhiHu.login_by_qrcode] Begin login zhihu by qrcode ...")
        qrcode_img_selector = "canvas.Qrcode-qrcode"
        # find login qrcode
        base64_qrcode_img = await utils.find_qrcode_img_from_canvas(
            self.context_page,
            canvas_selector=qrcode_img_selector
        )
        if not base64_qrcode_img:
            utils.logger.info("[ZhiHu.login_by_qrcode] login failed , have not found qrcode please check ....")
            if not base64_qrcode_img:
                sys.exit()

        # show login qrcode
        # fix issue #12
        # we need to use partial function to call show_qrcode function and run in executor
        # then current asyncio event loop will not be blocked
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[ZhiHu.login_by_qrcode] waiting for scan code login, remaining time is 120s")
        try:
            await self.check_login_state()

        except RetryError:
            utils.logger.info("[ZhiHu.login_by_qrcode] Login zhihu failed by qrcode login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(
            f"[ZhiHu.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_cookies(self):
        """login zhihu website by cookies"""
        utils.logger.info("[ZhiHu.login_by_cookies] Begin login zhihu by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".zhihu.com",
                'path': "/"
            }])
