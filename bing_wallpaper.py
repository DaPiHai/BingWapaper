# 文件名: bing_wallpaper.py
import requests
import ctypes
import sys
import os
from pathlib import Path
from datetime import datetime

# 配置项
WALLPAPER_URL = "https://bing.img.run/uhd.php"
MAX_RETRY = 3

# 动态路径配置
try:
    SCRIPT_DIR = Path(__file__).parent.resolve()
except NameError:  # 处理直接复制代码到REPL的情况
    SCRIPT_DIR = Path.cwd()

SAVE_DIR = SCRIPT_DIR / "images"


def create_save_dir():
    """创建壁纸保存目录（带权限检查）"""
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"目录已创建/确认：{SAVE_DIR}")
        return True
    except PermissionError as pe:
        print(f"权限不足，无法创建目录：{SAVE_DIR}\n错误详情：{pe}")
        return False
    except Exception as e:
        print(f"创建目录时发生意外错误：{e}")
        return False


def download_wallpaper():
    """下载必应壁纸（带重试机制）"""
    for attempt in range(MAX_RETRY):
        try:
            # response = requests.get(WALLPAPER_URL, timeout=15)
            response = requests.get(
                WALLPAPER_URL,
                timeout=15,
                verify=r'E:\apps\anaconda3\Lib\site-packages\certifi\cacert.pem'
            )
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                raise ValueError(f"非图片类型响应（{content_type}）")

            return response.content
        except requests.exceptions.RequestException as re:
            print(f"网络请求失败（尝试 {attempt + 1}/{MAX_RETRY}）: {re}")
            if attempt == MAX_RETRY - 1:
                raise


def save_wallpaper(image_data):
    """保存壁纸文件（带时间戳）"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = SAVE_DIR / f"Bing_{timestamp}.jpg"

        with open(filename, 'wb') as f:
            f.write(image_data)
        print(f"文件已保存：{filename}")
        return filename.resolve()  # 返回绝对路径
    except IOError as ioe:
        print(f"文件保存失败：{ioe}")
        raise


def set_wallpaper(filepath):
    """设置Windows壁纸（带路径验证）"""
    target = Path(filepath)
    if not target.exists():
        raise FileNotFoundError(f"壁纸文件不存在：{target.absolute()}")

    # 转换为Windows API需要的字符串格式
    wallpaper_path = str(target.absolute())

    SPI_SETDESKWALLPAPER = 0x0014
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    print(f"尝试设置壁纸路径：{wallpaper_path}")
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        wallpaper_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

    if not result:
        error_code = ctypes.GetLastError()
        raise WindowsError(f"API调用失败，错误代码：{error_code}")


def main():
    print("=" * 40)
    print(f"脚本目录：{SCRIPT_DIR}")
    print(f"保存目录：{SAVE_DIR}")
    print("=" * 40)

    try:
        if not create_save_dir():
            return 1

        image_data = download_wallpaper()
        wallpaper_path = save_wallpaper(image_data)
        set_wallpaper(wallpaper_path)

        print("\n操作成功！")
        print(f"当前壁纸：{wallpaper_path}")
        return 0
    except Exception as e:
        print(f"\n错误发生：{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())