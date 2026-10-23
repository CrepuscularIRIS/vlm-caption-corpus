---
id: PC-F2-11
name: 用某个固定 checkpoint 在"无工具/有工具"下的结果，给题目或调用打"需要工具"的层级，再作奖励门或四格奖励
family: F2_credit
status: needs_revision
problems: {P16: 3, P05: 3, P02: 2, P18: 2, P26: 2}
members: [litscan:65503, 2608.08907, 2609.08025, 2605.00737]
rs_patterns: [heterogeneous_decomposition, controlled_diagnostic_design]
---

## 操作

先用一个固定模型（外部冻结 reasoner、冻结 SFT checkpoint 或预训练策略），分别在"禁用工具"和"允许/强制工具"两种协议下跑同一题，再按结果分层，最后把层级接入 RL 奖励。

- VisTA：冻结 reasoner 原图答 vs 加工具答。四格奖励：错→对 +1，对→错 −.5，错→错 0，对→对 +1；组内 mean/std（litscan:65503 §3.4）。
- ToolVision：冻结 SFT 跑 16 次禁用工具、8 次允许工具，记 c、GTC、NTC。按层赋权：强层 w=.5（c≤8、GTC≥2、NTC≤1），弱层 w=.2（c≤8、GTC=1），普通层 0。奖励
  $$R=R_{acc}+.2R_{proto}+w\cdot\mathbf1[Y=1,n\ge1,\text{无执行错误}]-.05\max(0,n-6)$$
  （2608.08907 §3.3、AppA.3）。
- SVRL：预训练策略单次无工具答对，即标为 search-free。若 search-free 题仍搜索，则 $r_{aware}=.1$。奖励为正确性门控下的四因子乘积（2609.08025 Eqs3–4、§3.2）。
- To Call or Not：$N^*=\mathbf1[s_{NT}<\text{阈值}]$（需要），$\Delta^*=s_{AT}-s_{NT}$（效用）。从输入隐状态学 need 控制器（2605.00737 签名）。

## 信息

- 看得到：某个固定模型在两种协议下的结果，以及 GT。
- 看不到：当前策略在当前状态的需要；某一次具体调用的贡献；标签随 RL 漂移的程度。

## 成立条件

- 冻结测量对之后的策略仍然有效。ToolVision 明确把这列为条件："Frozen measurement remains relevant to later policy"（2608.08907 conditions）。
- "需要工具"与"工具有益"是两回事。$N^*$ 不等于 $\Delta^*>0$（2605.00737 failure_boundary）。
- 题目中要有足够的"禁用失败、允许成功"样本（2608.08907 conditions）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:65503 | 冻结 reasoner 四格奖励 | Table1; §3.4 | ChartQA 76.4→79.9；OoD 62.3→75.8；平均轮数 1.1/1.8/1.4/1.5 | 记录未覆盖 | 成员 |
| 2608.08907 | 冻结 SFT 分层 w + 成功工具 bonus + 超 6 次罚 | Table3; Fig2; AppD | 分层奖励高分辨率准确率 85.9/81.4/75.9 vs 统一 77.0/76.0/68.6；只看结果时工具调用塌到 0；超用项激活 297/198656=.15% | 单训练 run | 成员 |
| 2605.00737 | 无工具失败 need 标签 + 隐状态控制器 | Table2 | Mistral3.1-24B GSM-Hard：自报 .51（5% 调用）→ LNE .43（43% 调用） | 记录未覆盖 | 成员（反例：need 控制器并非普遍有益） |

## 成功条件 / 失败模式

- 成功：标签按目标模型自身测得；以"有/无工具"成对比较而不只看准确率；奖励只在"可从工具受益"的题上发放。
- 失败：
  - 对→对 同样 +1，不惩罚冗余；baseline 答对时所有组合都 +1，组内优势为 0，没有少用工具的压力（litscan:65503 degenerate_cases）。
  - bonus 奖励整条成功轨迹，≤6 次的无关调用也一并拿到；必要但失败的搜索拿不到 bonus（2608.08907 签名 3 failure_boundary）。
  - 静态单次标签有噪声，并会随策略过时（2609.08025 failure_boundary）。
  - 按 need 精度分配调用反而降分（2605.00737 Table2）。
  - 只看结果时工具调用塌到 0，而总奖励仍上升（2608.08907 negative_results Fig2）。

## 审稿期望

VisTA、ToolVision、SVRL 均为 reviewer_concern=low_evidence。"推断"：
- 需要标签漂移曲线（按训练步重测）；
- 需要"打乱层级"对照（ToolVision transfer 建议）；
- need 与 utility 要分开评测（2605.00737）。

## 认知障碍

- 准确率低本身混淆了"对工具有响应的题"与"两条路都解不了的题"（2608.08907 why_non_obvious）。
- 需要工具 ≠ 工具有益；排序调用应验证实际收益，而不只看 need 预测的准确率（2605.00737 why_non_obvious）。

## 工程经验

- 当正确的教师轨迹依赖学生做不到的精细定位时，只匹配终答是不够的；离线成功分组应当作带版本号的标签，记录其漂移，并保留直答支撑（2608.08907 lesson）。
- 当过程奖励鼓励验证时，先检查它是否被转化成了更多工具调用；正确性门控也不能代替调用校准（2609.08025 lesson）。
- 当评估器冻结时，应独立记录其可迁移性与置信校准；对→对的奖励不能解释为对冗余工具的惩罚（litscan:65503 lesson）。

