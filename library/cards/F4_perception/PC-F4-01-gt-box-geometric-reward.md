---
id: PC-F4-01
name: 用 GT 框几何匹配分（IoU / F / Hungarian / 中心距）叠加到终答奖励
family: F4_perception
status: candidate_pattern
problems: {P44: 2, P43: 1, P30: 1}
members: [litscan:72866, litscan:65886, 2604.19945, litscan:78888, litscan:77580, litscan:79625, litscan:73207, litscan:76356, litscan:63682, litscan:56056]
rs_patterns: [structural_prior_encoding, heterogeneous_decomposition]
---
## 操作

在终答奖励上加一个由 GT 目标框算出的几何分，再做组内标准化的 GRPO：

$$R=R_{acc}+R_{fmt}+w\,G(B_{pred},B_{gt})$$

代表形式是 TreeVGR 的双向 max-IoU（litscan:72866 Eq1–4 p7）：

$$R_{IoU}=\tfrac12\Big[\tfrac1M\sum_k\max_i IoU(\hat b_i,b_k)+\tfrac1N\sum_i\max_k IoU(\hat b_i,b_k)\Big]$$

其他变体：
- 召回优先 ModF1，$w_{fp}=0.1$（2604.19945 Eq2–3 p4）；
- 阈值化 Hungarian 匹配，要求 IoU≥.8 且标签 ROUGE≥.9（litscan:78888 Eqs3–4）；
- IoU 加中心距 sigmoid（litscan:65886 Eq1–2）；
- 覆盖门控 IoU 加 L1（litscan:79625 Eqs4–6）；
- Sinkhorn 软匹配 Fβ（litscan:76356 Eqs4–7）。

## 信息

- 奖励器可见 GT 框或 GT 对象集合，以及预测框（对象级变体还要类别）。
- 估计者是规则几何函数，不是策略本身，也不是冻结读者。有两处例外：Artemis 另用 ROUGE 匹配标签（litscan:78888），PMSPO 另用冻结 DINO 做语义调制（litscan:76356 Eq12–13）。
- 看不到的信息：
  - 这次框或裁图对答案的因果贡献；
  - 同一状态不裁时的结果。

## 成立条件

- 训练数据有 GT 框。
- 框坐标、图像索引与实际编码图对齐（2604.19945 App.F.1/F.3 pitfalls；litscan:63255 Eq10 低分辨率坐标）。
- 基座已有 grounding 先验，或先做冷启动 SFT：
  - TreeVGR 35k 多框 SFT（litscan:72866 Table8 conditions）；
  - Artemis 80K COCO 冷启动（litscan:78888 Table7）；
  - ZoomEarth 1000 条 SFT，工具必要/不必要 2:1（litscan:65886 Table6）。
- 若要定位到 token：POLIA 只把对象级额外优势路由到该对象的坐标 token（litscan:73207 §4 pp4–5）。其余成员都是整条序列一个标量（litscan:72866 signal_routing；litscan:78888 signal_routing）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:72866 | 双向 maxIoU，文本框不回放 crop | Table8 p19 | 同冷启动、无 IoU：TreeBench 38.0 / mIoU 27.2；dual：50.4 / 44.0；**recall-only：答案 0、mIoU 78.3** | 记录未覆盖 | 正例，同时给出 hack 证据 |
| litscan:65886 | IoU + 中心距 + answer + .05 format | Table6 | LRS-GRO avg 53.76，去两种空间奖 52.67；只加 distance 52.94 | 记录未覆盖 | 弱正 |
| 2604.19945 | Stage1 用工具 GT 分（ModF1）训 200 步，Stage2 换答案奖 | Table2 p6；Table3 p6 | DocVQA-RF 77.3（工具+答案同时训为 58.1，只用答案奖为 62.6）；$w_{fp}$ 1→.1：VisualProbe 42.9→46.3，**调用 2.13→3.20** | 记录未覆盖 | 正，但调用增多 |
| litscan:78888 | 阈值 Hungarian，η=.8 | Table6 p8 | Pixmo-val 81.4，none 为 65.2；但 LISA none 71.7 > 69.8 | 记录未覆盖 | 混合 |
| litscan:77580 | grounded 流 dual IoU + 历史最佳参考 | Tables2,5 | 5 基准平均：grounded-only 71.1；加 consistency+archive 72.4 | 记录未覆盖 | 正（依赖 GT 框） |
| litscan:79625 | 覆盖门控 IoU+L1，256 难例人工嵌套框 | Table4 | HR8K：61.0→69.9（Stage I）→72.1（Stage II）；V*：72.3→78.0→80.6 | 记录未覆盖 | 正 |
| litscan:73207 | 对象 GT IoU×conf，组 std，坐标 token 局部优势 | §4 pp4–5；Table1 p6 | 7B VSR 81.3，GRPO 为 59.0；3B GQA 60.2 低于 few-shot SFT 64.6 | 记录未覆盖 | 正，但需要对象 GT |
| litscan:76356 | Sinkhorn Fβ + DINO 语义 | Table4；Table12 | COD10K MAE .160→.024 | 4 种子，SD≤.003（Table12） | 正 |
| litscan:63682 | crop 只奖 best IoU 的正增量 + 必用工具奖 | §3.3.2；Table3 p7 | 去 strategy：MVToolBench 60.1→50.7；去 penalty：55.9 | 记录未覆盖 | 正；报告了重复裁图/枚举刷分 |
| litscan:56056 | （反证，不是奖励）200 条 focus 轨迹，框与答案的相关 | Table11–12（记录 question 字段） | IoU@.5 与答案相关 φ=−.02；Recall@.9 为 .44 | n/a | 紧框 IoU ≠ 答案收益 |

