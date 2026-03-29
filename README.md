AutoVJ是一款自动VJ的小程序

\## 需要注意 VDJ25版本以上的，可能需要手动修改下M3U历史路径为C:\Users\(你的电脑用户名)\AppData/Local/VirtualDJ  的目录下，如果80端口被占用的话也要改下端口。改完路径和端口需要重开下软件。

\## 🔥 核心特性 (Core Features)

\### 1. 🎵 智能音视频同步引擎 (Auto Audio-Video Sync)

突破传统本地 VJ 软件的限制，实现网络搜索视频音画同步，且可完美叠加本地 VJ 素材图层。

\- \*\*精准匹配:\*\* 自动根据当前播放的歌曲信息搜索 Bilibili 视频，并同屏至独立的渲染窗口。

\- \*\*时长自适应:\*\* 算法自动筛选与音频时长最接近的视频源，底层预处理视频轨道长度（Pitch/Rate 动态变速），使其与 VDJ 音频严丝合缝地物理对齐。



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
