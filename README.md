# wechat_simpleautoliker
A simple script program, written in Python, uses a fusion of image recognition and simulated keyboard commands to automatically like and forward snacks on public account pages.
//一个简单的脚本程序，利用python编写，利用图像识别和模拟键盘指令融合的方式实现在公众号页面下自动点赞转发点心操作。
好的，这是为您转换和美化后的Markdown格式内容：

# 微信PC版“公众号”自动化处理脚本

> **前言：**
>
> 这个PYTHON脚本本来是用作给某个公众号的所有已发布文章进行自动化点赞转发点心的，后来经过证实：这个操作完全没意义。
> 不过整个程序经过多次迭代以后，整体运行良好，没什么BUG，所以保留下来做个纪念。
> 后续不会提供更新，本人不对代码造成的任何影响负责，项目脚本仅供学习使用。如果各位有更好的修改方案，请留个Comment给我，感谢各位。

这是一个专为 **Windows 11** 平台设计的微信PC版“公众号”自动化处理脚本。

它结合 `pywinauto` (基于UI元素) 和 `pyautogui` (基于图像识别) 两种技术模拟人工操作，自动浏览订阅号列表，并根据用户的选择，智能执行“点赞/收藏”或“转发给文件传输助手”等操作；能自动记录和读取日志，从上次中断的日期继续执行；当检测到进度落后时（如应用崩溃重启），自动追回进度。

## 用法

1.  **模式选择**：脚本启动时，会提示用户选择 `[1] 点赞/收藏` 或 `[2] 转发` 模式。

      * **模式1 (自动点赞/收藏)**: 自动打开文章，寻找并点击“点赞”和“收藏”图标。
      * **模式2 (自动转发)**: 自动打开文章，模拟点击“转发” -\> “文件传输助手” -\> “发送”。

2.  **状态记忆 (上下文感知)**：自动从 `processed_log.txt` 读取上次处理的最后日期，在滚动时能“记住”当前所属的日期（“粘性日期”），解决一屏内没有日期标题的问题。

3.  **两阶段智能追赶**：

      * **外部工具驱动 ( \> 15 天)**：当日期差距过大时 (如 \> 15天)，脚本自动按下 **F10** 键，调用按键精灵；在预设时间后，按 **F12** 停止，并重新评估进度。
      * **滚轮精炼定位 ( \<= 15 天)**：当日期差距较小时，切换为直接模拟小幅度的鼠标滚轮滚动，以精细定位。

4.  **容错机制**：

      * **失位重校准**：在高速滚动后如果“迷路”（找不到日期），会自动向上滚动以重新定位。
      * **智能休眠**：每成功处理一定数量的文章（如16篇），会自动休眠一段时间（如12秒），主要是防止微信程序因长时间高负荷运行而崩溃（这个问题困扰我很久）。

## 技术栈

  * Python 3.x
  * **pywinauto**: 用于Windows窗口句柄控制、元素定位和键盘操作（如连接窗口、发送F10/F12）。
  * **pyautogui**: 用于图像识别和鼠标模拟（如点击点赞、转发、发送按钮）。
  * **PyYAML**: 用于解析 `config.yml` 配置文件。
  * **OpenCV (cv2) / Numpy**: `pyautogui` 的底层依赖，用于图像处理。

## 安装设置与开始

1.  **准备环境**
    一个Python 3.x 环境 (如 `venv` 虚拟环境)。

2.  **安装依赖**
    在项目根目录下创建一个 `requirements.txt` 文件，内容如下：

    ```text
    pywinauto
    pyautogui
    pyyaml
    opencv-python
    numpy
    ```

    然后运行命令安装所有依赖：

    ```bash
    pip install -r requirements.txt
    ```

