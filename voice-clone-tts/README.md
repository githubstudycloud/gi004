# 音色提取与TTS语音生成方案

本项目探究使用 Python 从音频中提取音色特征，并结合 ChatTTS 等模型生成语音的技术方案。

## 📋 目录

- [方案概述](#方案概述)
- [方案一：ChatTTS + Speaker Embedding](#方案一chattts--speaker-embedding)
- [方案二：OpenVoice 音色克隆](#方案二openvoice-音色克隆)
- [方案三：Coqui TTS + XTTS-v2](#方案三coqui-tts--xtts-v2)
- [方案四：SpeechBrain + ChatTTS 组合](#方案四speechbrain--chattts-组合)
- [方案对比](#方案对比)
- [安装指南](#安装指南)

---

## 方案概述

音色克隆 TTS 的核心流程：

```
参考音频 → 音色特征提取(Speaker Embedding) → TTS模型 → 生成目标音频
```

### 关键技术点

1. **Speaker Embedding（说话人嵌入）**：将说话人的声音特征编码为一个向量
2. **Tone Color Converter（音色转换器）**：将生成的语音转换为目标音色
3. **Zero-shot Voice Cloning（零样本语音克隆）**：仅需几秒参考音频即可克隆

---

## 方案一：ChatTTS + Speaker Embedding

### 简介

[ChatTTS](https://github.com/2noise/chattts) 是一个专为日常对话设计的生成式语音模型，支持中英文，音质自然流畅。

### 核心特点

- ✅ 支持细粒度韵律控制（笑声、停顿等）
- ✅ 中英文混合支持良好
- ✅ 可保存和加载 speaker embedding (.pt文件)
- ⚠️ 不支持直接从音频提取音色（需配合其他工具）

### 音色使用方式

```python
import ChatTTS
import torch

# 初始化
chat = ChatTTS.Chat()
chat.load(compile=False)

# 方式1: 随机采样说话人
rand_spk = chat.sample_random_speaker()
print(rand_spk)  # 保存此值以便复用

# 方式2: 加载预保存的 .pt 音色文件
spk = torch.load("speaker_embedding.pt", map_location="cpu")

# 设置推理参数
params_infer_code = ChatTTS.Chat.InferCodeParams(
    spk_emb=spk,        # 说话人嵌入
    temperature=0.3,     # 温度参数
    top_P=0.7,
    top_K=20,
)

# 生成语音
wavs = chat.infer(
    ["你好，这是一段测试语音。"],
    params_infer_code=params_infer_code,
)
```

### 音色文件来源

1. **ChatTTS_Speaker 项目**：提供预训练的稳定音色种子
   - GitHub: https://github.com/6drf21e/ChatTTS_Speaker
2. **自行采样保存**：使用 `sample_random_speaker()` 采样满意的音色后保存

### 局限性

ChatTTS 本身**不支持从任意音频提取音色**，需要配合方案四中的 SpeechBrain 等工具。

---

## 方案二：OpenVoice 音色克隆

### 简介

[OpenVoice](https://github.com/myshell-ai/OpenVoice) 是 MIT 和 MyShell 开发的即时语音克隆模型，支持从任意音频提取音色。

### 核心特点

- ✅ **真正的音色克隆**：可从任意音频提取音色
- ✅ 只需几秒参考音频
- ✅ 支持多语言
- ✅ MIT 开源许可，可商用
- ✅ 分离音色和语言/口音控制

### 工作原理

```
参考音频 → SE Extractor → Tone Color Embedding
                                    ↓
文本 → Base TTS → 基础语音 → Tone Color Converter → 目标音色语音
```

### 代码示例

```python
import os
import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

# 设备配置
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# 加载音色转换器
ckpt_converter = 'checkpoints_v2/converter'
tone_color_converter = ToneColorConverter(
    f'{ckpt_converter}/config.json',
    device=device
)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

# 1. 从参考音频提取音色
reference_audio = 'reference_speaker.mp3'
target_se, audio_name = se_extractor.get_se(
    reference_audio,
    tone_color_converter,
    vad=True  # 启用语音活动检测
)

# 2. 加载源音色（基础TTS的音色）
source_se = torch.load(f'{ckpt_converter}/ses/base_se.pth', map_location=device)

# 3. 音色转换
tone_color_converter.convert(
    audio_src_path='generated_base.wav',  # 基础TTS生成的音频
    src_se=source_se,
    tgt_se=target_se,
    output_path='output_cloned.wav'
)
```

### 安装

```bash
git clone https://github.com/myshell-ai/OpenVoice.git
cd OpenVoice
pip install -e .

# 下载模型检查点
# V2版本: https://huggingface.co/myshell-ai/OpenVoiceV2
```

---

## 方案三：Coqui TTS + XTTS-v2

### 简介

[Coqui TTS](https://github.com/coqui-ai/TTS) 是功能最全面的开源 TTS 工具包，XTTS-v2 支持零样本语音克隆。

### 核心特点

- ✅ 功能全面，支持多种 TTS 模型
- ✅ XTTS-v2 支持 17 种语言
- ✅ 只需 6 秒参考音频
- ✅ 内置 Speaker Encoder
- ⚠️ 注意：Coqui 公司已关闭，但开源项目仍可用

### 代码示例

```python
from TTS.api import TTS

# 初始化 XTTS-v2 模型
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# 直接使用参考音频进行语音克隆
tts.tts_to_file(
    text="你好，这是克隆后的语音。",
    file_path="output.wav",
    speaker_wav="reference_speaker.wav",  # 参考音频
    language="zh-cn"
)
```

### 提取 Speaker Embedding

```python
from TTS.utils.synthesizer import Synthesizer
from TTS.tts.utils.speakers import SpeakerManager

# 使用 Speaker Encoder 提取嵌入
speaker_manager = SpeakerManager(
    encoder_model_path="path/to/encoder_model.pth",
    encoder_config_path="path/to/encoder_config.json"
)

# 从音频计算 embedding
embedding = speaker_manager.compute_embedding_from_clip("reference.wav")
```

### 安装

```bash
pip install TTS

# 或从源码安装
git clone https://github.com/coqui-ai/TTS
cd TTS
pip install -e .
```

---

## 方案四：SpeechBrain + ChatTTS 组合

### 简介

结合 [SpeechBrain](https://speechbrain.github.io/) 的说话人编码器提取音色特征，再用于 ChatTTS 等模型。

### 核心特点

- ✅ SpeechBrain 提供高质量的 Speaker Embedding
- ✅ 可与多种 TTS 模型组合
- ✅ 灵活性高
- ⚠️ 需要额外的嵌入空间映射

### 代码示例

```python
from speechbrain.inference.speaker import EncoderClassifier
import torch

# 加载预训练的说话人编码器
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)

# 从音频提取 embedding
embedding = classifier.encode_file("reference_speaker.wav")
print(f"Embedding shape: {embedding.shape}")  # [1, 192]

# 保存 embedding
torch.save(embedding, "speaker_embedding.pt")

# 计算两个音频的相似度
emb1 = classifier.encode_file("speaker1.wav")
emb2 = classifier.encode_file("speaker2.wav")
similarity = torch.nn.functional.cosine_similarity(emb1, emb2)
print(f"Similarity: {similarity.item()}")
```

### 与 ChatTTS 结合（实验性）

```python
# 注意：这需要进行嵌入空间的映射，因为两者的 embedding 维度不同
# ChatTTS 使用自己的 speaker embedding 格式

# 方法1：训练一个映射网络
# 方法2：使用 ChatTTS 的音色种子库匹配最相似的音色
```

### 安装

```bash
pip install speechbrain
```

---

## 方案五：pyannote-audio 音色分析

### 简介

[pyannote-audio](https://github.com/pyannote/pyannote-audio) 专注于说话人分析，可用于音色特征提取。

### 代码示例

```python
from pyannote.audio import Model, Inference

# 加载说话人嵌入模型
model = Model.from_pretrained(
    "pyannote/embedding",
    use_auth_token="YOUR_HF_TOKEN"
)

# 创建推理器
inference = Inference(model, window="whole")

# 提取 embedding
embedding = inference("reference_speaker.wav")
print(f"Embedding shape: {embedding.shape}")
```

---

## 方案对比

| 方案 | 音色提取 | TTS质量 | 中文支持 | 易用性 | 推荐场景 |
|------|---------|---------|---------|--------|---------|
| **ChatTTS** | ❌ 不支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中文对话TTS |
| **OpenVoice** | ✅ 支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **推荐：音色克隆** |
| **Coqui XTTS** | ✅ 支持 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 多语言克隆 |
| **SpeechBrain** | ✅ 支持 | N/A | N/A | ⭐⭐⭐ | 音色分析/识别 |

### 推荐组合

1. **最简单**：OpenVoice（端到端音色克隆）
2. **中文最佳**：OpenVoice 提取音色 + ChatTTS 生成
3. **多语言**：Coqui XTTS-v2

---

## 安装指南

### 环境要求

- Python 3.9+
- PyTorch 2.0+
- CUDA 11.8+（推荐GPU加速）

### 快速安装

```bash
# 创建虚拟环境
conda create -n voice-clone python=3.10
conda activate voice-clone

# 安装基础依赖
pip install torch torchaudio

# 安装各方案依赖
pip install chattts        # ChatTTS
pip install TTS            # Coqui TTS
pip install speechbrain    # SpeechBrain

# OpenVoice 需要从源码安装
git clone https://github.com/myshell-ai/OpenVoice.git
cd OpenVoice && pip install -e .
```

---

## 参考资源

- [ChatTTS GitHub](https://github.com/2noise/chattts)
- [OpenVoice GitHub](https://github.com/myshell-ai/OpenVoice)
- [Coqui TTS GitHub](https://github.com/coqui-ai/TTS)
- [SpeechBrain](https://speechbrain.github.io/)
- [pyannote-audio](https://github.com/pyannote/pyannote-audio)
- [ChatTTS_Speaker 音色库](https://github.com/6drf21e/ChatTTS_Speaker)

---

## License

本文档及示例代码采用 MIT 许可证。
