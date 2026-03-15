AutoVJ是一款自动VJ的小程序

\## 需要注意 VDJ25版本以上的，可能需要手动修改下M3U历史路径为C:\Users\(你的电脑用户名)\AppData/Local/VirtualDJ  的目录下，如果显示端口占用的话也要改下端口。

\## 🔥 核心特性 (Core Features)



\### 1. 🎵 智能音视频同步引擎 (Auto Audio-Video Sync)

突破传统本地 VJ 软件的限制，实现网络搜索视频音画同步，且可完美叠加本地 VJ 素材图层。

\- \*\*精准匹配:\*\* 自动根据当前播放的歌曲信息搜索 Bilibili 视频，并同屏至独立的渲染窗口。

\- \*\*时长自适应:\*\* 算法自动筛选与音频时长最接近的视频源，底层预处理视频轨道长度（Pitch/Rate 动态变速），使其与 VDJ 音频严丝合缝地物理对齐。



\### 2. 📺 动力学全息监视器 (Cyber-Hardware HUD)

系统内置了对标专业机甲 UI 的白色工业级硬件监视器：

\- 实时绘制双碟机 (Deck 1 / Deck 2) 的 15 格动态 VU 音量电平表。

\- 毫秒级无延迟同步 VDJ 内部的 \*\*BPM、高中低频 EQ 状态



\### 3. 🌐 终极三核云端素材引擎

\- \*\*图层分离:\*\* VJ1 负责底层氛围背景（如星空、隧道），VJ2 负责前景粒子特效（如漏光、故障噪点）。

\- \*\*智能爬虫兜底:\*\* 当本地文件夹未命中合适素材时，引擎会根据当前曲风 (如 Dubstep, Trance) 自动唤醒后台物理隔离的 `undetected\_chromedriver`，潜入 Bilibili 静默搜索并挂载循环视觉素材。



\---



\## 🎮 面向 VJ/DJ：开箱即用指南 (User Guide)



无需懂任何代码，跟随以下步骤即可将这套强大的引擎接入你的演出工作流。



\### 📥 1. 下载与准备

1\. 前往 \[Releases 面板](../../releases) 下载最新的免安装绿色压缩包 `VDJ\_Visual\_Pro\_Max\_v600.zip`。

2\. 解压到任意\*\*不包含中文\*\*的路径下。



\### ⚠️ 2. 检查核心驱动 (极其重要)

为了保证引擎的云端抓取与音视频合轨功能正常，请确保解压后的文件夹内必须包含以下两个环境文件：

1\. \*\*`chromedriver.exe`\*\*: 请确保它的版本与你电脑上安装的 Google Chrome 浏览器版本严格一致。\[官网下载地址](https://googlechromelabs.github.io/chrome-for-testing/)。

2\. \*\*`ffmpeg.exe`\*\*: 负责底层视频与音频的高速无损合轨，必须和主程序放在同一个文件夹内。\[下载地址](https://github.com/BtbN/FFmpeg-Builds/releases)。



\### 🗂️ 3. 本地素材库挂载 (可选但强烈推荐)

程序根目录下有这两个文件夹，请放入你自己的循环视频（建议使用 `.mp4` 格式，h.264 编码，1080P，以降低 CPU 负载）：

\- `vj\_materials\_vj1/`：放入底层背景视频（例如：抽象几何、舞台灯光、隧道穿梭）。

\- `vj\_materials\_vj2/`：放入前景特效视频（例如：下雨、粒子光斑、老电视噪点、VHS 漏光）。



\### 🚀 4. 启动引擎

1\. 首先打开你的 \*\*VirtualDJ\*\* 软件，随便加载一首歌。

2\. 双击运行 `VDJ\_Visual\_Pro\_Max.exe`。

3\. 软件会弹出控制中心面板，并自动连接 VDJ。如果在 Log 区域看到 `✅ 音频节点握手成功`，说明连接正常。

4\. 点击面板下方的 \*\*“弹射渲染大屏”\*\*。

5\. 打开 \*\*OBS Studio\*\*，添加一个【窗口采集】，选择弹出的黑色渲染大屏窗口，满屏铺满，即可开始 Live 演出！

6\. 注意如果要关掉两个层，只留下视频源素材的视频层的话，要把全局动态透明度呼吸混合给关了

注意，要在vdj下把拓展插件network control给安装了，端口设置为80，且historyDelay设置为2，表示切歌后两秒识别为下一首歌切换

\---



\## 🎛️ 主控面板参数说明 (Control Panel Guide)



\- \*\*SYSTEM MATRIX (系统矩阵):\*\*

&#x20; - `本地图层库 / 云端VJ层`：控制素材来源。如果关闭云端，系统将只播放你本地文件夹里的内容。

&#x20; - `终极三核混合`：决定是否开启 VJ2 粒子特效层。关闭可大幅节省旧电脑的 CPU/GPU 资源。

&#x20; - `智能鼓点编排引擎`：打开后将接管画面的物理冲击感。

\- \*\*PRO VJ RACK (专业视觉效果器):\*\*

&#x20; - `硬件混音台状态监测`：打开/关闭画面底部的白色工业级音量、Loop、FX 状态字牌。

&#x20; - `物理变形引擎`：允许系统在底鼓 (Kick) 敲击时对画面进行动态镜像、缩放弹跳和旋转。

&#x20; - `色彩与故障`：军鼓 (Snare) 触发画面撕裂，底鼓触发霓虹色域映射和高能爆闪。

&#x20; - `图层透明度调音台`：强制干预 VJ1 和 VJ2 的基础亮度，支持使用旁边的绿色按钮一键关闭某一图层。



\---



\## 🛠️ 面向开发者：二次开发与编译指南 (Dev Guide)



本项目完全使用 Python 原生开发，没有任何外部重量级框架依赖，架构极致轻量。欢迎任何 Python 开发者、交互设计师参与共建。



\### 1. 架构简述

\- \*\*通信层 (`VDJPoller` \& `VJStateManager`):\*\* 利用 `requests.Session()` 维护 HTTP 长连接，以极低延迟高频轮询 VDJ `127.0.0.1:80/query` 接口。

\- \*\*爬虫层 (`MultiBrowserManager`):\*\* 封装了 `undetected\_chromedriver` 与 `yt-dlp`，实现多线程、反风控的视频流直链提取与本地极速缓存机制。

\- \*\*渲染层 (`KineticHUDSystem` \& `OBSVideoWindow`):\*\* 依托 `PyQt6.QGraphicsScene` 打造的软解视频混合矩阵，通过数学插值 (`Lerp`) 实现丝滑的物理阻尼动效。



\### 2. 环境搭建 (Environment Setup)

确保你的 Python 版本为 \*\*3.10+\*\*。推荐使用虚拟环境进行隔离开发：



```bash

\# 1. 克隆项目

git clone \[https://github.com/你的用户名/VDJ-Visual-Pro-Max.git](https://github.com/你的用户名/VDJ-Visual-Pro-Max.git)

cd VDJ-Visual-Pro-Max



\# 2. 创建并激活虚拟环境 (Windows)

python -m venv venv

.\\venv\\Scripts\\activate



\# 3. 安装项目依赖清单

pip install -r requirements.txt
