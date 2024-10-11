import threading
from typing import Optional

import openpyxl
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


class XLSXOperator:
    """
    excel表格操作类
    """
    default_load_counts = 10
    realname_cell_to_username_offset = 2
    remark_cell_to_username_offset = 4
    login_error_desc_cell_to_username_offset = 3
    subject_cell_to_username_offset = 5
    lock = threading.RLock()

    def __init__(self, workbook_path: str, sheet_name, start_column: str, end_column: str, start_row_no: int,
                 end_row_no: int):
        """
        初始化
        :param workbook_path: 工作簿路径
        :param sheet_name: 表格名称
        :param start_column: 起始列，英文字母
        :param end_column: 截止列，英文字母
        :param start_row_no: 起始行，数字
        :param end_row_no: 截止行，数字
        """
        self.workbook_path = workbook_path
        self.sheet_name = sheet_name
        self.start_column = start_column
        self.end_column = end_column
        self.start_line_no = start_row_no
        self.end_line_no = end_row_no
        self.workbook: Optional[Workbook] = None
        self.worksheet: Optional[Worksheet] = None

    def open(self):
        self.workbook: Workbook = openpyxl.load_workbook(filename=self.workbook_path)
        self.worksheet: Worksheet = self.workbook[self.sheet_name]

    def update_cell_val(self, row_no, column_no, value):
        """
        更新单元格值
        :param row_no: int, 行号，数字
        :param column_no: int, 行号，数字，非英文字母
        :param value: 值
        :return:
        """
        self.worksheet.cell(row_no, column_no, value)

    def close(self):
        if self.workbook:
            self.workbook.close()

    def save(self):
        if self.workbook:
            self.workbook.save(self.workbook_path)

    def get_data(self):
        raise NotImplementedError()


if __name__ == '__main__':
    import strgen
    # 定义生成随机字符串的模式，这里使用字母和数字
    pattern = "[a-zA-Z0-9]{8}"

    # 创建StringGenerator对象
    generator = strgen.StringGenerator(pattern)

    # 生成随机字符串
    random_string = generator.render()

    print(random_string)