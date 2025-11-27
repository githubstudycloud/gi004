"""
OpenVoice 音色克隆实现

特点：
1. 音色与内容分离
2. 先用基础TTS生成语音，再转换音色
3. 支持从任意音频提取音色
"""

import os
import sys
from pathlib import Path
from typing import Union, Optional
import shutil

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.base import VoiceClonerBase, VoiceEmbedding
from common.utils import ensure_dir, get_device, generate_voice_id


class OpenVoiceCloner(VoiceClonerBase):
    """
    OpenVoice 音色克隆器

    工作流程:
    1. extract_voice(): 从参考音频提取音色嵌入
    2. synthesize(): 使用基础TTS生成语音，然后转换为目标音色

    注意：OpenVoice 需要一个基础TTS来生成初始语音，
    然后用音色转换器转换为目标音色。
    """

    ENGINE_NAME = "openvoice"
    SUPPORTED_LANGUAGES = ["zh", "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "ja", "hu", "ko"]

    def __init__(
        self,
        model_path: str = None,
        device: str = None,
        base_tts: str = "edge-tts"  # 基础TTS引擎
    ):
        """
        初始化 OpenVoice

        Args:
            model_path: 模型路径 (checkpoints_v2/)
            device: 计算设备
            base_tts: 基础TTS引擎 ('edge-tts' / 'openvoice')
        """
        super().__init__(model_path, device)
        self.base_tts = base_tts
        self.device = device or get_device()

        # 模型组件
        self.tone_color_converter = None
        self.base_speaker_se = None
        self.se_extractor = None

    def load_model(self):
        """加载 OpenVoice 模型"""
        try:
            from openvoice import se_extractor
            from openvoice.api import ToneColorConverter
        except ImportError:
            raise ImportError(
                "OpenVoice 未安装。请运行:\n"
                "  git clone https://github.com/myshell-ai/OpenVoice.git\n"
                "  cd OpenVoice && pip install -e ."
            )

        import torch

        model_path = self.model_path or "checkpoints_v2/converter"
        config_path = f"{model_path}/config.json"
        ckpt_path = f"{model_path}/checkpoint.pth"

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"模型配置不存在: {config_path}\n"
                "请下载模型: https://huggingface.co/myshell-ai/OpenVoiceV2"
            )

        print(f"[OpenVoice] 加载模型: {model_path}")

        # 加载音色转换器
        self.tone_color_converter = ToneColorConverter(config_path, device=self.device)
        self.tone_color_converter.load_ckpt(ckpt_path)

        # 加载基础说话人音色
        base_se_path = f"{self.model_path or 'checkpoints_v2'}/base_speakers/ses/zh.pth"
        if os.path.exists(base_se_path):
            self.base_speaker_se = torch.load(base_se_path, map_location=self.device)

        self.se_extractor = se_extractor
        self._model_loaded = True
        print(f"[OpenVoice] 模型加载完成，设备: {self.device}")

    def extract_voice(
        self,
        audio_path: str,
        voice_id: str = None,
        voice_name: str = "",
        save_dir: str = "./voices"
    ) -> VoiceEmbedding:
        """
        从音频提取音色

        Args:
            audio_path: 参考音频路径
            voice_id: 音色ID（可选，自动生成）
            voice_name: 音色名称
            save_dir: 保存目录

        Returns:
            VoiceEmbedding 对象
        """
        import torch

        self.ensure_loaded()

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        voice_id = voice_id or generate_voice_id()
        voice_dir = ensure_dir(Path(save_dir) / voice_id)

        print(f"[OpenVoice] 提取音色: {audio_path}")

        # 提取音色嵌入
        target_se, audio_name = self.se_extractor.get_se(
            audio_path,
            self.tone_color_converter,
            vad=True
        )

        # 保存嵌入
        embedding_path = voice_dir / "embedding.pt"
        torch.save(target_se, embedding_path)

        # 复制原始音频作为参考
        ref_audio_path = voice_dir / f"reference{Path(audio_path).suffix}"
        shutil.copy2(audio_path, ref_audio_path)

        # 创建音色对象
        voice = VoiceEmbedding(
            voice_id=voice_id,
            name=voice_name or voice_id,
            source_audio=str(ref_audio_path),
            embedding_path=str(embedding_path),
            engine=self.ENGINE_NAME,
            metadata={"embedding_shape": list(target_se.shape)}
        )

        # 保存元数据
        voice.save_meta(voice_dir / "voice.json")

        print(f"[OpenVoice] 音色已保存: {voice_dir}")
        return voice

    def synthesize(
        self,
        text: str,
        voice: Union[VoiceEmbedding, str],
        output_path: str,
        language: str = "zh"
    ) -> str:
        """
        使用音色合成语音

        Args:
            text: 文本内容
            voice: VoiceEmbedding 或音色目录路径
            output_path: 输出路径
            language: 语言

        Returns:
            输出文件路径
        """
        import torch
        import tempfile

        self.ensure_loaded()

        # 加载音色
        if isinstance(voice, str):
            voice = self.load_voice(voice)

        # 加载音色嵌入
        target_se = torch.load(voice.embedding_path, map_location=self.device)

        # 步骤1: 使用基础TTS生成语音
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            base_audio_path = tmp.name

        print(f"[OpenVoice] 生成基础语音...")
        self._generate_base_audio(text, base_audio_path, language)

        # 步骤2: 提取基础语音的音色（用于转换）
        source_se, _ = self.se_extractor.get_se(
            base_audio_path,
            self.tone_color_converter,
            vad=False
        )

        # 步骤3: 转换音色
        print(f"[OpenVoice] 转换音色...")
        ensure_dir(Path(output_path).parent)

        self.tone_color_converter.convert(
            audio_src_path=base_audio_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=output_path
        )

        # 清理临时文件
        os.unlink(base_audio_path)

        print(f"[OpenVoice] 合成完成: {output_path}")
        return output_path

    def _generate_base_audio(self, text: str, output_path: str, language: str):
        """
        使用基础TTS生成语音

        Args:
            text: 文本
            output_path: 输出路径
            language: 语言
        """
        if self.base_tts == "edge-tts":
            self._generate_with_edge_tts(text, output_path, language)
        else:
            raise ValueError(f"不支持的基础TTS: {self.base_tts}")

    def _generate_with_edge_tts(self, text: str, output_path: str, language: str):
        """使用 edge-tts 生成基础语音"""
        try:
            import edge_tts
            import asyncio
        except ImportError:
            raise ImportError("请安装 edge-tts: pip install edge-tts")

        # 语言到声音的映射
        voice_map = {
            "zh": "zh-CN-XiaoxiaoNeural",
            "en": "en-US-AriaNeural",
            "ja": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural",
            "es": "es-ES-ElviraNeural",
        }

        voice = voice_map.get(language, "zh-CN-XiaoxiaoNeural")

        async def generate():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)

        asyncio.run(generate())


# 便捷函数
def create_cloner(model_path: str = None, device: str = None) -> OpenVoiceCloner:
    """
    创建 OpenVoice 克隆器

    Args:
        model_path: 模型路径
        device: 设备

    Returns:
        OpenVoiceCloner 实例
    """
    cloner = OpenVoiceCloner(model_path=model_path, device=device)
    cloner.load_model()
    return cloner
