# Research Newspaper / 研究日报 Skill

启动词：**出版一下今天的报纸**。

提供跨领域的图文 HTML 日报、机构时间线、技术指南、分类统计、逐工作基线与归因评价、SQLite 历史和趋势预测复盘。无需调用指定厂商 API。研究与判断由使用它的智能体完成，脚本负责校验、存储和渲染。

## 使用

将本目录放入支持 SKILL.md 的智能体的技能目录。Codex 可放入 `~/.codex/skills/research-newspaper`；其他宿主按其技能发现规则配置。不能自动发现技能时，让智能体读取本仓库的 `SKILL.md`，再说启动词。

首次告诉智能体研究方向和关注问题，后续沿用报纸目录中的 `profile.json`。换方向新建目录，分别积累。并非所有智能体只靠一句话就能自动加载远程技能；宿主须允许读文件、联网调研和运行脚本。

依赖：Python 3.10+，核心代码仅标准库；浏览器用于阅读／可选视觉检查。若要缩放复杂图片，宿主可自行选择可用工具；本包不强制图像库。

```sh
python scripts/init_report.py --output ./my-newspaper --topic "具身智能" --focus "隐藏状态下的动作安全" --timezone Asia/Shanghai --date 2026-11-01
cd my-newspaper
python build.py
python check_report.py
python serve.py
```

初始化是空报纸，不含捏造研究。让智能体按 `SKILL.md` 调研并补充数据。HTML 可以离线读；`serve.py` 提供本机只读接口，SQLite 保留版本。首次可按来源日期补历史背景，但旧材料不能当作今天首发或新预测命中。

启动词默认生成本地报文，不自动联网发布或配置定时任务。GitHub/LAN/托管发布需另有授权。没有浏览或执行权限的宿主应说明缺失能力，不得冒充已研究或已生成。

仓库不包含原使用者的研究记录、个人课题、论文图片、数据库或凭据。`assets/report` 是空白应用模板；`references` 说明数据契约和评价流程。可将模板用于不同语言和领域，分类需按研究方向确认。
