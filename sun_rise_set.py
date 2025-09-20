import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
from matplotlib.colors import to_rgb, LinearSegmentedColormap
from datetime import datetime, timedelta

# 加载数据
# 注意：根据CSV文件格式，手动添加列名
df = pd.read_csv('Sun_rise_set_2024.csv', names=['YYYY-MM-DD', 'RISE', 'TRAN.', 'SET'], skiprows=1)
df['Date'] = pd.to_datetime(df['YYYY-MM-DD'])
df['RISE_min'] = df['RISE'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
df['SET_min'] = df['SET'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
df['TRAN_min'] = df['TRAN.'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
df['Day_length_min'] = df['SET_min'] - df['RISE_min']
df['Dayofyear'] = df['Date'].dt.dayofyear

# 定义颜色段（用户要求的日期范围）
colors = ['#97E3FC', '#C3F87E', '#FDD874', '#E1C28D', '#97E3FC']
# 1月1日到3月1日，3月1日到6月1日，6月1日到9月1日，9月1日到12月31日
segments = [1, 60, 152, 245, 366]  # 2024年日期的天序

def get_background_color(dayofyear):
    for i in range(len(segments) - 1):
        start, end = segments[i], segments[i+1]
        if start <= dayofyear <= end:
            frac = (dayofyear - start) / (end - start)
            c_start = np.array(to_rgb(colors[i]))
            c_end = np.array(to_rgb(colors[i+1]))
            return tuple(c_start * (1 - frac) + c_end * frac)
    return to_rgb(colors[0])  # 默认

# 设置画布 - 使用GridSpec创建两个子图：上方为曲线图，下方为时间轴
fig = plt.figure(figsize=(12, 8))
from matplotlib.gridspec import GridSpec

gs = GridSpec(3, 1, height_ratios=[10, 1, 1])  # 曲线图:时间轴:信息显示

# 曲线图子图
ax_main = fig.add_subplot(gs[0])
ax_main.set_xlim(0, 1)  # 归一化时间轴 (0=00:00, 1=23:59)
ax_main.set_ylim(-1.1, 1.1)  # y轴范围
ax_main.set_xticks([])  # 无x轴数值
ax_main.set_yticks([])  # 无y轴
ax_main.spines['top'].set_visible(False)
ax_main.spines['right'].set_visible(False)
ax_main.spines['left'].set_visible(False)
ax_main.spines['bottom'].set_visible(False)
# 添加纯白色宽度为2的横轴直线，y=0居中
ax_main.plot([0, 1], [0, 0], color='white', linewidth=2, zorder=10)

# 添加0点、12点和24点的标记（归一化坐标）
time_marks = [0, 0.5, 1]  # 0点、12点、24点对应的归一化坐标
time_labels = ['0:00', '12:00', '24:00']

# 为每个时间点添加垂直线标记
for t in time_marks:
    ax_main.axvline(x=t, color='white', linestyle='--', linewidth=1, alpha=0.7, zorder=5)

# 添加时间标签
for t, label in zip(time_marks, time_labels):
    ax_main.text(t, 0.95, label, ha='center', va='top', color='white', fontsize=10, 
                 bbox=dict(facecolor='black', alpha=0.3, edgecolor='none', boxstyle='round,pad=0.3'), zorder=15)

# 时间轴子图
ax_time = fig.add_subplot(gs[1])
ax_time.set_xlim(0, len(df) - 1)  # 时间轴范围为数据天数
ax_time.set_ylim(-0.1, 0.1)  # 非常窄的y范围，只显示一条线
ax_time.set_yticks([])  # 无y轴
ax_time.spines['top'].set_visible(False)
ax_time.spines['right'].set_visible(False)
ax_time.spines['left'].set_visible(False)
ax_time.spines['bottom'].set_color('white')
ax_time.spines['bottom'].set_linewidth(2)

# 设置时间轴刻度和标签
# 每个月显示一个主刻度
month_positions = []
month_labels = []
current_month = df.iloc[0]['Date'].month
month_positions.append(0)
month_labels.append(df.iloc[0]['Date'].strftime('%b'))

for i in range(1, len(df)):
    if df.iloc[i]['Date'].month != current_month:
        month_positions.append(i)
        month_labels.append(df.iloc[i]['Date'].strftime('%b'))
        current_month = df.iloc[i]['Date'].month

if len(month_positions) < len(month_labels):
    month_positions.append(len(df)-1)
    month_labels.append(df.iloc[-1]['Date'].strftime('%b'))

ax_time.set_xticks(month_positions)
ax_time.set_xticklabels(month_labels, color='white', fontsize=10)

# 在时间轴上绘制数据点（不可见，仅用于交互）
time_axis_points = ax_time.scatter(range(len(df)), np.zeros(len(df)), s=20, alpha=0, picker=5)

# 底部信息文本显示 - 调整位置到时间轴下方约10px处
info_text = fig.text(0.5, 0.08, '', ha='center', va='top', fontsize=12, fontweight='bold', zorder=100)

# 曲线列表 (前后10天 + 当前 = 21条) - 线宽修改为原来的一半
lines = [ax_main.plot([], [], alpha=0, lw=1)[0] for _ in range(21)]

# 动画状态
current_day = 0
anim_running = True
hovered_day = None
fast_forwarding = False
fast_forward_target = -1

# 粉蓝渐变色映射
color_values = np.linspace(0, 1, 21)

# 改进后的generate_curve函数 - 确保曲线在整个0-24小时范围内完整显示
def generate_curve(row):
    # 将时间转换为归一化值 (0-1)
    rise_norm = row['RISE_min'] / 1440
    set_norm = row['SET_min'] / 1440
    tran_norm = row['TRAN_min'] / 1440
    
    # 生成0-24小时的完整x轴数据
    x = np.linspace(0, 1, 1000)  # 更多点使曲线更平滑
    
    # 计算三角函数曲线，确保日中天是最高点且曲线在整个0-24小时范围内完整
    # 1. 计算日出日落时间的中点
    center = (rise_norm + set_norm) / 2
    
    # 2. 计算日出日落时间的跨度
    length = set_norm - rise_norm
    
    # 3. 为整个0-24小时范围创建完整的正弦波形
    # 使用更宽的周期来确保曲线在日出前和日落后也有显示
    phase = 2 * np.pi * (x - center) / (length * 2)  # 扩展周期为两倍日长
    
    # 4. 创建基础正弦曲线
    y = np.sin(phase)
    
    # 5. 对曲线进行调制，确保日出日落处与x轴相交
    # 创建一个窗口函数，在日出前和日落后逐渐衰减
    window = np.ones_like(x)
    
    # 日出前的衰减区域
    sunrise_mask = x < rise_norm
    if np.any(sunrise_mask):
        # 计算从0到日出的归一化距离
        sunrise_dist = (x[sunrise_mask] - 0) / rise_norm
        # 使用二次曲线衰减，日出前逐渐减弱为0
        window[sunrise_mask] = np.sin(sunrise_dist * np.pi/2) ** 2
    
    # 日落后的衰减区域
    sunset_mask = x > set_norm
    if np.any(sunset_mask):
        # 计算从日落到24点的归一化距离
        sunset_dist = (1 - x[sunset_mask]) / (1 - set_norm)
        # 使用二次曲线衰减，日落后逐渐减弱为0
        window[sunset_mask] = np.sin(sunset_dist * np.pi/2) ** 2
    
    # 6. 应用窗口函数到曲线上
    y = y * window
    
    return x, y

def update(frame):
    global current_day, hovered_day, anim_running, fast_forwarding, fast_forward_target
    
    # 处理快速前进
    if fast_forwarding:
        # 计算当前天到目标天的最短路径
        if abs(current_day - fast_forward_target) <= 1:
            # 已经接近目标，停止快速前进
            current_day = fast_forward_target
            fast_forwarding = False
            anim_running = False
            anim.event_source.stop()
            # 显示信息
            display_day_info(current_day)
        else:
            # 继续快速前进（一次跳过多天）
            step = 5 if fast_forward_target > current_day else -5
            current_day = (current_day + step) % len(df)
    elif anim_running and hovered_day is None:
        # 正常动画速度：每秒5天
        current_day = (current_day + 1) % len(df)
    
    idx = current_day
    # 更新背景颜色
    bg_color = get_background_color(df.iloc[idx]['Dayofyear'])
    fig.patch.set_facecolor(bg_color)
    ax_main.set_facecolor(bg_color)
    ax_time.set_facecolor(bg_color)
    
    # 更新曲线
    for d in range(-10, 11):  # 前后10天
        day_idx = (idx + d) % len(df)
        row = df.iloc[day_idx]
        x, y = generate_curve(row)
        dist = abs(d)
        
        # 用户要求：当天透明度为0%（完全不透明），前后1天透明度为90%，以此类推到前后10天透明度为100%
        alpha = 1.0 - (dist * 0.1)
        
        # 为不同距离的曲线设置不同的颜色
        color = plt.cm.coolwarm(color_values[d + 10])
        
        lines[d + 10].set_data(x, y)
        lines[d + 10].set_alpha(alpha)
        lines[d + 10].set_color(color)
        lines[d + 10].set_zorder(20 - dist)  # 当前天zorder最高，距离越近zorder越高
    
    # 先清除之前的所有标记
    # 清除时间轴位置标记
    if hasattr(update, 'current_marker') and update.current_marker is not None:
        try:
            update.current_marker.remove()
        except Exception:
            pass  # 如果标记已经不存在，忽略错误
    # 清除日出日落日中天标记
    if hasattr(update, 'sunrise_line') and update.sunrise_line is not None:
        try:
            update.sunrise_line.remove()
        except Exception:
            pass
    if hasattr(update, 'sunset_line') and update.sunset_line is not None:
        try:
            update.sunset_line.remove()
        except Exception:
            pass
    if hasattr(update, 'suntran_line') and update.suntran_line is not None:
        try:
            update.suntran_line.remove()
        except Exception:
            pass
    # 清除文本标签
    if hasattr(update, 'sunrise_text') and update.sunrise_text is not None:
        try:
            update.sunrise_text.remove()
        except Exception:
            pass
    if hasattr(update, 'sunset_text') and update.sunset_text is not None:
        try:
            update.sunset_text.remove()
        except Exception:
            pass
    if hasattr(update, 'suntran_text') and update.suntran_text is not None:
        try:
            update.suntran_text.remove()
        except Exception:
            pass

    # 添加时间轴位置标记
    update.current_marker = ax_time.axvline(x=current_day, color='red', linewidth=2, zorder=5)

    # 为当前天添加日出、日落和日中天的水平线标记
    current_row = df.iloc[current_day]
    # 生成当前天的曲线数据来找到最高点和最低点
    current_x, current_y = generate_curve(current_row)
    
    # 最高点 (日中天) - 我们直接使用日中天时间而不是找曲线最大值，因为曲线可能有多个峰值
    tran_norm = current_row['TRAN_min'] / 1440
    # 日出时间 (最低点位置)
    rise_norm = current_row['RISE_min'] / 1440
    # 日落时间
    set_norm = current_row['SET_min'] / 1440
    
    # 找到日出时的y值（最低点）
    sunrise_y = current_y[np.argmin(np.abs(current_x - rise_norm))]
    # 找到日落时的y值（接近最高点）
    sunset_y = current_y[np.argmin(np.abs(current_x - set_norm))]
    # 日中天时的y值
    suntran_y = current_y[np.argmin(np.abs(current_x - tran_norm))]
    
    # 添加水平虚线
    update.sunrise_line = ax_main.axhline(y=sunrise_y, color='white', linestyle='--', linewidth=1, alpha=0.7, zorder=10)
    update.sunset_line = ax_main.axhline(y=sunset_y, color='white', linestyle='--', linewidth=1, alpha=0.7, zorder=10)
    update.suntran_line = ax_main.axhline(y=suntran_y, color='white', linestyle='-', linewidth=2, alpha=1.0, zorder=10)
    
    # 根据背景亮度调整文本颜色
    bg_color = get_background_color(current_row['Dayofyear'])
    bg_brightness = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]
    text_color = 'black' if bg_brightness > 0.5 else 'white'
    
    # 添加文本标签
    update.sunrise_text = ax_main.text(0.02, sunrise_y, 'sunrise', ha='left', va='center', color=text_color, fontsize=10,
                                      bbox=dict(facecolor='black', alpha=0.3, edgecolor='none', boxstyle='round,pad=0.3'), zorder=15)
    update.sunset_text = ax_main.text(0.02, sunset_y, 'sunset', ha='left', va='center', color=text_color, fontsize=10,
                                     bbox=dict(facecolor='black', alpha=0.3, edgecolor='none', boxstyle='round,pad=0.3'), zorder=15)
    update.suntran_text = ax_main.text(0.02, suntran_y, 'suntran', ha='left', va='center', color=text_color, fontsize=10,
                                      bbox=dict(facecolor='black', alpha=0.3, edgecolor='none', boxstyle='round,pad=0.3'), zorder=15)
    
    return lines + [update.current_marker, update.sunrise_line, update.sunset_line, update.suntran_line, update.sunrise_text, update.sunset_text, update.suntran_text]

# 显示日期信息的函数
def display_day_info(day_idx):
    try:
        row = df.iloc[day_idx]
        # 更新文本内容
        info_text.set_text(f'date: {row["Date"].strftime("%Y-%m-%d")} | sun rise: {row["RISE"]} | sun tran: {row["TRAN."]} | sun set: {row["SET"]}')
        
        # 根据背景亮度调整文本颜色
        bg_color = get_background_color(row['Dayofyear'])
        bg_brightness = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]
        text_color = 'black' if bg_brightness > 0.5 else 'white'
        info_text.set_color(text_color)
        info_text.set_bbox(dict(facecolor='white', alpha=0.9, edgecolor='none', boxstyle='round,pad=0.5'))
        
        # 强制刷新画布以显示文本
        fig.canvas.draw_idle()
    except IndexError:
        info_text.set_text('')

# 动画 - 每200ms更新一次，实现每秒钟过五天
anim = FuncAnimation(fig, update, interval=200, blit=False, cache_frame_data=False)

# 初始化所有标记属性
update.current_marker = None
update.sunrise_line = None
update.sunset_line = None
update.suntran_line = None
update.sunrise_text = None
update.sunset_text = None
update.suntran_text = None

# 鼠标移动事件处理函数
def on_motion(event):
    global hovered_day, anim_running
    
    # 检查是否在时间轴上悬停
    if event.inaxes == ax_time and event.xdata is not None:
        # 计算最接近的日期索引
        day_idx = int(round(event.xdata))
        day_idx = max(0, min(day_idx, len(df) - 1))
        
        if hovered_day != day_idx:
            hovered_day = day_idx
            # 显示日期信息
            display_day_info(hovered_day)
        
        # 如果鼠标悬停在时间轴上且动画正在运行，暂停动画
        if anim_running:
            anim_running = False
            try:
                anim.event_source.stop()
            except Exception:
                pass  # 忽略可能的错误
    else:
        # 不在时间轴上，清除悬停状态并恢复动画播放
        if hovered_day is not None:
            hovered_day = None
            info_text.set_text('')
            info_text.set_bbox(dict(facecolor='none', edgecolor='none'))
        
        # 如果鼠标不在时间轴上且动画未运行，恢复动画
        if not anim_running and not fast_forwarding:
            anim_running = True
            try:
                anim.event_source.start()
            except Exception:
                pass  # 忽略可能的错误

# 鼠标点击事件处理函数（用于时间轴交互）
def on_click(event):
    global fast_forwarding, fast_forward_target, anim_running
    
    # 检查是否点击了时间轴
    if event.inaxes == ax_time and event.xdata is not None:
        # 计算目标日期索引
        target_day = int(round(event.xdata))
        target_day = max(0, min(target_day, len(df) - 1))
        
        if target_day != current_day:
            # 开始快速跳转到目标日期
            fast_forwarding = True
            fast_forward_target = target_day
            anim_running = True  # 确保动画运行以便处理快速跳转
            try:
                # 不管动画是否在运行，都尝试启动它来处理快速跳转
                anim.event_source.start()
            except Exception:
                pass  # 忽略可能的错误
        else:
            # 如果已经在目标日期，直接暂停
            anim_running = False
            try:
                anim.event_source.stop()
            except Exception:
                pass  # 忽略可能的错误

# 连接事件处理函数
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_press_event', on_click)

# 设置布局
plt.tight_layout(rect=[0, 0.05, 1, 0.98])

# 显示图形
plt.show()
