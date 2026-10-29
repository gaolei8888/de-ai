# de-ai 去 AI 化产品与技术设计 V1.2

日期：2026-10-29
状态：设计提案，以下模块尚未实现
仓库：gaolei8888/de-ai

## 1. 产品定义

**de-ai = AI Output Refinement Engine（AI 作品精修引擎）**。

面向四类作品：文本、语音、视频、软件 UI。目标是发现模板化、失真、不一致和体验缺陷，并在保留创作者原意、功能与项目约束的前提下进行可解释、可回滚、可验证的局部修复。

这里的“去 AI 化”是质量与作者风格优化，不是宣称能够判定 AI 来源、绕过检测或移除来源水印。尊重素材授权、声音与肖像使用同意、原始溯源信息。

核心口号：**Keep the intent. Improve the result.**

## 2. 产品分层

### de-ai Studio
- 统一项目页；选择 Text / Audio / Video / UI 工作区。
- 统一问题清单：严重程度、置信度、证据位置、预计修复成本、风险及审查状态。
- 多版本对比、逐条确认、撤销、报告导出。
- 媒体专用界面：文本 diff；音频波形与时间线；视频镜头/关键帧与时间轴；UI 截图/DOM/组件树与交互流程。

### de-ai Engine
1. **Intent Guard**：解析作者原意、视频分镜、台词与角色设定、UI 功能规范和不可更改约束；缺少规范时显式标记未知，而不猜测。
2. **De-AI Inspector**：提供各领域规则、模型审查和确定性检测，输出可复核证据。
3. **Repair Planner**：推荐优先级和最低破坏性的局部修复方案；量化资源成本与可能副作用。
4. **Execution Adapters**：调用现有编辑器、TTS、视频工作流及代码代理；默认只给建议，修改需授权。
5. **Regression Validator**：在修复后验证原意、事实、音画、视觉与功能约束未退化；失败时回退。
6. **Creator/Brand Profile**：可编辑的风格规则、素材规范、偏好历史、显式允许收集的反馈。

架构应为 **共享审查协议 + 四类插件**，而不是一个大模型笼统打分。

## 3. 领域设计

### Text
输入：粘贴文本 / Markdown / txt；后续 DOCX 和网页。
检测：陈词滥调、模板式排比、过度断言、冗长、机械段落结构、事实与引用风险。
修复：句段级改写、风格约束、保留事实和主张、展示 diff。
验证：主张/否定/数字/引用保真；高风险变更人工确认。

### Audio / Voice
输入：有权使用的 WAV/MP3、配音文本及可选说话人表现要求。
检测：ASR 与原稿偏差、静音与停顿、语速异常、过密或缺失的韵律变化、爆音/噪声、表现风格与内容不匹配。不能把固定节奏或合成音本身等同于低质量。
修复：脚本标注、切分、局部重录、合法授权声音的 TTS 重合成、音量与停顿调整。
验证：ASR 内容对齐、发音听评、峰值与响度范围、接缝自然度、人工 A/B 听审。
**不支持未经同意的声音克隆或人物冒充。**

### Video
输入：视频文件、字幕/音轨、可选分镜与角色/场景设定。
检测：帧间闪烁、人物服装道具漂移、动作因果不合理、场景不连续、字幕/口型与声音不匹配、剪辑节奏、镜头语言重复。区分艺术风格与真实缺陷。
修复：标记问题镜头及时间码；建议帧修补、局部重新生成、重新剪辑、字幕/声音校正。重生成可通过 dc-video-v2 等外部适配器。
验证：修复前后关键帧、人物/场景一致性、声音/字幕对齐、人工审片。避免无故全片重做。
研究：VBench++ / Video-Bench / Ref4D-VideoBench 的分维度评估思路，不将自动指标视为绝对真理。

### Software UI / UX
输入：浏览器授权测试 URL、截图、可选源码/组件树、用户任务与设计规范。
检测：
- 机械式通用卡片瀑布、无意义渐变/徽章/图标、信息层次不清；
- 排版、间距、色彩、组件、状态在多页面之间不一致；
- 响应式布局、触控目标、键盘访问、焦点、对比度、文本替代；
- 假按钮、无效交互、加载/错误/空态缺失，真实任务流程冗长；
- AI 生成界面典型的“有视觉，无产品逻辑”问题。
修复：给出组件级 diff、token 变更与交互状态设计；授权后由代码 Agent 生成 PR；不能仅靠截图改图后宣称 UI 已修复。
验证：Playwright 流程测试、视觉回归、axe-core/WCAG 2.2 自动与人工检查；跨屏尺寸；保留行为约束。
**设计风格并无唯一审美答案**：默认按产品任务而非“看起来像 AI”评分。

## 4. 统一问题协议