## 成功条件 / 失败模式

**成功条件**
- 同时约束召回与精确率（litscan:72866 Table8）；
- 先建立工具技能，再切回答案奖（2604.19945 Table2）；
- 任务目标确实在 GT 框里。

**失败模式**
- **只奖召回会枚举框直到不作答**：recall-only 答案 0、mIoU 78.3（litscan:72866 Table8）。
- **复制框不受罚**：均匀复制所有预测框不改变两项分数，重复的高 IoU 框还会提高 precision 均值（litscan:72866 invariance，读者推导）。
- **召回优先会增加调用**：调用 2.13→3.20（2604.19945 Table3）。
- **捷径与 hack**：
  - 混入正向（canonical）文档时，模型走 index0 捷径（2604.19945 App.D.3）；
  - 工具条件 bonus 下出现先答后调工具的 hack（2604.19945 Sec.4.3.2 / Fig.4，详见 PC-F4-02）。
- **几何代理与内容脱节**：
  - 中心距不约束框大小与内容（litscan:65886 failure_boundary）；
  - 紧框 IoU 与答案近零相关（litscan:56056 Table11–12）。
- **边界未定义**：
  - Hungarian 权重在 N=1 时分母为 0（litscan:78888 degenerate_cases）；
  - 空预测 / 空 GT 的 fallback 未定义（litscan:72866 degenerate_cases）。
- **硬阈值无梯度**：定位改善但未过阈值时奖励不变（litscan:78888 degenerate_cases）。

## 审稿期望

推断，成员记录均为 low_evidence。审稿人会要求：
- 同冷启动、无几何奖的对照（只有 litscan:72866 做了）；
- 重复框、空答案率与调用次数的 hack 监测；
- GT 框来源与测试集去重；
- 多种子。成员均未报告训练种子，只有 litscan:76356 Table12 有 4 种子。

## 认知障碍

- 终答奖不约束 grounding，而检测/定位数据集现成就有框，所以直接加几何项看起来很自然。
- 前人很少把"框准不准"和"框对答案有没有用"分开测量。SimpleVGC 的相关分析（litscan:56056 Table11–12）显示两者可以几乎无关。

## 工程经验

- **只奖召回时**：策略会枚举框到不作答。应同时加 precision 项，并监控空答率（litscan:72866 Table8）。
- **工具奖用 max 聚合时**：重复调用不受罚。另需重复/冗余惩罚（2604.19945 degenerate_cases；litscan:63682 penalty 消融 60.1→55.9）。
- **坐标链路**：
  - 训练用归一化坐标、推理用绝对坐标时，必须按实际 H/W 换算（litscan:72866 E.1 pitfalls）；
  - 框按低分辨率宽高给出、裁图却取原图时，要保持比例对应（litscan:63255 Eq10）。
- **混入未增广的 canonical 数据时**：模型会学 index0 捷径。应在工具阶段只用增广数据（2604.19945 App.D.3：DocVQA-RF 67.1→79.4，工具调用 6.98→4.26）。

