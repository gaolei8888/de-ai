# 界面点睛：本地浏览器审查（实验性）

本阶段新增 **Playwright CLI**，可在桌面和手机两个视口打开本地网页，保存截图及 JSON 问题报告。该功能尚未接入网页 Studio，也不能直接修改源码。

## 安装与运行

```bash
pip install -r api/requirements.txt
pip install "playwright>=1.50,<2"
python -m playwright install chromium
uvicorn run:app --port 8000
# 在另一个终端运行
python -m tools.ui_audit http://127.0.0.1:8000/ --output artifacts/ui-audit
```

输出：`desktop.png`、`mobile.png` 和 `report.json`。检查项目包括图像 alt、按钮名称、表单标签、main landmark、文档语言与横向溢出。

**安全范围**：仅允许 loopback URL；禁止将此 CLI 直接暴露为公网接口。页面的外部资源请求会被拦截；对于不可信网页应在额外的隔离容器中执行，限制文件权限和网络。不会点击、提交表单或自动修复。

**限制**：启发式结果可能误报或漏报。脚本不包含完整的无障碍计算、WCAG 认证或多页用户任务测试。下一步应补充 axe-core、行为测试以及经审核的代码补丁。
