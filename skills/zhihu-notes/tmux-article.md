# 【一眼就懂】Tmux 为什么是终端玩家的必备神器

> 如果你还在一个个开终端窗口，这篇文章帮你彻底搞懂什么叫"终端会话管理"。

## 背景

程序员日常是这样的：写代码的窗口、跑服务的窗口、看日志的窗口、SSH 连接的服务器——开着四五个终端，切换来切换去，关机重开还得一个个重建。

这就是 **Tmux** 要解决的问题。

Tmux（Terminal Multiplexer）是一个终端多路复用器，本质上是终端的"窗口管理器"。它让你在一个终端里管理多个会话，**断开 SSH 不丢工作**，**分屏不靠鼠标**，**会话可以挂着随时回来**。

---

## 核心概念：三个层级

理解 Tmux 先理解这三个东西：

| 概念 | 类比（类比窗口管理器） | 作用 |
|------|----------------------|------|
| **Session** | 工作空间 | 一个完整的工作环境，可以detach（挂起） |
| **Window** | 浏览器 Tab | 一个会话里的多个终端标签页 |
| **Pane** | VS Code 分屏 | 一个窗口里的多个面板 |

记住这个顺序：**Session > Window > Pane**

---

## 常用命令速查

### 会话管理

```bash
# 新建会话
tmux new -s mywork

# 断开当前会话（保留后台运行）
# 按 Ctrl+b 然后按 d

# 查看所有会话
tmux ls

# 回到某个会话
tmux attach -t mywork
# 缩写
tmux a -t mywork

# 杀掉会话
tmux kill-session -t mywork
```

### 窗口管理

| 按键 | 作用 |
|------|------|
| `Ctrl+b c` | 新建窗口 |
| `Ctrl+b 数字` | 跳到第 N 个窗口 |
| `Ctrl+b n / p` | 下一个 / 上一个窗口 |
| `Ctrl+b w` | 列出所有窗口（可视化选择） |
| `Ctrl+b ,` | 重命名当前窗口 |
| `Ctrl+b &` | 关闭当前窗口 |

### 分屏（Pane）

| 按键 | 作用 |
|------|------|
| `Ctrl+b %` | 垂直分屏（左右两块） |
| `Ctrl+b "` | 水平分屏（上下两块） |
| `Ctrl+b 方向键` | 在 pane 之间切换 |
| `Ctrl+b z` | 当前 pane 全屏，再按恢复 |
| `Ctrl+b x` | 关闭当前 pane |
| `Ctrl+b ;` | 上一次活跃的 pane |

---

## 实战场景

### 场景一：SSH 断开不丢工作

这是Tmux 最核心的使用场景，没有之一。

```bash
# 服务器上执行
tmux new -s project

# 在会话里正常工作
cd /project
npm run dev

# 断开 SSH 了？没关系！
# 重新连接后执行
tmux a -t project

# 你会发现服务还在跑，日志还在滚动
```

这就是 **detach**：会话在后台挂着，进程不受影响。

### 场景二：一个窗口同时看代码和日志

```bash
# 新建窗口
Ctrl+b c

# 分屏
Ctrl+b %   # 左右分

# 左边跑服务
cd backend && npm run dev

# 切换到右边
Ctrl+b →

# 右边看日志
tail -f logs/access.log
```

### 场景三：复制粘贴（Tmux 内置）

```bash
# 进入复制模式
Ctrl+b [

# 移动光标（Vim 风格）
Page Up / Page Down  # 上下滚动
q                # 退出复制模式

# 选中后
Enter            # 复制选中文本
Ctrl+b ]         # 粘贴
```

---

## 常见坑与正确做法

### 坑一：开了太多 pane 不知道怎么关

**解法**：每关一个 pane 按 `Ctrl+b x`，逐个关闭。或者直接关整个会话：

```bash
tmux kill-session -t mywork
```

### 坑二：复制模式退不出来

**解法**：按 `q` 退出，不要按 ESC（很多教程会误导你）。

### 坑三：Pane 之间切换不习惯

**解法**：在 `~/.tmux.conf` 里加一行配置：

```bash
# vim 风格的上下左右（不用默认的 Alt+方向键）
bind-key h select-pane -L
bind-key j select-pane -D
bind-key k select-pane -U
bind-key l select-pane -R
```

然后 `tmux source ~/.tmux.conf` 生效。

### 坑四：滚屏只能看到一部分

**解法**：复制模式下可以上下滚动，只要在 `~/.tmux.conf` 开启鼠标模式：

```bash
set -g mouse on
```

之后就可以直接用鼠标滚轮滚动了。

---

## 进阶配置：打造你的 Tmux

`~/.tmux.conf` 是 Tmux 的配置文件，以下是公认提升体验的配置：

```bash
# ===== 外观 =====
set -g default-terminal "screen-256color"   # 256色支持
set -g history-limit 50000                 # 滚屏历史上限
set -g base-index 1                         # 窗口从 1 开始编号
set -g pane-base-index 1                   # Pane 从 1 开始编号

# ===== 状态栏 =====
set -g status-interval 1                   # 状态栏每秒更新
set -g status-left "#[fg=green]#{session_name} "
set -g status-right "#[fg=yellow]%H:%M "

# ===== 体验优化 =====
set -g mouse on                            # 鼠标支持
set -g focus-events on                     # 配合 vim 的 focus events
set -g escape-time 0                      # ESC 延迟消除（Vim 用户刚需）

# ===== 快捷键 =====
unbind C-b                                 # 解绑默认前缀 Ctrl+b
set -g prefix C-a                          # 换成 Ctrl+a（更顺手）
bind-key C-a send-prefix                   # 双重 Ctrl+a 发送原 Ctrl+a

# ===== 分屏快捷键 =====
bind | split-window -h                    # 水平分屏
bind - split-window -v                    # 垂直分屏
```

---

## 总结

| 核心能力 | 解决了什么问题 |
|---------|--------------|
| 会话管理（Session） | SSH 断开不掉线，工作不丢 |
| 分屏（Pane） | 一个窗口搞定所有操作，不用切换 |
| 窗口管理（Window） | 多任务并行，标签化组织 |
| 复制粘贴 | 内置全键盘操作，不用鼠标 |

**一句话：Tmux 让你的终端变成一个真正的 IDE。**

用了 Tmux 之后，我再也没开过第二个终端窗口。

---

**你们日常是怎么管理终端会话的？评论区聊聊。**

---

*相关阅读：*
- *[配置指南] Tmux 进阶：让你的 ~/.tmux.conf 更好看*
- *[工具推荐] Terminal Workflow：iTerm2 + Tmux 组合拳*
