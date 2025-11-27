"""
GPT-SoVITS 音色克隆实现

特点：
1. 中文效果最佳
2. 支持零样本（5秒）和微调（1分钟）
3. 需要运行独立的 API 服务

使用方式：
1. 启动 GPT-SoVITS API 服务
2. 调用本模块进行音色克隆
"""

import os
import sys
import json
import requests
import shutil
from pathlib import Path
from typing import Union, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.base import VoiceClonerBase, VoiceEmbedding
from common.utils import ensure_dir, generate_voice_id, validate_audio_file


class GPTSoVITSCloner(VoiceClonerBase):
    """
    GPT-SoVITS 音色克隆器

    通过 API 调用 GPT-SoVITS 服务。
    GPT-SoVITS 的"音色提取"实际上是保存参考音频和文本，
    合成时使用参考音频进行零样本克隆。
    """

    ENGINE_NAME = "gpt-sovits"
    SUPPORTED_LANGUAGES = ["zh", "en", "ja"]

    def __init__(
        self,
        api_host: str = "127.0.0.1",
        api_port: int = 9880,
        model_path: str = None,
        device: str = None
    ):
        """
        初始化 GPT-SoVITS

        Args:
            api_host: API 服务地址
            api_port: API 服务端口
            model_path: 未使用（GPT-SoVITS 通过服务加载模型）
            device: 未使用
        """
        super().__init__(model_path, device)
        self.api_host = api_host
        self.api_port = api_port
        self.base_url = f"http://{api_host}:{api_port}"
        self.session = requests.Session()

    def load_model(self):
        """检查 API 服务是否可用"""
        try:
            resp = self.session.get(f"{self.base_url}/", timeout=5)
            self._model_loaded = True
            print(f"[GPT-SoVITS] API 服务已连接: {self.base_url}")
        except requests.exceptions.ConnectionError:
            self._model_loaded = False
            print(f"[GPT-SoVITS] 警告: API 服务未运行")
            print(f"[GPT-SoVITS] 请先启动服务:")
            print(f"  cd GPT-SoVITS")
            print(f"  python api_v2.py -a {self.api_host} -p {self.api_port}")

    def extract_voice(
        self,
        audio_path: str,
        voice_id: str = None,
        voice_name: str = "",
        save_dir: str = "./voices",
        reference_text: str = ""
    ) -> VoiceEmbedding:
        """
        保存音色（GPT-SoVITS 保存参考音频和文本）

        Args:
            audio_path: 参考音频路径（3-10秒，清晰）
            voice_id: 音色ID
            voice_name: 音色名称
            save_dir: 保存目录
            reference_text: 参考音频对应的文本（重要！）

        Returns:
            VoiceEmbedding 对象
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        if not validate_audio_file(audio_path):
            raise ValueError(f"无效的音频文件: {audio_path}")

        voice_id = voice_id or generate_voice_id()
        voice_dir = ensure_dir(Path(save_dir) / voice_id)

        print(f"[GPT-SoVITS] 保存音色: {audio_path}")

        # 复制参考音频
        ref_audio_path = voice_dir / f"reference{Path(audio_path).suffix}"
        shutil.copy2(audio_path, ref_audio_path)

        # 保存参考文本
        ref_text_path = voice_dir / "reference_text.txt"
        with open(ref_text_path, 'w', encoding='utf-8') as f:
            f.write(reference_text)

        # 创建音色对象
        voice = VoiceEmbedding(
            voice_id=voice_id,
            name=voice_name or voice_id,
            source_audio=str(ref_audio_path),
            embedding_path=str(ref_audio_path),  # GPT-SoVITS 直接使用音频
            engine=self.ENGINE_NAME,
            metadata={
                "reference_text": reference_text,
                "reference_text_path": str(ref_text_path)
            }
        )

        voice.save_meta(voice_dir / "voice.json")

        print(f"[GPT-SoVITS] 音色已保存: {voice_dir}")
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
            text: 文本
            voice: VoiceEmbedding 或音色目录
            output_path: 输出路径
            language: 语言

        Returns:
            输出文件路径
        """
        self.ensure_loaded()

        # 加载音色
        if isinstance(voice, str):
            voice = self.load_voice(voice)

        # 获取参考文本
        reference_text = voice.metadata.get("reference_text", "")

        print(f"[GPT-SoVITS] 合成语音: {text[:30]}...")

        # 调用 API
        payload = {
            "text": text,
            "text_lang": language,
            "ref_audio_path": voice.source_audio,
            "prompt_text": reference_text,
            "prompt_lang": language
        }

        try:
            resp = self.session.post(
                f"{self.base_url}/tts",
                json=payload,
                timeout=120
            )

            if resp.status_code == 200:
                ensure_dir(Path(output_path).parent)
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                print(f"[GPT-SoVITS] 合成完成: {output_path}")
                return output_path
            else:
                raise Exception(f"API 错误: {resp.status_code} - {resp.text}")

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"无法连接到 GPT-SoVITS 服务 {self.base_url}\n"
                "请确保服务已启动"
            )

    def synthesize_with_audio(
        self,
        text: str,
        reference_audio: str,
        reference_text: str,
        output_path: str,
        language: str = "zh"
    ) -> str:
        """
        直接使用参考音频合成（不保存音色）

        Args:
            text: 文本
            reference_audio: 参考音频
            reference_text: 参考文本
            output_path: 输出路径
            language: 语言

        Returns:
            输出路径
        """
        self.ensure_loaded()

        print(f"[GPT-SoVITS] 直接克隆合成...")

        payload = {
            "text": text,
            "text_lang": language,
            "ref_audio_path": reference_audio,
            "prompt_text": reference_text,
            "prompt_lang": language
        }

        resp = self.session.post(
            f"{self.base_url}/tts",
            json=payload,
            timeout=120
        )

        if resp.status_code == 200:
            ensure_dir(Path(output_path).parent)
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            print(f"[GPT-SoVITS] 合成完成: {output_path}")
            return output_path
        else:
            raise Exception(f"API 错误: {resp.status_code}")

    def set_model(
        self,
        gpt_model_path: str = None,
        sovits_model_path: str = None
    ):
        """
        切换模型（用于微调模型）

        Args:
            gpt_model_path: GPT 模型路径
            sovits_model_path: SoVITS 模型路径
        """
        payload = {}
        if gpt_model_path:
            payload["gpt_model_path"] = gpt_model_path
        if sovits_model_path:
            payload["sovits_model_path"] = sovits_model_path

        if not payload:
            return

        resp = self.session.post(
            f"{self.base_url}/set_model",
            json=payload,
            timeout=60
        )

        if resp.status_code == 200:
            print(f"[GPT-SoVITS] 模型切换成功")
        else:
            raise Exception(f"模型切换失败: {resp.text}")


# 便捷函数
def create_cloner(
    api_host: str = "127.0.0.1",
    api_port: int = 9880
) -> GPTSoVITSCloner:
    """
    创建 GPT-SoVITS 克隆器

    Args:
        api_host: API 地址
        api_port: API 端口

    Returns:
        GPTSoVITSCloner 实例
    """
    cloner = GPTSoVITSCloner(api_host=api_host, api_port=api_port)
    cloner.load_model()
    return cloner