3.  **准备图像模板**
    这个脚本的运行严重依赖图像识别，因为我没有上传必要的识别要素图片，也就是UI，所以启动之前必须先手动截取以下UI元素的图片，并按文件名保存在项目根目录下的 `templates` 文件夹中。

    1.  `like.png` (点赞图标)
    2.  `favorite.png` (收藏图标)
    3.  `close.png` (文章页的关闭X按钮)
    4.  `forward.png` (文章页的转发图标)
    5.  `file_assistant.png` (转发面板中的“文件传输助手”)
    6.  `send.png` (转发确认面板中的绿色“发送”按钮)
    7.  `liked.png` (已点赞状态的图标)
    8.  `favorited.png` (已收藏状态的图标)

    **注意**： 截图时请尽量保持截图的简洁和高辨识度，这决定了图像识别的准确率。

4.  **准备外部滚动工具**
    安装脚本精灵，手动录制鼠标滚轮的下滚操作，然后设定由 **F10** 启动、**F12** 停止，脚本会在追踪不到当前日期时自动运行这个操作。

5.  **设置微信界面**
    登录微信，打开公众号页面（能看到日期，然后对应日期下的一条一条的文章那里。），将这个页面放在垂直水平居中位置，上下铺满，左右留空（防止程序误点到关闭按钮）。将桌面设置为不显示桌面图标，有条件的还可以下载个 `Hide Taskbar.exe` 隐藏下任务栏，反正正常运行这个挂机程序也不会再用电脑了。

6.  **编辑代码**
    将主代码和配置文件中的文件路径替换成自己的，已经做出标记。

7.  **运行脚本**
    以 **管理员模式** 进入PowerShell，调整大小到不会遮挡公众号页面，一般是放在屏幕左上角位置，然后CD进你保存这个脚本`main.py`的文件夹，接着开启虚拟python环境`venv\Scripts\activate`，然后`python main.py`，程序就会自动运行了。

    ```powershell
    # 示例命令：

    # 1. 切换到脚本目录
    cd C:\path\to\your\script\folder

    # 2. 激活虚拟环境
    .\venv\Scripts\activate

    # 3. 运行主程序
    python main.py
    ```

8.  **查BUG**
    你可以在文件夹内的 `processed_log.txt` 中找到你的脚本上一次运行的结尾日期，我也在代码中留了保存识别结果截图的选项，把对应的代码注释给解除就可以用了。
---

# WeChat PC "Official Accounts" Automation Script

> **Foreword:**
>
> This Python script was originally intended to automatically "Like," "Share," and "Favorite" all published articles from a specific Official Account. It was later confirmed that this operation is entirely meaningless.
> However, after many iterations, the overall program runs well with no significant bugs, so it is being kept as a memento.
> There will be no subsequent updates. I am not responsible for any impact caused by the code. The project script is only for learning purposes. If you have a better modification plan, please leave me a comment. Thank you.

This is an automation script designed specifically for the **Windows 11** PC version of WeChat, targeting "Official Accounts" (Subscriptions).

It combines `pywinauto` (UI element-based) and `pyautogui` (image recognition-based) techniques to simulate manual operation. It automatically browses the subscription feed, and based on user selection, intelligently executes "Like/Favorite" or "Forward to File Transfer Assistant." It can automatically log and read its progress, resuming from the last interrupted date, and will automatically catch up if it detects it has fallen behind (e.g., after an application crash and restart).

## Features

1.  **Mode Selection**: On launch, the script prompts the user to select either `[1] Like/Favorite` or `[2] Forward` mode.
    * **Mode 1 (Auto Like/Favorite)**: Automatically opens articles, finds, and clicks the "Like" and "Favorite" icons.
    * **Mode 2 (Auto Forward)**: Automatically opens articles, simulates clicking "Forward" -> "File Transfer Assistant" -> "Send".

2.  **State Memory (Context-Aware)**: Automatically reads the last processed date from `processed_log.txt`. While scrolling, it "remembers" the current date ("sticky date") to solve the issue of not having a date header visible on every screen.

