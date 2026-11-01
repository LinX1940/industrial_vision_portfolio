from dataclasses import dataclass, field
import datetime
from typing import Dict, Any, Optional


@dataclass
class ImageRecord:
  """工业视觉图像记录类（ImageRecord）

  用于封装单张采集图像的元数据，包括文件路径、空间尺寸、
  硬件采集条件（如曝光、增益）以及时间戳。
  """

  file_path: str
  width: int
  height: int
  capture_params: Dict[str, Any] = field(default_factory=dict)
  timestamp: str = field(
      default_factory=lambda: datetime.datetime.now().strftime(
          "%Y-%m-%d %H:%M:%S"
      )
  )

  def get_resolution_summary(self) -> str:
    """返回图像的分辨率摘要字符串。"""
    return f"{self.width}x{self.height}"

  def update_capture_param(self, key: str, value: Any) -> None:
    """动态更新或添加某项采集条件参数（如曝光时间、增益等）。"""
    self.capture_params[key] = value
    print(f"[Info] 参数已更新: {key} = {value}")

  def display_info(self) -> None:
    """打印该图像记录的完整元数据信息。"""
    print("=" * 40)
    print(f"图像路径 : {self.file_path}")
    print(f"分辨率   : {self.get_resolution_summary()}")
    print(f"采集时间 : {self.timestamp}")
    print(f"采集参数 : {self.capture_params}")
    print("=" * 40)


def main():
  # 实例化一个工业图像记录对象
  record = ImageRecord(
      file_path="outputs/demo_stream.mp4", width=640, height=480
  )

  # 调用实例方法更新采集条件
  record.update_capture_param("exposure_time_ms", 15.5)
  record.update_capture_param("gain_db", 6.0)

  # 调用实例方法展示完整信息
  record.display_info()


if __name__ == "__main__":
  main()