# OpenBCI Realtime EEG Desktop

基于 BrainFlow、PySide6、PyQtGraph 的 OpenBCI Cyton 实时 EEG 桌面应用工程。

## 功能

- 支持 BrainFlow Synthetic Board，方便无硬件开发。
- 支持 OpenBCI Cyton 串口连接路径。
- 8 通道实时 EEG 波形显示。
- 实时带通、陷波、Welch PSD、频带能量计算。
- PSD 曲线和 Delta/Theta/Alpha/Beta/Gamma 频带能量显示。
- 配置持久化和 CSV 录制模块骨架。
- 关闭窗口或停止采集时执行 `stop_stream()` 和 `release_session()`。

## 运行

先在你自己的 Python 环境中安装依赖：

```powershell
pip install -r requirements.txt
```

启动应用：

```powershell
python -m openbci_realtime_app.main
```

默认使用 Synthetic Board。连接真实 Cyton 前，请切换到 `cyton` 模式并选择正确串口。

## 测试

```powershell
python -m pytest openbci_realtime_app\tests
```

