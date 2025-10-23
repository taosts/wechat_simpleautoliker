# inspector.py 
from pywinauto.application import Application
import sys

try:
    # 直接连接到已知的“公众号”窗口
    print("正在直接连接到 '公众号' 窗口...")
    app = Application(backend="uia").connect(title="公众号", timeout=10)
    main_window = app.window(title="公众号")
    
    print("\n'公众号' 窗口连接成功！")
    print("窗口标题:", main_window.window_text())
    
    # 打印出“公众号”窗口内部所有子控件的详细信息
    print("\n--- 正在打印 '公众号' 窗口的所有子控件信息 ---")
    main_window.print_control_identifiers()
    print("\n--- 打印完毕 ---")
    
except Exception as e:
    print(f"\n发生错误: {e}")
    print("请确保'公众号'窗口已经手动打开并且可见。")

    sys.exit(1)
