import warnings
warnings.filterwarnings('ignore')
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import SubtitleGenerator
from backend import main

if __name__ == '__main__':
    # 1. 新建字幕生成对象，指定语言
    # sg = SubtitleGenerator(r"D:\DinoStark\Temp\IMG_1524.mp4", language="auto")
    sg = main.SubtitleGenerator(r"D:\DinoStark\Temp\output_audio.mp3", language="auto")
    # 2. 运行程序
    sg.run()
