# main.py (相比V1.0增加转发功能)

import cv2
import numpy as np
import pyautogui
import time
import yaml
import os
import sys
import re
import locale
from datetime import date, timedelta
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError

def parse_date_string(date_str):
    """
    将多种格式的日期字符串转换为标准的 date 对象以便比较。
    """
    try:
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Chinese_China.936')
        except locale.Error:
            print("警告: 未找到 'zh_CN.UTF-8' 或 'Chinese_China.936' locale。星期解析可能失败。")

    today = date.today()
    if date_str == "今天": return today
    if date_str == "昨天": return today - timedelta(days=1)
    match = re.fullmatch(r"(\d{1,2})月(\d{1,2})日", date_str)
    if match:
        month, day = map(int, match.groups())
        return date(today.year, month, day)
    weekdays = {'星期一': 0, '星期二': 1, '星期三': 2, '星期四': 3, '星期五': 4, '星期六': 5, '星期日': 6}
    if date_str in weekdays:
        target_weekday = weekdays[date_str]
        days_ago = (today.weekday() - target_weekday + 7) % 7
        calculated_date = today - timedelta(days=days_ago)
        if calculated_date == today and date_str != "今天":
             calculated_date -= timedelta(days=7)
        return calculated_date
    return None

def get_last_processed_date(log_file_path):
    """
    从日志文件中读取最后一行，解析出日期并返回 date 对象。
    """
    if not os.path.exists(log_file_path): return None
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = [line for line in f if line.strip()]
            if not lines: return None
            last_line = lines[-1]
            match = re.match(r"^(.+?) - ", last_line)
            if match:
                date_str = match.group(1).strip()
                return parse_date_string(date_str)
    except Exception as e:
        print(f"读取日志文件日期时出错: {e}")
    return None