3.  **Two-Stage Smart Catch-up**:
    * **External Tool Driven ( > 15 days)**: When the date gap is large (e.g., > 15 days), the script automatically presses the **F10** key to invoke an external macro tool (like AutoHotkey/QMacro); after a preset time, it presses **F12** to stop and re-evaluates the progress.
    * **Scroll Wheel Refinement ( <= 15 days)**: When the date gap is small, it switches to simulating small mouse wheel scrolls for fine-grained positioning.

4.  **Fault Tolerance**:
    * **Position Recalibration**: If it gets "lost" (can't find a date) after high-speed scrolling, it will automatically scroll up to re-orient itself.
    * **Smart Sleep**: After successfully processing a certain number of articles (e.g., 16), it will automatically sleep for a period (e.g., 12 seconds). This is mainly to prevent the WeChat application from crashing due to prolonged high-load operation (an issue that plagued me for a long time).

## Tech Stack

* Python 3.x
* **pywinauto**: Used for Windows handle control, element targeting, and keyboard operations (e..g., connecting to the window, sending F10/F12).
* **pyautogui**: Used for image recognition and mouse simulation (e.g., clicking Like, Forward, Send buttons).
* **PyYAML**: Used for parsing the `config.yml` configuration file.
* **OpenCV (cv2) / Numpy**: Underlying dependencies for `pyautogui`, used for image processing.

## Installation and Setup

1.  **Prepare Environment**
    A Python 3.x environment (e.g., a `venv` virtual environment).

2.  **Install Dependencies**
    Create a `requirements.txt` file in the project's root directory with the following content:

    ```text
    pywinauto
    pyautogui
    pyyaml
    opencv-python
    numpy
    ```

    Then, run the command to install all dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Prepare Image Templates**
    This script relies heavily on image recognition. Since I have not uploaded the necessary UI element images, you must manually take screenshots of the following UI elements before starting. Save them by file name in a `templates` folder in the project's root directory.

    1.  `like.png` (The 'Like' icon)
    2.  `favorite.png` (The 'Favorite' icon)
    3.  `close.png` (The 'X' close button on an article page)
    4.  `forward.png` (The 'Forward' icon on an article page)
    5.  `file_assistant.png` (The "File Transfer Assistant" in the forward panel)
    6.  `send.png` (The green "Send" button in the forward confirmation panel)
    7.  `liked.png` (The icon indicating 'Already Liked' status)
    8.  `favorited.png` (The icon indicating 'Already Favorited' status)

    **Note**: When taking screenshots, keep them as clean and distinct as possible. This directly determines the accuracy of the image recognition.

4.  **Prepare External Scrolling Tool**
    Install a macro/scripting tool (like QMacro), manually record a mouse wheel "scroll down" action, and set it to be triggered by **F10** and stopped by **F12**. The script will automatically run this action when it cannot find the current date.

5.  **Set Up WeChat Interface**
    Log in to WeChat, open the "Official Accounts" (Subscriptions) page (where you can see dates and the list of articles under them). Position this window centered vertically and horizontally, filling the screen from top to bottom but leaving space on the left and right (to prevent the script from accidentally clicking the close button). Set your desktop to hide icons. If possible, download and use `Hide Taskbar.exe` to hide the taskbar. You won't be using the computer while this script is running anyway.

6.  **Edit the Code**
    Replace the file paths in the main code and configuration files with your own. These locations have been marked.

7.  **Run the Script**
    Open PowerShell **in Administrator Mode**. Resize it so it doesn't obstruct the WeChat window (e.g., place it in the top-left corner). `cd` into the folder where you saved `main.py`. Activate your virtual environment (`venv\Scripts\activate`), and then run `python main.py`. The program will start automatically.

    ```powershell
    # Example commands:
    
    # 1. Change to the script directory
    cd C:\path\to\your\script\folder
    
    # 2. Activate the virtual environment
    .\venv\Scripts\activate
    
    # 3. Run the main program
    python main.py
    ```

8.  **Debugging**
    You can find the end date of the script's last run in the `processed_log.txt` file in the folder. I have also left an option in the code to save screenshots of recognition results; you can enable it by uncommenting the corresponding lines.

