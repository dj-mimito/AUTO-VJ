AUTOVJ是一个自动同步VJ的小程序

\---



\## 🔥 核心特性 (Core Features)



\### 1. 🎵 自动同步音视频，实现网络搜索视频音画同步，且可叠加本地VJ素材图层。
搜索B站视频并同屏至一个新窗口，时长约接近音频时长越匹配，原理是预处理视频轨道长度使得其跟音频一致。



\### 2. 📺 动力学全息监视器 (Cyber-Hardware HUD)

抛弃土味的文字叠加，系统内置了对标专业机甲 UI 的白色工业级监视器：

\- 实时绘制双碟机 (Deck 1 / Deck 2) 的 15 格动态 VU 音量电平表。

\- 毫秒级无延迟同步 VDJ 内部的 \*\*BPM、高中低频 EQ 状态、Loop 循环锁定状态、FX 效果器挂载数量\*\*。



\### 3. 🌐 终极三核云端素材引擎

\- 图层分离: VJ1 负责底层氛围背景（如星空、隧道），VJ2 负责前景粒子特效（如漏光、故障噪点）。

\- 智能爬虫兜底: 当本地文件夹未命中合适素材时，引擎会根据当前曲风 (如 Dubstep, Trance) 自动唤醒后台隔离的 `undetected\_chromedriver`，潜入 Bilibili 静默搜索并挂载 4K 无水印循环素材。



\---



\## 🎮 面向 VJ/DJ：开箱即用指南 (User Guide)



无需懂任何代码，跟随以下步骤即可将这套强大的引擎接入你的演出工作流。



\### 📥 1. 准备工作

1\. 在 \[Releases 面板](../../releases) 下载最新的免安装绿色压缩包 `VDJ\_Visual\_Pro\_Max\_v600.zip`。

2\. 解压到任意不包含中文路径的文件夹中。

3\. \*\*环境硬性要求：\*\* - 你的电脑必须安装了 Google Chrome 浏览器。

&#x20;  - 请检查你电脑上 Chrome 的版本，并前往官方下载对应版本的 `chromedriver.exe`，替换掉压缩包内的同名文件。



\### 🗂️ 2. 本地素材库挂载 (可选但强烈推荐)

程序根目录下有这两个文件夹，请放入你自己的循环视频（建议使用 `.mp4` h.264 编码，1080P，以降低 CPU 负载）：

\- `vj\_materials\_vj1/`：放入底层背景视频（例如：抽象几何、舞台灯光、隧道穿梭）。

\- `vj\_materials\_vj2/`：放入前景特效视频（例如：下雨、粒子光斑、老电视噪点、VHS 漏光）。



\### 🚀 3. 启动引擎

1\. 首先打开你的 \*\*VirtualDJ\*\* 并随便加载一首歌。

2\. 双击运行 `VDJ\_Visual\_Pro\_Max.exe`。

3\. 软件会弹出控制中心面板，并自动连接 VDJ。如果在 Log 区域看到 `✅ 音频节点握手成功`，说明连接正常。

4\. 点击面板下方的 \*\*“弹射渲染大屏”\*\*。

5\. 打开 \*\*OBS Studio\*\*，添加一个【窗口采集】，选择刚刚弹出的黑色渲染窗口，满屏铺满，即可开始你的 Live 演出！



\---



\## 🎛️ 主控面板参数说明 (Control Panel Guide)



\- \*\*SYSTEM MATRIX (系统矩阵):\*\*

&#x20; - `本地图层库 / 云端VJ层`：控制素材来源。如果关闭云端，系统将只播放你本地文件夹里的内容。

&#x20; - `终极三核混合`：决定是否开启 VJ2 粒子特效层。关闭可大幅节省旧电脑的 CPU/GPU 资源。

\- \*\*PRO VJ RACK (专业视觉效果器):\*\*

&#x20; - `硬件混音台状态监测`：打开/关闭画面底部的白色工业级音量、Loop、FX 状态字牌。

&#x20; - `物理变形引擎`：允许系统在底鼓敲击时对画面进行缩放和旋转。

&#x20; - `图层透明度调音台`：强制干预 VJ1 和 VJ2 的基础亮度，支持一键单独关闭某一图层。



\---



\## 🛠️ 面向开发者：二次开发与编译指南 (Dev Guide)



本项目欢迎任何 Python 开发者、交互设计师或新媒体艺术家参与共建。



\### 1. 架构简述

本项目完全使用 Python 原生开发，没有任何外部重量级框架依赖，极致轻量：

\- \*\*通信层 (`VDJPoller` \& `VJStateManager`):\*\* 利用 `requests.Session()` 维护 HTTP 长连接，以 60FPS 的极低延迟轮询 VDJ `127.0.0.1:80/query` 接口。

\- \*\*爬虫层 (`MultiBrowserManager`):\*\* 封装了 `undetected\_chromedriver` 与 `yt-dlp`，实现多线程、反风控的视频流直链提取与本地极速缓存机制。

\- \*\*渲染层 (`KineticHUDSystem` \& `OBSVideoWindow`):\*\* 依托 `PyQt6.QGraphicsScene` 打造的软解视频混合矩阵，通过数学差值 (`Lerp`) 实现丝滑的物理阻尼动效。



\### 2. 环境搭建

```bash

\# 1. 克隆项目

git clone \[https://github.com/你的用户名/VDJ-Visual-Pro-Max.git](https://github.com/你的用户名/VDJ-Visual-Pro-Max.git)

cd VDJ-Visual-Pro-Max



\# 2. 创建并激活虚拟环境 (推荐)

python -m venv venv

.\\venv\\Scripts\\activate



\# 3. 安装核心依赖

pip install PyQt6 requests yt-dlp undetected-chromedriver selenium mutagen