def load_config():
    """从 config.yml 文件中加载配置。"""
    try:
        with open('config.yml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("错误: 未找到 config.yml。请确保配置文件存在。"); sys.exit(1)
    except yaml.YAMLError as e:
        print(f"解析 config.yml 时出错: {e}"); sys.exit(1)

# --- 核心修改：重构文章处理函数 ---
def process_opened_article(config, mode):
    """
    处理文章内的逻辑：根据传入的 mode 执行不同操作。
    mode: 'like' (点赞收藏) 或 'forward' (转发)
    """
    print(f"\n--- 正在处理新文章 (模式: {mode}) ---")
    action_delay = config['timeouts']['action_delay']
    default_confidence = config['confidence']['default']
    
    time.sleep(config['timeouts']['article_load_delay'])

    if mode == 'like':
        # --- 模式1：点赞和收藏 (原有逻辑) ---
        try:
            like_location = pyautogui.locateCenterOnScreen(config['templates']['like'], confidence=default_confidence)
            if like_location: pyautogui.click(like_location); print("成功点击 '点赞'。"); time.sleep(action_delay)
        except pyautogui.ImageNotFoundException: print("未找到'点赞'按钮，可能已点赞或加载失败。")
        try:
            fav_location = pyautogui.locateCenterOnScreen(config['templates']['favorite'], confidence=default_confidence)
            if fav_location: pyautogui.click(fav_location); print("成功点击 '收藏'。"); time.sleep(action_delay)
        except pyautogui.ImageNotFoundException: print("未找到'收藏'按钮，可能已收藏或加载失败。")

    elif mode == 'forward':
        # --- 模式2：转发给文件传输助手 ---
        try:
            # 1. 点击转发按钮
            forward_location = pyautogui.locateCenterOnScreen(config['templates']['forward'], confidence=default_confidence)
            if forward_location:
                pyautogui.click(forward_location); print("成功点击 '转发'。")
                # 等待转发面板加载
                time.sleep(config['timeouts'].get('forward_pane_delay', 2))
                
                # 2. 点击文件传输助手 
                assistant_location = pyautogui.locateCenterOnScreen(config['templates']['file_assistant'], confidence=default_confidence)
                if assistant_location:
                    pyautogui.click(assistant_location); print("成功点击 '文件传输助手'。")
                    time.sleep(action_delay) # 等待发送按钮出现
                    
                    # 3. 点击发送 
                    send_location = pyautogui.locateCenterOnScreen(config['templates']['send'], confidence=default_confidence)
                    if send_location:
                        pyautogui.click(send_location); print("成功点击 '发送'。")


# <<< 核心修改：新增1.5秒延迟 >>>
                        print("等待发送操作完成...")
                        time.sleep(1.5) # 新增：等待发送弹窗消失，再执行关闭
                    else:
                        print("未找到'发送'按钮。")
                else:
                    print("未找到'文件传输助手'。")
            else:
                print("未找到'转发'按钮。")
        except pyautogui.ImageNotFoundException:
            print("转发流程中未找到所需图片。")
        except KeyError as e:
            print(f"配置错误: config.yml 中缺少转发模板路径 {e}。")

    # --- 公共逻辑：关闭文章  ---
    try:
        close_location = pyautogui.locateCenterOnScreen(config['templates']['close'], confidence=default_confidence)
        if close_location: pyautogui.click(close_location); print("成功点击 '关闭'。")
        else: print("未找到'关闭'按钮。")
    except pyautogui.ImageNotFoundException: print("未找到'关闭'按钮。")
    
    print("--- 文章处理完毕 ---"); time.sleep(1.5)


def main():
    config = load_config()
    total_processed_count = 0
    project_path = r'这里要换成自己的文件路径\wechat_autoliker' ###################看这里！
    log_file_path = os.path.join(project_path, 'processed_log.txt')
    
    # --- 开始时选择操作模式 ---
    operation_mode = ''
    while operation_mode not in ['1', '2']:
        print("\n" + "="*30)
        print("  请选择要执行的操作模式:")
        print("    1: 点赞和收藏 (默认)")
        print("    2: 转发给文件传输助手") 
    # 别的人也行，直接修改templates中的头像图片就好了，图片文件名保持不变。
        print("="*30)
        operation_mode = input("  请输入选项 (1 或 2): ").strip()

    if operation_mode == '1':
        operation_mode = 'like'
        print("\n[模式已选择：点赞和收藏]")
    else:
        operation_mode = 'forward'
        print("\n[模式已选择：转发给文件传输助手]")
    # ------------------------------------

    last_logged_date = get_last_processed_date(log_file_path)
    if last_logged_date: print(f"初始化成功。根据日志，上次处理到的日期为: {last_logged_date.strftime('%Y-%m-%d')}")
    else: print("初始化成功。未找到历史处理记录，将从头开始。")

    print(f"处理记录将保存在: {log_file_path}")
    print(f"启动微信自动点赞程序。按 Ctrl+C 停止。")

    try:
        app = Application(backend="uia").connect(title="公众号", timeout=10)
        main_window = app.window(title="公众号")
        main_window.set_focus()
        print("'公众号' 窗口连接成功！")
    except ElementNotFoundError:
        print("错误: 未找到 '公众号' 窗口。请确保您已手动打开该窗口。"); sys.exit(1)

    try:
        scroll_pane = main_window.child_window(control_type="Document")
        scroll_pane.wait('exists', timeout=10)
        print("内容窗格定位成功。")
    except (ElementNotFoundError, RuntimeError) as e:
        print(f"错误: 在 '公众号' 窗口内未找到可滚动的内容窗格(Document)。错误详情: {e} 程序终止。"); sys.exit(1)
    
    # --- 加载配置参数 ---
    processed_articles_texts = set()
    consecutive_no_new_articles_count = 0
    last_known_date_str = "未知日期"
    date_regex = r"^(今天|昨天|星期[一二三四五六日]|\d{1,2}月\d{1,2}日)$"
    article_regex = r"阅读.*赞.*"
    stability_config = config.get('stability', {})
    batch_size = stability_config.get('batch_size', 30)
    rest_duration = stability_config.get('rest_duration_seconds', 45)
    fast_forward_config = config.get('fast_forward', {})
    tool_run_duration = fast_forward_config.get('external_tool_run_duration', 8)
    tool_cooldown = fast_forward_config.get('external_tool_cooldown', 2)


    while True:
        if not main_window.exists():
            print("\n主窗口 '公众号' 已关闭，程序将正常退出。"); break

        try:
            # --- 侦察阶段 ---
            all_visible_proxies = scroll_pane.descendants(control_type="Text")
            screen_date_obj, screen_date_str = None, None
            for proxy in all_visible_proxies:
                if proxy.is_visible() and re.fullmatch(date_regex, proxy.window_text().strip()):
                    screen_date_str, screen_date_obj = proxy.window_text().strip(), parse_date_string(proxy.window_text().strip())
                    break
            
            # --- 决策阶段 ---
            if screen_date_obj and last_logged_date and screen_date_obj > last_logged_date:
                date_difference = (screen_date_obj - last_logged_date).days

                if date_difference > 15: # 差距巨大
                    print(f"调用外部追赶工具 (目标差距: {date_difference}天)。按 F10 启动...")
                    main_window.type_keys('{F10}')
                    print(f"外部工具运行中，等待 {tool_run_duration} 秒...")
                    time.sleep(tool_run_duration)
                    main_window.type_keys('{F12}')
                    print(f"按 F12 停止。冷却 {tool_cooldown} 秒后重新评估...")
                    time.sleep(tool_cooldown)
                else: # 差距中等，使用滚轮精炼
                    print(f"滚轮精炼定位模式 (目标差距: {date_difference}天)。执行大滚动...")
                    scroll_pane.wheel_mouse_input(wheel_dist=-20)
                    time.sleep(0.5) # 等待UI刷新
                
                # 失位重校准机制
                if not any(p.is_visible() and re.fullmatch(date_regex, p.window_text().strip()) for p in scroll_pane.descendants(control_type="Text")):
                    print(">> 滚动后失位！执行向上校准以重新定位...")
                    for attempt in range(10):
                        scroll_pane.wheel_mouse_input(wheel_dist=+8); time.sleep(0.5)
                        if any(p.is_visible() and re.fullmatch(date_regex, p.window_text().strip()) for p in scroll_pane.descendants(control_type="Text")):
                            print(">> 校准成功，已重新捕获日期！"); break
                    else: print(">> 警告: 校准失败。")
                
                continue # 

            # --- 正常处理模式 ---
            if screen_date_str: last_known_date_str = screen_date_str
            print(f"\n正常处理模式: 当前记忆日期 '{last_known_date_str}'。开始查找新文章...")
            new_articles_this_cycle = [p for p in all_visible_proxies if p.is_visible() and p.rectangle().width() > 0 and re.search(article_regex, p.window_text().strip()) and p.window_text().strip() not in processed_articles_texts]
            if not new_articles_this_cycle:
                consecutive_no_new_articles_count += 1; print("当前屏幕无新发现的文章。")
                if consecutive_no_new_articles_count >= 3: print("连续多次滚动未发现新内容，判定已到达页面底部。"); break
            else: consecutive_no_new_articles_count = 0
            print(f"本轮发现 {len(new_articles_this_cycle)} 篇新文章，开始处理...")
            for article_proxy in new_articles_this_cycle:
                current_text = article_proxy.window_text().strip()
                print(f"--- 正在处理文章: '{current_text}' (日期: {last_known_date_str}) ---")
                try:
                    # --- 核心修改：传入操作模式 ---
                    article_proxy.click_input(); process_opened_article(config, operation_mode)
                    
                    processed_articles_texts.add(current_text); total_processed_count += 1
                    with open(log_file_path, 'a', encoding='utf-8') as log_file:
                        log_file.write(f"{last_known_date_str} - {current_text}\n")
                    last_logged_date = parse_date_string(last_known_date_str)
                    if batch_size > 0 and total_processed_count % batch_size == 0:
                        print(f"\n{'='*56}\n批处理任务达成 (已处理 {total_processed_count} 篇文章)。\n系统将进入休眠 {rest_duration} 秒，以防止程序崩溃...\n{'='*56}")
                        time.sleep(rest_duration)
                        print("\n--- 休眠结束，恢复任务 ---\n")
                except Exception as e:
                    print(f"点击或处理文章时出错: {e}。将跳过此文章。"); time.sleep(1)
            print("\n执行页面滚动 (常规)...")
            scroll_pane.wheel_mouse_input(wheel_dist=-8) # 改滚动距离
            time.sleep(config['timeouts']['scroll_delay'])
        
        except ElementNotFoundError: print("\n主窗口在操作过程中消失，可能是被意外关闭。程序即将退出。"); break
        except Exception as e: import traceback; print(f"主循环发生严重错误: {e}"); traceback.print_exc(); break

    print(f"\n会话结束。共处理的文章数量：{total_processed_count}")

if __name__ == "__main__":
    main()