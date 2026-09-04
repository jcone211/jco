---
title: "flit stk — 量化盯盘"
date: 2026-09-04
description: "导入即用的无后端轻量级量化工作前台 · Chrome 扩展（Manifest V3），含 AI Agent、多渠道实时行情与多条件提醒。"
summary: "受 DeepSeek Harness 架构启发的浏览器端量化盯盘工具，集成 AI Agent、实时行情、多条件提醒与 flit_bridge 沙箱桥接。"
tags: ["Chrome 插件", "浏览器扩展", "量化盯盘", "AI Agent", "市场数据"]
---

## 项目背景

手机设置多个股价提醒麻烦，工作时切手机容易分心；股票分组不够灵活，多组股票管理操作繁琐；市场上稀缺的量化分析 AI Agent。本项目就是为解决这些问题而生的——装好浏览器即用，零服务端零配置。

## 架构总览

本项目受 **DeepSeek Harness** 架构启发，采用双路径沙箱 + Guard 安全执行层 + 轨迹日志 + 工作流自发现的设计模式。

| flit_stk 对应层 | DeepSeek Harness 类比 | 关键差异 |
|---|---|---|
| **flit_bridge**（spawn+白名单+只读SQL+无Shell+路径防护） | 沙箱隔离执行环境 | 日常文件读写不走 bridge，经 Chrome File System Access API 直通（用户手势授权） |
| **ai/core/ai_guard.js**（纯函数三态判定：放行/注解/丢弃） | 输出拦截（Guard） | 只针对行情反编造，不覆盖通用内容 |
| **ai/core/ai_debug.js**（会话全程记录+容量上限+回放） | 轨迹日志 | 完全一致 |
| **chrome.storage.sync** + `.gitignore` + 日志脱敏 + 提示词硬规则 | 密钥/凭证保护 | 多一层 Git 级别防护（自动忽略 `config.json`） |
| **`flit/` 写约束**（文件只能写 `flit/` 下）+ 工作流自动发现（`flit/workflow/`） | 工作目录隔离 + 可复用工作流 | AI 只能写 `flit/`，读全目录但受 Chrome 授权管辖 |

### 架构图

点击下方链接可直接查看完整的项目架构图（交互式 SVG 架构图，支持主题切换与导出）：

- ▶️ <a href="/files/flit_stk-architecture.html" target="_blank" rel="noopener noreferrer"><strong>项目总览架构图</strong></a> — 整体架构总览，包含数据流、信任边界与模块关系
- 🔒 <a href="/files/flit-harness.html" target="_blank" rel="noopener noreferrer"><strong>AI 安全执行框架图</strong></a> — 双路径沙箱（直通路径 vs 沙箱路径）、Guard 反编造判定、轨迹日志与工作流自发现

> 架构图使用 [Archify](https://archify.dev) 生成，支持暗色/亮色切换、交互式探索、节点聚焦与路径追踪，直接在新标签页打开即可体验。

## 核心能力

| 功能 | 说明 |
|---|---|
| **AI Agent** | 基于 **ReAct 范式**，零依赖 function-calling 循环，工具组冷加载，持久记忆偏好，多 API Key 配置，支持多本地工作目录 |
| **Agent桥接** | 通过 **flit_bridge** 桥接本地 PostgreSQL 数据库，支持 AI Agent 执行脚本、查询日线、回测验证，零配置即可启用 |
| **多渠道实时行情** | 集成 **adata 免费实时数据**、**小石大数据**、**问财 & 雪球页面爬取** 三种渠道，全局设置一键切换 |
| **多条件提醒** | 分别按**当日涨跌幅**与**导入以来涨跌幅**设置阈值，实时监控并触发提醒 |
| **要点与事件记录** | 记录交易逻辑与预测事件，追踪准确率，分析结合实际动态调整策略 |
| **专业免费渠道** | 批量打开问财/雪球看 K 线，一键批量导入到指定组合 |
| **全局可控** | 按需启用/关闭各功能模块，不用的不占空间 |
| **一键迁移** | 导出/导入完整数据，快速无缝迁移到其他设备 |

## 数据路径

1. **Content Script** 抓取股票页整页 HTML → background SW
2. SW 转发 HTML 到 **Offscreen** 隐藏页解析（SW 无 DOM）
3. **Data Landing** 匹配股票 → 合并字段 → 双阈值锁存通知
4. 落地结果写入 `chrome.storage`，popup 通过 `onChanged` 刷新

## 工程说明

该项目仍在持续迭代中。项目页以当前可运行界面、问题背景和实现过程为主，架构图已整合关键模块设计与版本迭代记录。

- 代码仓库：[jcone211/flit_stk](https://github.com/jcone211/flit_stk)
- 当前版本：**v1.9.0**
- 当前状态：持续迭代中