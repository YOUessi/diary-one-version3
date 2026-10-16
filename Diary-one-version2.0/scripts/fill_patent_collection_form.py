# -*- coding: utf-8 -*-
"""按开发现状填写 patent/真实功能采集表.docx，保留原 Word 字体与表格结构。"""
from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

PATENT_DIR = Path(__file__).resolve().parents[2] / "patent"
TEMPLATE = PATENT_DIR / "真实功能采集表.docx"
BACKUP = PATENT_DIR / "真实功能采集表_填写前备份.docx"
OUT = TEMPLATE

FIELDS = {
    "dev_hw": "x86_64 个人计算机，8GB 及以上内存，100GB 可用磁盘空间",
    "dev_os": "Windows 10/11 64 位（主开发环境）；macOS（iOS 构建与可选联调）",
    "run_hw": "Apple iPhone / Android 智能手机；可选 AI 摄像耳机（蓝牙/Wi-Fi 协同）",
    "dev_tools": "Visual Studio Code、Cursor、Node.js 20、Python 3.14、Git、Docker Desktop、Figma",
    "run_platform": "iOS 15+、Android（Expo Go / 原生壳）；服务端 Linux 容器（Docker）",
    "run_support": "Expo SDK、React Native、FastAPI、PostgreSQL、Redis、MinIO、ffmpeg、DashScope 兼容 API",
    "dev_purpose": "实现低负担采集、理解与可信日回顾的个人记忆软件",
    "industry": "消费电子与个人记忆管理应用软件",
    "languages": "TypeScript、JavaScript、Python、SQL",
    "source_lines": "约 12 万行（diary-one 单体仓库：移动端 + BFF/Worker + 联调脚本）",
    "main_functions": (
        "Diary One 智能个人记忆系统面向终端用户提供「设备采集—手机编排—云端理解—结果回传」闭环。"
        "手机 App（React Native/Expo）提供 Diary、Memory、Device、Account 四页主入口："
        "Diary 按日展示记忆卡（Chapter）与小记忆（Aha），支持今日状态、日历选日与历史分页加载；"
        "Memory 支持字面搜索、Captured by You 原始素材浏览、Your Topics 与 Memory Preferences；"
        "Device 展示耳机连接、同步与自动采集设置（未连接时诚实展示，不伪造状态）；"
        "Account 提供资料编辑、通知与语言、隐私与数据管理及云端证据上传同意开关。"
        "登录支持邮箱 OTP（可配置 SMTP），登录后可完成可跳过偏好问卷并记录云处理同意版本。"
        "媒体处理链路：相册/演示素材导入、SHA256 去重、视频语义抽帧与质量门控、"
        "端侧语义路由（Feature Print 融合与规则审计）、Evidence 规范化与本地 SQLite 账本；"
        "可导出 DayRevision Bundle 并经 Bearer 鉴权上传至 Dev Lite 或量产 BFF。"
        "云端 FastAPI BFF 提供 /health、OTP、/v1/day-revisions 幂等接收、/v1/jobs 轮询、"
        "Daily Recap MP4 渲染（ffmpeg）及 evidence 语义端点；Worker 从 MinIO 拉取证据并代理 X02 V1.75 算法编排。"
        "Share 支持日级 Daily Recap 视频、照片拼贴与插画分享流；内测 Lab 可切换 Research/Production 云目标并 Ping 联调。"
        "系统遵循「观测与叙事分离、宁少勿编、失败可恢复」：未授权云同意不上传；"
        "Your Story 与用户偏好和算法正文分层存储；处理失败 fail-closed 并保留可重试语义。"
    ),
    "tech_features": (
        "端云协同、Evidence 最小上传、语义抽帧与路由、DayRevision 幂等任务、"
        "OTP 会话 Bearer、本地账本与原子发布结果校验。"
    ),
    "feature_options": "已选（最多 3 项）：APP；人工智能软件；大数据软件",
    "copyright_purpose": "保护自研 Diary One 移动端与云端 BFF 源代码及文档，用于软件著作权登记",
    "copyright_before": "否，本次说明书与源代码均为首次提交登记，未办理过著作权",
}


def _char_count(s: str) -> int:
    return len(s.replace("\n", "").replace(" ", ""))


def _validate() -> None:
    assert 8 <= _char_count(FIELDS["dev_purpose"]) <= 50
    assert 4 <= _char_count(FIELDS["industry"]) <= 50
    mf = _char_count(FIELDS["main_functions"])
    assert 500 <= mf <= 1300, mf
    assert _char_count(FIELDS["tech_features"]) <= 100
    assert _char_count(FIELDS["copyright_purpose"]) <= 50


def _clear_paragraph(p) -> None:
    for r in list(p.runs):
        r._element.getparent().remove(r._element)


def set_cell_text(cell, text: str, *, placeholder_style: bool = False) -> None:
    """写入单元格：宋体 12pt；占位风格为灰色（与原表「必填项」一致时可关）。 """
    if not cell.paragraphs:
        cell.add_paragraph()
    p = cell.paragraphs[0]
    _clear_paragraph(p)
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    run = p.add_run(text)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(12)
    if placeholder_style:
        run.font.color.rgb = RGBColor(0xA6, 0xA6, 0xA6)
    else:
        run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    run.bold = False


def fill_nested_table(nt) -> None:
    set_cell_text(nt.rows[0].cells[1], FIELDS["dev_hw"])
    set_cell_text(nt.rows[0].cells[5], FIELDS["dev_os"])
    set_cell_text(nt.rows[1].cells[1], FIELDS["run_hw"])
    set_cell_text(nt.rows[1].cells[5], FIELDS["dev_tools"])
    set_cell_text(nt.rows[2].cells[1], FIELDS["run_platform"])
    set_cell_text(nt.rows[2].cells[5], FIELDS["run_support"])
    set_cell_text(nt.rows[3].cells[1], FIELDS["dev_purpose"])
    set_cell_text(nt.rows[3].cells[5], FIELDS["industry"])
    set_cell_text(nt.rows[4].cells[1], FIELDS["languages"])
    set_cell_text(nt.rows[4].cells[4], FIELDS["source_lines"])
    set_cell_text(nt.rows[5].cells[1], FIELDS["main_functions"])
    set_cell_text(nt.rows[6].cells[1], FIELDS["tech_features"])
    # 第 7 行为选项示意图，文字写入第 8 行合并区，不删原图
    if len(nt.rows) > 8:
        set_cell_text(nt.rows[8].cells[1], FIELDS["feature_options"])
    else:
        set_cell_text(nt.rows[7].cells[1], FIELDS["feature_options"])


def main() -> None:
    if not TEMPLATE.is_file():
        raise SystemExit(f"Missing template: {TEMPLATE}")
    _validate()
    if not BACKUP.is_file():
        shutil.copy2(TEMPLATE, BACKUP)
    doc = Document(str(TEMPLATE))
    outer = doc.tables[0]
    nested = outer.rows[0].cells[1].tables[0]
    fill_nested_table(nested)
    set_cell_text(outer.rows[1].cells[2], FIELDS["copyright_purpose"])
    set_cell_text(outer.rows[2].cells[2], FIELDS["copyright_before"])
    doc.save(str(OUT))
    print(f"Saved: {OUT}")
    print(f"Backup: {BACKUP}")
    print(f"main_functions chars: {_char_count(FIELDS['main_functions'])}")
    print(f"tech_features chars: {_char_count(FIELDS['tech_features'])}")


if __name__ == "__main__":
    main()
