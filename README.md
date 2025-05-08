# 音频批量剪辑工具

这是一个用于批量剪辑音频文件的 Python 工具，可以同时处理多个音频文件，去除每个文件的开头和结尾部分。

## 功能特点

- 批量处理多个音频文件
- 支持 MP3、WAV、M4A 格式
- 多进程并行处理，提高效率
- 保持原始音频质量
- 显示处理进度条
- 详细的错误报告

## 环境要求

- Python 3.6+
- ffmpeg
- 依赖包：
  - pydub
  - tqdm
  - numpy

## 安装步骤

1. 安装 Python 依赖：
```bash
pip install pydub tqdm numpy
```

2. 安装 ffmpeg：
```bash
# 使用 conda 安装
conda install -c conda-forge ffmpeg

# 或手动下载安装
# 访问 https://github.com/BtbN/FFmpeg-Builds/releases
# 下载并解压到合适的位置
```

## 使用方法

1. 修改代码中的输入输出路径：
```python
input_directory = r"你的输入文件夹路径"
output_directory = r"你的输出文件夹路径"
```

2. 设置剪切时间：
```python
start_seconds = 22  # 开头剪切的秒数
end_seconds = 17    # 结尾剪切的秒数
```

3. 运行脚本：
```bash
python audio_trimmer.py
```

## 参数说明

- `input_directory`: 输入音频文件夹路径
- `output_directory`: 输出音频文件夹路径
- `start_seconds`: 开头要剪切的秒数
- `end_seconds`: 结尾要剪切的秒数
- `processes`: 并行处理的进程数（可选，默认使用所有 CPU 核心）

## 输出说明

- 处理成功的文件会保存在输出目录中
- 文件名格式为：`trimmed_原文件名`
- 程序会显示处理进度和结果统计
- 如果有处理失败的文件，会显示详细的错误信息

## 注意事项

1. 确保输入目录存在且包含音频文件
2. 确保有足够的磁盘空间
3. 确保已正确安装 ffmpeg
4. 处理大文件时可能需要较长时间

## 常见问题

1. 如果提示找不到 ffmpeg，请检查安装路径
2. 如果处理失败，检查音频文件是否完整
3. 如果输出文件大小为 0，检查输入文件格式是否正确

## 许可证

MIT License