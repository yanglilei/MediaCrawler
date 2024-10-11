import os
from pathlib import Path

from PIL import Image

from tools import utils


class XHSWatermarkHandler:
    def __init__(self, cover_image_path: str):
        self.cover_image_path = cover_image_path
        if not os.path.exists(cover_image_path):
            raise ValueError(f"cover_image_path is not exists: {cover_image_path}")

    def handle(self, origin_image_path, is_retain_origin_image=True):
        """
        处理水印逻辑
        :param origin_image_path: 原图路径
        :param is_retain_origin_image: 保存原图标志，True-保存原图；False-不保存原图
        :return:
        """
        utils.logger.info(f"开始编辑图片：【{origin_image_path}】")
        try:
            new_image_path = self.concat_image(origin_image_path)
        except:
            utils.logger.exception("编辑图片失败")
        else:
            utils.logger.info(f"编辑图片成功！【{origin_image_path}】 保存到：【{new_image_path}】")
            if not is_retain_origin_image:
                try:
                    os.remove(origin_image_path)
                except:
                    utils.logger.exception("删除旧图片失败")

    def concat_image(self, origin_image_path, new_image_path="") -> str:

        cover_image = None
        origin_image = None
        try:
            # 打开背景图
            origin_image = Image.open(origin_image_path).convert('RGBA')
            origin_image_width, origin_image_height = origin_image.size
            # 打开水印图
            cover_image = Image.open(self.cover_image_path).convert('RGBA')
            cover_image_width, cover_image_height = cover_image.size

            # 获取透明图片的透明通道（alpha通道）
            r, g, b, alpha = cover_image.split()
            new_image = Image.new('RGB', (origin_image_width, origin_image_height), (255, 255, 255))
            origin_image.paste(origin_image, (0, 0))
            origin_image.paste(cover_image,
                               (origin_image_width - cover_image_width, origin_image_height - cover_image_height),
                               alpha)

            # 围绕中心的点旋转180度
            rotated_cover_image = cover_image.rotate(180, center=(cover_image_width // 2, cover_image_height // 2),
                                                     expand=True)
            origin_image.paste(rotated_cover_image, (0, 0), rotated_cover_image.split()[3])

            new_image_path = origin_image_path if not new_image_path else new_image_path
            new_file_path = Path(new_image_path).with_suffix('.png')
            # 保存拼接后的图片
            origin_image.save(new_file_path)
            return str(new_file_path)
        finally:
            if origin_image:
                origin_image.close()
            if cover_image:
                cover_image.close()


def recursive_handle_xhs_images_with_xhs_watermark(image_dir, cover_image_path=None, is_retain_origin_image=True,
                                                   extensions=('.jpg',)):
    """
    递归处理xhs带水印的图片，带水印的图片都为.jpg格式，只处理.jpg格式的图片。

    :param image_dir: 图片目录
    :param cover_image_path: 遮罩图片的路径，用于遮罩掉水印
    :param is_retain_origin_image: 是否保存原图片，原图片为.jpg格式，True-保存；False-不保存！
    :param extensions: 后缀，只处理.jpg格式的图片。从xhs获取的图片保存到本地均为.jpg格式，因此此处只要获取.jpg格式的图片，.png的图片不能处理，防止已经去过水印的图片被删除！
    :return:
    """
    from pathlib import Path
    if not image_dir:
        raise ValueError("image_dir 不能为空")

    if cover_image_path and not Path(cover_image_path).exists():
        raise ValueError(f"cover_image_path 路径不存在：{cover_image_path}")

    if image_dir and not Path(image_dir).exists():
        raise ValueError(f"image_dir 路径不存在：{image_dir}")

    xhs_watermark_handler = XHSWatermarkHandler(
        str(Path.cwd().joinpath("xhs_cover.png")) if not cover_image_path else cover_image_path)

    # 定义要遍历的文件夹路径
    folder_path = Path(image_dir)
    # 定义所需的图片文件扩展名
    # extensions = ['.jpg', '.jpeg', '.png']

    # 使用列表推导式和递归遍历所有文件
    image_files = [file for file in folder_path.rglob('*') if file.suffix.lower() in extensions and file.is_file()]

    # 处理所有的带水印的图片
    for image_file in image_files:
        xhs_watermark_handler.handle(image_file, is_retain_origin_image)


if __name__ == "__main__":
    recursive_handle_xhs_images_with_xhs_watermark(r"C:\Users\lovel\Desktop\image_output_dir",
                                                   is_retain_origin_image=False)
