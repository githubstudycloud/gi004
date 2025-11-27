# 音色克隆 TTS 完整离线部署指南

本文档详细说明如何在**完全离线**环境中部署所有 5 种音色克隆 TTS 引擎。

---

## 目录

- [项目总览](#项目总览)
- [快速开始](#快速开始)
- [完整下载清单](#完整下载清单)
- [引擎一：XTTS-v2](#引擎一xtts-v2推荐)
- [引擎二：OpenVoice](#引擎二openvoice)
- [引擎三：GPT-SoVITS](#引擎三gpt-sovits中文首选)
- [引擎四：CosyVoice](#引擎四cosyvoice阿里通义)
- [引擎五：Fish-Speech](#引擎五fish-speech)
- [生产环境部署](#生产环境部署)
- [离线安装 Python 依赖](#离线安装-python-依赖)
- [常见问题](#常见问题)

---

## 项目总览

### 完整目录结构

```
vscode/
├── voice-clone-tts/              # 音色克隆项目
│   ├── production/               # 生产环境代码【推荐使用】
│   │   ├── main.py              # 命令行入口
│   │   ├── server.py            # HTTP API 服务
│   │   ├── client.py            # Python 客户端
│   │   ├── requirements.txt     # 依赖清单
│   │   ├── environment.yml      # Conda 环境配置
│   │   ├── common/              # 公共模块
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # 基类定义
│   │   │   └── utils.py         # 工具函数
│   │   ├── xtts/                # XTTS-v2 引擎
│   │   │   ├── __init__.py
│   │   │   ├── cloner.py
│   │   │   └── requirements.txt
│   │   ├── openvoice/           # OpenVoice 引擎
│   │   │   ├── __init__.py
│   │   │   ├── cloner.py
│   │   │   └── requirements.txt
│   │   └── gpt-sovits/          # GPT-SoVITS 引擎
│   │       ├── __init__.py
│   │       ├── cloner.py
│   │       └── requirements.txt
│   │
│   ├── solutions/               # 各方案独立实现
│   │   ├── 01-openvoice/
│   │   │   ├── voice_cloner.py
│   │   │   ├── test_clone.py
│   │   │   └── requirements.txt
│   │   ├── 02-coqui-xtts/
│   │   │   ├── voice_cloner.py
│   │   │   ├── test_clone.py
│   │   │   └── requirements.txt
│   │   ├── 03-gpt-sovits/
│   │   │   ├── voice_cloner.py
│   │   │   ├── test_clone.py
│   │   │   └── requirements.txt
│   │   ├── 04-cosyvoice/        # CosyVoice 方案
│   │   │   ├── voice_cloner.py
│   │   │   ├── test_clone.py
│   │   │   └── requirements.txt
│   │   └── 05-fish-speech/      # Fish-Speech 方案
│   │       ├── voice_cloner.py
│   │       ├── test_clone.py
│   │       └── requirements.txt
│   │
│   ├── examples/                # 示例代码
│   └── requirements.txt         # 基础依赖
│
├── tts_model/                   # 模型文件【离线必需】
│   ├── README.md
│   └── xtts_v2.tar.part_*       # XTTS-v2 模型分卷 (21个文件)
│
└── OFFLINE_DEPLOYMENT.md        # 本文档
```

### 引擎对比

| 引擎 | 离线难度 | 中文质量 | 模型大小 | 显存需求 | 推荐场景 |
|------|---------|---------|---------|---------|---------|
| **XTTS-v2** | ⭐ 简单 | ⭐⭐⭐ | ~2GB | 4GB | 快速部署、多语言 |
| **OpenVoice** | ⭐⭐ 中等 | ⭐⭐⭐⭐ | ~500MB | 4GB | 音色转换 |
| **GPT-SoVITS** | ⭐⭐⭐ 复杂 | ⭐⭐⭐⭐⭐ | ~3GB | 6GB | 中文首选 |
| **CosyVoice** | ⭐⭐⭐ 复杂 | ⭐⭐⭐⭐⭐ | ~2GB | 4GB | 阿里通义、跨语言 |
| **Fish-Speech** | ⭐⭐ 中等 | ⭐⭐⭐⭐ | ~2GB | 4GB | 低显存、快速推理 |

---

## 快速开始

### 最简部署（XTTS-v2）

```bash
# 1. 克隆代码
git clone https://github.com/githubstudycloud/gi004.git
cd gi004

# 2. 还原模型文件
cd tts_model
cat xtts_v2.tar.part_* | tar -xvf -
cd ..

# 3. 创建环境
conda create -n voice-clone python=3.10
conda activate voice-clone

# 4. 安装依赖
pip install -r voice-clone-tts/production/requirements.txt

# 5. 启动服务
cd voice-clone-tts/production
python main.py serve --engine xtts --port 8000
```

---

## 完整下载清单

### 代码文件（GitHub 仓库）

| 类型 | 路径 | 说明 |
|------|------|------|
| 生产代码 | `voice-clone-tts/production/` | 统一 API 服务 |
| XTTS 实现 | `voice-clone-tts/production/xtts/` | XTTS-v2 引擎 |
| OpenVoice 实现 | `voice-clone-tts/production/openvoice/` | OpenVoice 引擎 |
| GPT-SoVITS 实现 | `voice-clone-tts/production/gpt-sovits/` | GPT-SoVITS 客户端 |
| CosyVoice 实现 | `voice-clone-tts/solutions/04-cosyvoice/` | CosyVoice 方案 |
| Fish-Speech 实现 | `voice-clone-tts/solutions/05-fish-speech/` | Fish-Speech 方案 |
| 公共模块 | `voice-clone-tts/production/common/` | 基类和工具 |

### 模型文件

| 引擎 | 模型 | 大小 | 下载地址 | 本仓库状态 |
|------|------|------|---------|-----------|
| **XTTS-v2** | xtts_v2 | ~2GB | [HuggingFace](https://huggingface.co/coqui/XTTS-v2) | ✅ 已包含 |
| **OpenVoice** | OpenVoiceV2 | ~500MB | [HuggingFace](https://huggingface.co/myshell-ai/OpenVoiceV2) | ❌ 需下载 |
| **GPT-SoVITS** | pretrained_models | ~3GB | [HuggingFace](https://huggingface.co/lj1995/GPT-SoVITS) | ❌ 需下载 |
| **CosyVoice** | CosyVoice-300M | ~2GB | [ModelScope](https://modelscope.cn/models/iic/CosyVoice-300M) | ❌ 需下载 |
| **Fish-Speech** | fish-speech-1.5 | ~2GB | [HuggingFace](https://huggingface.co/fishaudio/fish-speech-1.5) | ❌ 需下载 |

### 第三方代码仓库

| 引擎 | GitHub 仓库 | 说明 |
|------|------------|------|
| OpenVoice | https://github.com/myshell-ai/OpenVoice | 需源码安装 |
| GPT-SoVITS | https://github.com/RVC-Boss/GPT-SoVITS | 独立服务 |
| CosyVoice | https://github.com/FunAudioLLM/CosyVoice | 需源码安装 |
| Fish-Speech | https://github.com/fishaudio/fish-speech | 需源码安装 |

---

## 引擎一：XTTS-v2（推荐）

### 特点
- 安装最简单，一行 `pip install TTS`
- 支持 17 种语言
- 只需 6 秒参考音频
- 模型已包含在本仓库

### 离线部署步骤

#### 1. 还原模型

```bash
# Linux / macOS / Git Bash
cd tts_model
cat xtts_v2.tar.part_* | tar -xvf -

# Windows PowerShell
cd tts_model
Get-Content xtts_v2.tar.part_* -ReadCount 0 | Set-Content xtts_v2.tar -Encoding Byte
tar -xvf xtts_v2.tar

# Windows CMD
cd tts_model
copy /b xtts_v2.tar.part_* xtts_v2.tar
tar -xvf xtts_v2.tar
```

还原后结构：
```
tts_model/xtts_v2/
├── config.json          # 模型配置
├── model.pth            # 主模型权重 (1.87GB)
├── dvae.pth             # DVAE 模型 (211MB)
├── speakers_xtts.pth    # 说话人嵌入 (7.75MB)
├── mel_stats.pth        # 梅尔统计 (1KB)
└── vocab.json           # 词汇表 (361KB)
```

#### 2. 安装依赖

```bash
# requirements: xtts/requirements.txt
TTS>=0.22.0
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.21.0
```

#### 3. 使用本地模型

```python
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# 加载配置
config = XttsConfig()
config.load_json("tts_model/xtts_v2/config.json")

# 加载模型
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="tts_model/xtts_v2/")
model.cuda()  # 或 model.cpu()

# 音色克隆
outputs = model.synthesize(
    "你好，这是测试语音",
    config,
    speaker_wav="reference.wav",
    language="zh-cn"
)
```

#### 4. 启动服务

```bash
cd voice-clone-tts/production
python main.py serve --engine xtts --model-path ../../tts_model/xtts_v2 --port 8000
```

---

## 引擎二：OpenVoice

### 特点
- 音色与内容分离
- 先用基础 TTS 生成语音，再转换音色
- 可将任意语音转换为目标音色

### 离线部署步骤

#### 1. 克隆并安装 OpenVoice

```bash
git clone https://github.com/myshell-ai/OpenVoice.git
cd OpenVoice
pip install -e .
```

#### 2. 下载模型

从 [HuggingFace](https://huggingface.co/myshell-ai/OpenVoiceV2) 下载，解压到：

```
checkpoints_v2/
├── converter/
│   ├── config.json
│   └── checkpoint.pth
└── base_speakers/
    └── ses/
        └── zh.pth
```

#### 3. 安装依赖

```bash
# requirements: openvoice/requirements.txt
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.21.0
librosa>=0.10.0
soundfile>=0.12.0
edge-tts>=6.1.0  # 基础 TTS
```

#### 4. 启动服务

```bash
cd voice-clone-tts/production
python main.py serve --engine openvoice --model-path ../checkpoints_v2/converter --port 8000
```

---

## 引擎三：GPT-SoVITS（中文首选）

### 特点
- 中文效果最佳
- 支持零样本（5秒）和微调（1分钟）
- 需要运行独立的 API 服务

### 离线部署步骤

#### 1. 克隆并安装 GPT-SoVITS

```bash
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
pip install -r requirements.txt
```

#### 2. 下载预训练模型

从 [HuggingFace](https://huggingface.co/lj1995/GPT-SoVITS) 下载到：

```
GPT-SoVITS/GPT_SoVITS/pretrained_models/
├── chinese-roberta-wwm-ext-large/
├── chinese-hubert-base/
├── s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt
├── s2G488k.pth
└── ...
```

#### 3. 启动 GPT-SoVITS API 服务

```bash
cd GPT-SoVITS
python api_v2.py -a 127.0.0.1 -p 9880
```

#### 4. 启动封装服务

```bash
cd voice-clone-tts/production
python main.py serve --engine gpt-sovits --api-host 127.0.0.1 --api-port 9880 --port 8000
```

### 注意事项
- GPT-SoVITS 提取音色时**必须提供参考文本**
- 参考音频建议 3-10 秒，清晰无杂音

---

## 引擎四：CosyVoice（阿里通义）

### 特点
- 3秒极速克隆
- 支持中英日粤韩五种语言
- 跨语言合成（用中文音频合成英文）
- 情感/风格控制

### 离线部署步骤

#### 1. 克隆并安装 CosyVoice

```bash
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice

# 创建环境（需要 Python 3.8）
conda create -n cosyvoice python=3.8
conda activate cosyvoice

# 安装依赖
pip install -r requirements.txt
```

#### 2. 下载模型

从 [ModelScope](https://modelscope.cn/models/iic/CosyVoice-300M) 或 [HuggingFace](https://huggingface.co/FunAudioLLM/CosyVoice-300M) 下载到：

```
CosyVoice/pretrained_models/
├── CosyVoice-300M/          # 零样本/跨语言
├── CosyVoice-300M-SFT/      # 预训练角色
└── CosyVoice-300M-Instruct/ # 指令控制
```

#### 3. 安装依赖

```bash
# requirements: solutions/04-cosyvoice/requirements.txt
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.21.0
soundfile>=0.12.0
librosa>=0.10.0
```

#### 4. 使用代码

```python
# 使用 solutions/04-cosyvoice/voice_cloner.py
from voice_cloner import CosyVoiceCloner

cloner = CosyVoiceCloner(model_dir="pretrained_models/CosyVoice-300M")

# 零样本克隆
cloner.zero_shot_clone(
    text="你好，这是克隆的语音",
    reference_audio="reference.wav",
    reference_text="参考音频的文本",
    output_path="output.wav"
)

# 跨语言克隆（用中文参考合成英文）
cloner.cross_lingual_clone(
    text="Hello, this is cross-lingual synthesis",
    reference_audio="chinese_reference.wav",
    output_path="output_english.wav"
)

# 指令控制（需要 Instruct 模型）
cloner.instruct_clone(
    text="今天天气真好",
    speaker="中文女",
    instruct="用开心的语气说",
    output_path="output_happy.wav"
)
```

---

## 引擎五：Fish-Speech

### 特点
- 低显存需求（仅需 4GB）
- 快速推理（RTX 4090 达 1:7 实时率）
- 支持 8 种语言（中英日韩法德阿西）
- 无需音素依赖

### 离线部署步骤

#### 1. 克隆并安装 Fish-Speech

```bash
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech

# 创建环境
conda create -n fish-speech python=3.10
conda activate fish-speech

# 安装
pip install -e .
```

#### 2. 下载模型

```bash
# 使用 huggingface-cli
huggingface-cli download fishaudio/fish-speech-1.5 --local-dir checkpoints/fish-speech-1.5

# 或手动下载: https://huggingface.co/fishaudio/fish-speech-1.5
```

模型目录：
```
fish-speech/checkpoints/fish-speech-1.5/
├── model.pth
├── config.json
└── ...
```

#### 3. 安装依赖

```bash
# requirements: solutions/05-fish-speech/requirements.txt
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.21.0
soundfile>=0.12.0
librosa>=0.10.0
transformers>=4.35.0
requests>=2.28.0
httpx>=0.24.0
```

#### 4. 使用代码

```python
# 使用 solutions/05-fish-speech/voice_cloner.py

# 方式一：本地推理（需要完整安装 fish-speech）
from voice_cloner import FishSpeechCloner

cloner = FishSpeechCloner(model_path="checkpoints/fish-speech-1.5")
cloner.clone(
    text="你好，这是 Fish-Speech 合成的语音",
    reference_audio="reference.wav",
    output_path="output.wav",
    language="zh"
)

# 方式二：使用 API（需注册 fish.audio 获取 API key）
from voice_cloner import FishSpeechAPI

api = FishSpeechAPI(api_key="your-api-key")
api.clone(
    text="Hello world",
    reference_audio="reference.wav",
    output_path="output.wav"
)

# 方式三：本地命令行调用
from voice_cloner import FishSpeechLocal

local = FishSpeechLocal(fish_speech_path="fish-speech")
local.clone(
    text="测试语音",
    reference_audio="reference.wav",
    output_path="output.wav"
)
```

---

## 生产环境部署

### Docker 部署

```dockerfile
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app

# 安装依赖
COPY voice-clone-tts/production/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY voice-clone-tts/production/ ./voice-clone/

# 复制模型
COPY tts_model/xtts_v2/ ./models/xtts_v2/

# 设置环境变量
ENV MODEL_PATH=/app/models/xtts_v2
ENV VOICE_ENGINE=xtts

EXPOSE 8000

CMD ["python", "voice-clone/server.py", "--engine", "xtts", "--port", "8000"]
```

构建并运行：

```bash
docker build -t voice-clone:latest .
docker run -d -p 8000:8000 --gpus all voice-clone:latest
```

### HTTP API 使用

```bash
# 提取音色
curl -X POST http://localhost:8000/extract_voice \
  -F "audio=@reference.wav" \
  -F "voice_name=我的声音"

# 合成语音
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "你好世界", "voice_id": "xxx", "language": "zh"}' \
  --output output.wav

# 直接克隆（不保存音色）
curl -X POST http://localhost:8000/synthesize_direct \
  -F "audio=@reference.wav" \
  -F "text=你好世界" \
  -F "language=zh" \
  --output output.wav

# 列出所有音色
curl http://localhost:8000/voices

# 删除音色
curl -X DELETE http://localhost:8000/voices/{voice_id}
```

### Python 客户端

```python
from client import VoiceCloneClient, VoiceCloneService

# 方式一：使用客户端
client = VoiceCloneClient("http://localhost:8000")

# 健康检查
print(client.health_check())

# 提取音色
voice = client.extract_voice("reference.wav", voice_name="测试")
print(f"音色ID: {voice['voice_id']}")

# 合成语音
audio_data = client.synthesize("你好世界", voice["voice_id"])
with open("output.wav", "wb") as f:
    f.write(audio_data)

# 或直接保存到文件
client.synthesize_to_file("你好世界", voice["voice_id"], "output.wav")

# 方式二：使用服务封装（更简单）
service = VoiceCloneService("http://localhost:8000")

# 一键克隆
service.clone_voice("你好世界", "reference.wav", "output.wav")

# 批量合成
texts = ["第一句", "第二句", "第三句"]
service.batch_synthesize(texts, voice_id, output_dir="./outputs/")
```

---

## 离线安装 Python 依赖

### 在有网络的机器上下载

```bash
# 方式一：下载 wheel 包
pip download -r requirements.txt -d ./packages/

# 方式二：使用 pip wheel
pip wheel -r requirements.txt -w ./wheels/

# 方式三：导出 conda 环境
conda env export > environment_full.yml
```

### 在离线机器上安装

```bash
# 从本地目录安装
pip install --no-index --find-links=./packages/ -r requirements.txt

# 或使用 wheel
pip install --no-index --find-links=./wheels/ -r requirements.txt
```

### 完整依赖清单

```
# ========== 核心依赖 ==========
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.21.0
librosa>=0.10.0
soundfile>=0.12.0

# ========== HTTP 服务 ==========
fastapi>=0.100.0
uvicorn>=0.22.0
python-multipart>=0.0.6
requests>=2.28.0

# ========== XTTS ==========
TTS>=0.22.0

# ========== OpenVoice ==========
edge-tts>=6.1.0

# ========== Fish-Speech ==========
transformers>=4.35.0
httpx>=0.24.0
```

---

## 常见问题

### Q: 模型还原失败？

确保所有分卷文件完整：
```bash
ls -la tts_model/xtts_v2.tar.part_*
# 应该有 21 个文件 (aa ~ au)
```

### Q: CUDA 内存不足？

```bash
# 使用 CPU
python main.py serve --engine xtts --device cpu --port 8000

# 或设置环境变量
export CUDA_VISIBLE_DEVICES=""
```

### Q: GPT-SoVITS 连接失败？

确保先启动 GPT-SoVITS API 服务：
```bash
cd GPT-SoVITS
python api_v2.py -a 127.0.0.1 -p 9880
```

### Q: OpenVoice 提示模型不存在？

确保下载了完整的 OpenVoiceV2 模型：
```
checkpoints_v2/
├── converter/
│   ├── config.json
│   └── checkpoint.pth
└── base_speakers/ses/zh.pth
```

### Q: CosyVoice 安装失败？

CosyVoice 需要 Python 3.8 环境：
```bash
conda create -n cosyvoice python=3.8
conda activate cosyvoice
cd CosyVoice && pip install -r requirements.txt
```

### Q: Fish-Speech 本地推理失败？

检查是否正确安装：
```bash
cd fish-speech
pip install -e .
```

确认模型已下载：
```bash
ls checkpoints/fish-speech-1.5/
```

---

## 下载清单总结

### 最小部署（仅 XTTS）

| 内容 | 大小 | 说明 |
|------|------|------|
| 代码 | ~5MB | GitHub 仓库 |
| XTTS 模型 | ~2GB | ✅ 已包含在仓库 |
| Python 依赖 | ~3GB | pip 安装 |
| **总计** | **~5GB** | |

### 完整部署（所有 5 个引擎）

| 内容 | 大小 | 说明 |
|------|------|------|
| 代码 | ~5MB | GitHub 仓库 |
| XTTS 模型 | ~2GB | ✅ 已包含 |
| OpenVoice 代码+模型 | ~500MB | GitHub + HuggingFace |
| GPT-SoVITS 代码+模型 | ~3GB | GitHub + HuggingFace |
| CosyVoice 代码+模型 | ~2GB | GitHub + ModelScope |
| Fish-Speech 代码+模型 | ~2GB | GitHub + HuggingFace |
| Python 依赖 | ~5GB | pip 安装 |
| **总计** | **~15GB** | |

---

## 代码文件完整清单

### production/ 目录（统一 API）

```
voice-clone-tts/production/
├── main.py               # 命令行入口（extract/synthesize/serve）
├── server.py             # FastAPI HTTP 服务
├── client.py             # VoiceCloneClient/VoiceCloneService
├── requirements.txt      # 依赖清单
├── environment.yml       # Conda 环境
├── common/
│   ├── __init__.py
│   ├── base.py           # VoiceClonerBase, VoiceEmbedding
│   └── utils.py          # ensure_dir, get_device, generate_voice_id
├── xtts/
│   ├── __init__.py
│   ├── cloner.py         # XTTSCloner
│   └── requirements.txt
├── openvoice/
│   ├── __init__.py
│   ├── cloner.py         # OpenVoiceCloner
│   └── requirements.txt
└── gpt-sovits/
    ├── __init__.py
    ├── cloner.py         # GPTSoVITSCloner
    └── requirements.txt
```

### solutions/ 目录（独立方案）

```
voice-clone-tts/solutions/
├── 01-openvoice/
│   ├── voice_cloner.py   # OpenVoice 独立实现
│   ├── test_clone.py
│   └── requirements.txt
├── 02-coqui-xtts/
│   ├── voice_cloner.py   # XTTS 独立实现
│   ├── test_clone.py
│   └── requirements.txt
├── 03-gpt-sovits/
│   ├── voice_cloner.py   # GPT-SoVITS 独立实现
│   ├── test_clone.py
│   └── requirements.txt
├── 04-cosyvoice/
│   ├── voice_cloner.py   # CosyVoiceCloner, CosyVoiceSimple
│   ├── test_clone.py
│   └── requirements.txt
└── 05-fish-speech/
    ├── voice_cloner.py   # FishSpeechCloner, FishSpeechAPI, FishSpeechLocal
    ├── test_clone.py
    └── requirements.txt
```

---

## 版本信息

- 文档版本: 2.0 (完整版)
- 更新日期: 2025-11-27
- 仓库地址: https://github.com/githubstudycloud/gi004
- 支持引擎: XTTS-v2, OpenVoice, GPT-SoVITS, CosyVoice, Fish-Speech