建议 Issue 对象：
```json
{
  "id": "iss_001",
  "modality": "video",
  "category": "continuity.character",
  "severity": "major",
  "confidence": 0.84,
  "location": {"start_ms": 12600, "end_ms": 15300, "shot_id": "shot_04"},
  "evidence": ["frame_12600", "frame_14900"],
  "expected_constraint": "角色外套必须保持蓝色",
  "observation": "外套颜色发生变化",
  "proposed_actions": ["local_regenerate", "manual_review"],
  "risk": "medium",
  "status": "proposed"
}
```
字段含义：confidence 是检查器置信度而非 AI 来源概率；证据与规则版本需保存。其他模态的 location 分别是文档偏移、音频时间戳、UI 组件选择器/页面状态。必要时增加 `source_version` 与 `checker_version`。

## 5. 参考实现与接口

建议 monorepo：
```
apps/studio/                 # Next.js + Tiptap + 领域编辑视图
services/api/                # FastAPI
services/worker/             # 异步审查和修复任务
packages/contracts/          # schema / JSON Schema / OpenAPI
packages/inspectors/text/
packages/inspectors/audio/
packages/inspectors/video/
packages/inspectors/ui/
packages/intent-guard/
packages/repair-planner/
packages/regression/
packages/adapters/           # dc-llm, dc-video-v2, Browser/Playwright, TTS
evals/                       # 标注数据、基线与回归
docs/
```

推荐技术：TypeScript/Next.js/Tiptap；Python/FastAPI；PostgreSQL；Redis 队列；对象存储；FFmpeg/ASR/VAD；视频关键帧分析；Playwright + axe-core。模型路由通过可替换 LLM API，dc-llm 可作为适配之一。视频分析与修复分开计费和任务化，避免每次全片调用昂贵模型。默认不需要训练自己的基础模型。

API 初版：
- `POST /v1/projects`
- `POST /v1/assets`：上传或登记已授权资产
- `POST /v1/reviews`：按模态执行检查，返回 task_id
- `GET /v1/reviews/{id}`：问题及证据
- `POST /v1/repairs/plan`：生成局部修复计划
- `POST /v1/repairs/{id}/approve`：用户授权执行
- `POST /v1/validations`：修复后回归检查
- `GET/PUT /v1/profiles/{id}`：风格与质量约束

## 6. 开发阶段（避免四个产品同时做完）

**P0 平台底座（2–3 周，估算）：** 项目/资产管理、问题 Schema、报告 UI、文本 Inspector + diff、UI 静态审查和规则型检测、评测框架。

**P1 双线真实验证（3–5 周，估算）：**
- Software UI：通过 Playwright 采集 DOM、截图、交互状态，形成可复现 UI 审查报告；再加可审批代码补丁。
- Video：FFmpeg 镜头切分、关键帧、字幕/台词时间码、人物/场景一致性问题定位，先输出建议，不承诺自动重生成。
理由：用户已有软件 Agent 和 AI 视频场景，最容易产生可复现价值。

**P2 音频与深度修复（4–6 周，估算）：** ASR + VAD + 韵律/响度分析，局部修复；接入已有 TTS/视频执行工作流；多模态回归。

**P3 商业化：** 团队协作、工作区权限、成本计量、API Token、受控存储、审计与插件。所有阶段时间仅为初始估计，以实际团队人力确定。

## 7. 验收指标（目标值，非现状）
- 自动发现问题经人工审查的有效率：目标 >= 80%（按模态分别统计，不能汇总掩盖）。
- 高风险原意/功能变更漏检：目标 < 2%（基于人工标注评测集）。
- 修复后引入新缺陷比例：目标 < 5%。
- UI 自动化任务成功率不低于修复前，并满足选定的 WCAG 2.2 AA 检查范围（自动工具不能完全保证 WCAG 合规）。
- 用户采纳率、审查时间、人均成本与净改进评分作为真实产品指标。

建立 golden set：各模态至少 50 个正例、50 个边界/反例，包含专业设计但“看起来像 AI”的正常内容和真实有缺陷的人工内容，避免把审美偏好当作来源鉴别。

## 8. 风险和策略
- 风格主观：审查给出可验证理由与用户目标，允许覆盖规则。
- 内容来源：保留已有水印与溯源元数据；不承诺检测作者身份。
- 声音/肖像/版权：授权校验、敏感资产隔离、删除流程。
- UI 网站：仅对所有者授权的域名与测试环境做浏览器自动化；源码修改必须通过审查和可回滚 PR。
- 隐私：默认最小化存储；清晰说明第三方模型的数据路径与保留政策。
- 安全：插件沙盒、提示注入防护、限制媒体处理资源与远程内容访问。

## 9. 参考
- Martin Fowler, LLM Voice: https://martinfowler.com/bliki/LLM-Voice.html
- Nielsen Norman Group, The Custodial Era of UX: https://www.nngroup.com/articles/ai-ux-debt/
- W3C WCAG 2.2: https://www.w3.org/TR/wcag/
- NIST Synthetic Content Transparency: https://www.nist.gov/publications/reducing-risks-posed-synthetic-content-overview-technical-approaches-digital-content
- VBench++: https://pubmed.ncbi.nlm.nih.gov/41247905/
- Ref4D-VideoBench: https://openaccess.thecvf.com/content/CVPR2026/html/Wei_Ref4D-VideoBench_Four-Dimensional_Reference-Based_Evaluation_of_Text-to-Video_Generative_Models_CVPR_2026_paper.html
