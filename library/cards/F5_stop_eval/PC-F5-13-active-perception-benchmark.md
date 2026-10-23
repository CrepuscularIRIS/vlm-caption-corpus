---
id: PC-F5-13
name: 构造必须操作图像才能答、且终答可核验的评测，并把"取证"与"作答"分开计分
family: F5_stop_eval
status: candidate_pattern
problems: {P48: 3, P49: 2, P33: 1, P65: 1, P53: 1}
members: [2511.01833, litscan:72197, litscan:77853, litscan:2777]
rs_patterns: [controlled_diagnostic_design, decompose_and_delegate, heterogeneous_decomposition]
---
## 操作
按视觉操作类型挑选/生成题目，保留可程序核验的答案；零样本跑有/无工具的模型，并单独计分取证行为：
- TIR-Bench：13 类视觉操作，抽取终答后对选择/短答精确比对，列表任务算 IoU（2511.01833 Sec.4.1）。
- O3-Bench（InSight-o3）：345 QA / 204 张图的多区域地图与图表，三个强模型全答对的题被剔除（litscan:72197 relevance P48、pitfalls）。
- ACTIVE-o3：小/密目标检测与分割，固定 K 候选区域预算（litscan:77853 signatures）。
- ActiView：限制初始视域，分 zoom / shift / mixed；按人工线索视图算 $P=TP/(TP+FP)$、$R=TP/(TP+FN)$、F1，并单独报 QA（litscan:2777 AppG Eqs1–3）。

## 信息
构造者见源图、程序变换真值或人工标注；被测模型只见图像、题目与工具接口。终答抽取常用外部 LLM（TIR-Bench 用 GPT-4o 抽取，2511.01833 information）。

## 成立条件
- 题目答案与图像变换正确；抽取器可靠（2511.01833 conditions）。
- 各 benchmark 之间不能默认独立：TIR-Bench 的 Visual Search 含 32 个 HR-Bench 题（2511.01833 conditions）。
- 工具环境与模型输入预算对齐：InSight-o3 中 reasoner 输入 1280² vs 3500² 决定搜索增益（litscan:72197 pitfalls）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2511.01833 TIR-Bench | 13 类视觉操作 + 有/无工具对比 | Sec.4.1 p.6（Table 2）；Sec.4.2 p.7 | o3-TU All 46.0 vs o3 26.9；o4-mini-TU 37.5 vs 21.2；Proportion VQA 用工具反降 34.2→31.7 | 记录未覆盖 | 记录未覆盖 |
| litscan:72197 InSight-o3 / O3-Bench | 固定 reasoner + 训练 searcher；新 benchmark | Table5 p10；Table1 | GPT-5-mini O3 39.0→61.5；Gemini 高分辨率 + searcher 在 HR4K 83.5→82.3、VProbe 39.6→36.2 | 多数评测 3 trials，MME 单次；训练种子未知 | 记录未覆盖 |
| litscan:77853 ACTIVE-o3 | 固定预算主动感知 GRPO + 小/密目标评测 | Table15 p21；Table4；Table6；Table16 | LVIS dense 小目标 AP 1.6→4.3；SODA-A AP .7→9.2；DirectRFT 大目标 APl 23.4 高于 20.9；heuristic-only MMBench 78.9 低于 base 80.1 | default + 3 run：APs 4.25±.10 | 记录未覆盖 |
| litscan:2777 ActiView | 受限初始视域 + 视图选择 P/R 与 QA 分开 | Table5 p8；Table10 p16；Table11 p17 | GPT-4o 个体 pipeline 66.40 vs 人 84.67；LLaVA-7B 4→16 切块 60.31→57.69 | 随机基线 10K runs；重复推理方差未给 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：报告终答、调用次数、可用工具、执行预算（2511.01833 lesson）。
- 失败模式：
  - 工具收益不均，有的任务用工具反而降（2511.01833 Sec.4.2）；高分辨率 + searcher 在若干 benchmark 下降（litscan:72197 Table1）。
  - 作者以人工直觉要求工具，不是逐题证明不能直答（2511.01833 failure_boundary）。
  - "三强模型全答对则剔除"使难度成为条件选择（litscan:72197 pitfalls）。
  - 全选视图可抬 recall 不保证 QA；不选也可能靠先验答对（litscan:2777 degenerate_cases）。
  - 单图 zoom 任一视图答对即成功，多图联合回答——跨架构比较有 oracle 选择优势（litscan:2777 negative_results）。
  - 固定预算下的感知提升不说明学会少调用或停止（litscan:77853 lesson）。

## 审稿期望
- 同时报调用次数与 token；调用多本身不是效率提升（2511.01833 lesson）。
- 统一单图/多图最终回答规则；不能用最佳视图 oracle 代替实际策略（litscan:2777 lesson）。

## 认知障碍
只测高分辨率搜索会漏掉其他操作；提供工具也不保证模型调用或获益（2511.01833 why_non_obvious）。全图答对不代表能找到需要的视图（litscan:2777 why_non_obvious）。

## 工程经验
- 当工具 API 的定量评测不输出推理、需另用网页重跑做定性分析时，两份结果必须分别归档（2511.01833 pitfalls）。
- 当评测 reasoner 与工具的输入分辨率不同，搜索增益会被分辨率主导，必须对齐输入预算（litscan:72197 pitfalls）。
- 当 benchmark 由强模型过滤构造时，要在报告中标明筛选条件，不能当无偏难度（litscan:72197 pitfalls）。
- 当同题不同初始视图被当成多题时，它们不独立，样本量要按题计（litscan:2777 pitfalls）。

