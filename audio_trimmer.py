from pydub import AudioSegment
import os
from pydub.utils import which
import subprocess
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import numpy as np

def setup_ffmpeg():
    """
    设置 ffmpeg 环境
    """
    if which("ffmpeg") is None:
        # 尝试设置 ffmpeg 路径
        ffmpeg_paths = [
            r"D:\Program Files\ffmpeg\ffmpeg-2025-03-27-git-114fccc4a5-full_build\bin\ffmpeg.exe",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(os.environ.get("CONDA_PREFIX", ""), "Library", "bin", "ffmpeg.exe"),
        ]
        
        for path in ffmpeg_paths:
            if os.path.exists(path):
                os.environ["FFMPEG_BINARY"] = path
                return True
        print("错误: 未找到 ffmpeg")
        return False
    return True

def check_audio_file(file_path):
    """
    使用 ffmpeg 检查音频文件是否可以正确读取
    """
    try:
        # 使用 ffmpeg 获取音频文件信息
        result = subprocess.run(
            ['ffmpeg', '-i', file_path, '-f', 'null', '-'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

def load_audio_file(file_path, filename):
    """
    尝试多种方式加载音频文件
    """
    print(f"尝试加载音频文件: {filename}")
    
    # 检查文件完整性
    if not check_audio_file(file_path):
        raise Exception("音频文件可能已损坏或格式不正确")
    
    # 尝试不同的加载方式
    methods = [
        # 方法1：使用特定格式加载
        lambda: AudioSegment.from_file(file_path, format=filename.split('.')[-1].lower()),
        # 方法2：使用 mp3 专用加载
        lambda: AudioSegment.from_mp3(file_path),
        # 方法3：自动检测格式
        lambda: AudioSegment.from_file(file_path),
        # 方法4：使用 wav 格式加载
        lambda: AudioSegment.from_wav(file_path),
    ]
    
    last_error = None
    for method in methods:
        try:
            audio = method()
            print("音频文件加载成功！")
            return audio
        except Exception as e:
            last_error = e
            continue
    
    raise last_error

def process_audio(args):
    """
    处理单个音频文件
    """
    input_path, output_path, start_cut, end_cut = args
    filename = os.path.basename(input_path)
    
    try:
        # 获取音频时长
        duration = float(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]).decode().strip())
        
        # 检查长度
        if duration <= start_cut + end_cut:
            return (False, filename, "文件太短")
            
        # 使用 ffmpeg 直接剪切和编码，使用更激进的压缩参数
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-ss', str(start_cut),
            '-t', str(duration - start_cut - end_cut),
            '-acodec', 'libmp3lame',     # 使用 MP3 编码器
            '-b:a', '64k',               # 降低比特率
            '-ac', '1',                  # 转换为单声道
            '-compression_level', '0',    # 最高压缩级别
            '-map_metadata', '-1',        # 移除元数据
            '-q:a', '8',                 # 最低音质（0最好，9最差）
            output_path
        ], check=True, capture_output=True)
        
        return (True, filename, None)
        
    except subprocess.CalledProcessError as e:
        return (False, filename, f"FFmpeg 错误: {e.stderr.decode()}")
    except Exception as e:
        return (False, filename, str(e))

def trim_audio(input_dir, output_dir, start_cut=10, end_cut=10, processes=None):
    """
    批量剪辑音频文件
    """
    try:
        if not os.path.exists(input_dir):
            print(f"错误：输入目录不存在：{input_dir}")
            return
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 获取所有音频文件
        audio_files = [f for f in os.listdir(input_dir) 
                      if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
        
        if not audio_files:
            print("未找到音频文件")
            return
            
        # 准备并行处理参数
        process_args = [
            (
                os.path.join(input_dir, filename),
                os.path.join(output_dir, filename),
                start_cut,
                end_cut
            )
            for filename in audio_files
        ]
        
        # 使用系统 CPU 核心数或指定的进程数
        num_processes = processes or cpu_count()
        
        # 统计
        total = len(audio_files)
        results = {'processed': 0, 'skipped': 0, 'failed': 0}
        failed_files = []  # 记录失败的文件
        
        # 使用进程池并行处理
        with Pool(processes=num_processes) as pool:
            with tqdm(total=total, desc="处理进度", ncols=100, leave=False, mininterval=0.1) as pbar:
                for success, filename, error in pool.imap_unordered(process_audio, process_args):
                    if success:
                        results['processed'] += 1
                    elif error == "文件太短":
                        results['skipped'] += 1
                    else:
                        results['failed'] += 1
                        failed_files.append((filename, error))  # 记录失败的文件名和错误信息
                    pbar.update(1)
        
        # 清除进度条并显示结果
        print(f"\r处理完成! 成功: {results['processed']}, 跳过: {results['skipped']}, 失败: {results['failed']}")
        
        # 如果有失败的文件，显示详细信息
        if failed_files:
            print("\n失败的文件:")
            for filename, error in failed_files:
                print(f"- {filename}: {error}")
        
    except Exception as e:
        print(f"程序出错: {str(e)}")

if __name__ == "__main__":
    input_directory = r"输入文件路径"
    output_directory = r"输出文件路径"
    
    start_seconds = 22
    end_seconds = 17
    
    # 可以指定进程数，例如使用8个进程
    # trim_audio(input_directory, output_directory, start_seconds, end_seconds, processes=8)
    
    # 或使用默认的 CPU 核心数
    trim_audio(input_directory, output_directory, start_seconds, end_seconds)