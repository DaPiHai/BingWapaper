# 文件名: bing_wallpaper.py（完整代码）
import requests
import ctypes
import sys
from pathlib import Path
from datetime import datetime

# 配置项
WALLPAPER_URL = "https://bing.img.run/uhd.php"
MAX_RETRY = 3

# 动态路径配置
try:
    SCRIPT_DIR = Path(__file__).parent.resolve()
except NameError:
    SCRIPT_DIR = Path.cwd()

SAVE_DIR = SCRIPT_DIR / "images"
LOG_DIR = SCRIPT_DIR / "logs"


class EnhancedLogger:
    """增强型日志记录器（支持时间戳和空行分隔）"""

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.log_file = self._get_log_path()
        self.terminal = sys.stdout

        log_dir.mkdir(parents=True, exist_ok=True)
        self.log = open(self.log_file, 'a', encoding='utf-8')

    def _get_log_path(self):
        """生成月度日志文件路径"""
        return self.log_dir / f"{datetime.now().strftime('%Y-%m')}.log"

    def _get_timestamp(self):
        """生成标准时间戳"""
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")

    def write(self, msg):
        """智能添加时间戳（空行不加时间戳）"""
        if msg.strip() == '':
            self.terminal.write(msg)
            self.log.write(msg)
        else:
            timestamped_msg = self._get_timestamp() + msg
            self.terminal.write(timestamped_msg)
            self.log.write(timestamped_msg)

    def flush(self):
        """同步缓冲区"""
        self.terminal.flush()
        self.log.flush()


def create_dir(dir_path):
    """创建目录（带错误处理）"""
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"目录创建失败：{str(e)}")
        return False


def download_wallpaper():
    """下载壁纸（带详细日志）"""
    print("正在尝试下载文件...")
    for attempt in range(MAX_RETRY):
        try:
            response = requests.get(WALLPAPER_URL, timeout=15, verify=False)
            response.raise_for_status()

            if not response.headers.get('Content-Type', '').startswith('image/'):
                raise ValueError("非图片类型响应")

            print("文件下载成功")
            return response.content
        except Exception as e:
            if attempt == MAX_RETRY - 1:
                print(f"文件下载失败：{str(e)}")
                raise


def save_wallpaper(image_data):
    """保存文件（带日期命名）"""
    filename = SAVE_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jpg"

    if filename.exists():
        raise FileExistsError("今日壁纸已存在")

    try:
        with open(filename, 'wb') as f:
            f.write(image_data)
        print("文件保存成功")
        return filename.resolve()
    except Exception as e:
        print(f"文件保存失败：{str(e)}")
        raise


def set_wallpaper(filepath):
    """设置壁纸（带状态跟踪）"""
    print("正在尝试设置壁纸...")
    target = Path(filepath)

    if not target.exists():
        raise FileNotFoundError(f"壁纸文件不存在：{target}")

    SPI_SETDESKWALLPAPER = 0x0014
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        str(target.absolute()),
        0x01 | 0x02
    )

    if not result:
        raise WindowsError(f"API调用失败，错误代码：{ctypes.GetLastError()}")

    print("壁纸设置成功")


def main():
    sys.stdout = EnhancedLogger(LOG_DIR)
    print("\n")  # 执行分隔空行

    current_date_file = SAVE_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jpg"
    if current_date_file.exists():
        print("今日壁纸已存在，程序终止")
        return 1

    try:
        if not all([create_dir(SAVE_DIR), create_dir(LOG_DIR)]):
            return 1

        image_data = download_wallpaper()
        wallpaper_path = save_wallpaper(image_data)
        set_wallpaper(wallpaper_path)

        print(f"操作成功！壁纸路径：{wallpaper_path}")
        return 0
    except Exception as e:
        print(f"错误发生：{str(e)}")
        return 1
    finally:
        print("\n")  # 确保每次执行后有空行分隔


if __name__ == "__main__":
    sys.exit(main())