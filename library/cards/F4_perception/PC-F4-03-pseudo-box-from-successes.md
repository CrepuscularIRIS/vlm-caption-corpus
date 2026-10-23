---
id: PC-F4-03
name: 用成功轨迹的框共识或相对面积代替 GT 框，塑形裁图几何（无框标注）
family: F4_perception
status: candidate_pattern
problems: {P44: 2, P30: 2, P43: 2, P02: 1}
members: [litscan:71995, litscan:63255, 2605.16416]
rs_patterns: [self_supervised_signal_engineering, heterogeneous_decomposition]
---
## 操作

不用 GT 框，而用同组 on-policy 样本自身构造几何参照，只对成功且裁图的轨迹施加几何分。

**1. 共识框（MedVR，litscan:71995 Eq4–5 pp5–6）**

$$\hat M(u,v)=\mathbb1\Big[\sum_{i\in T^+}M_i(u,v)>|T^+|/2\Big],\qquad R_{tool}=0.5+0.5\,\mathbb1[IoU(M_i,\hat M)>0.5]$$

**2. 相对面积罚（AdaptVision，litscan:63255 Eq9–10）**

$$R_{tool}=R_{crop}-2\cdot\mathbb1[R_{acc}=1]\mathbb1[R_{crop}=1]\operatorname{clip}\!\big(r_{area}/\overline{area}_{succ}-1,0,1\big)$$

**3. 不确定度目标面积（CAVE $c^{af}$，2605.16416 Sec.3.2.3 pp4–5）**

- 目标面积 $\hat\rho=.02+.28u$，$u$ 为归一化答案熵。
- 奖励 $(1-|\rho-\hat\rho|)$。
- 门控 $1-\exp(-([c^{bu}]_++c^{ea}))$。

## 信息

- 需要 GT 答案，用来筛选成功轨迹；**不需要中间框标注**。
- 估计者因成员而异：
  - 同组成功轨迹的框集合：MedVR、AdaptVision 的面积均值；
  - 策略自身 teacher-forced 答案熵：CAVE；
  - 外部 GPT4o 判断 crop 是否相关（AdaptVision 的 $R_{crop}$，见 PC-F4-04）。
- 看不到的信息：这块区域是否必要；同状态不裁时的结果。

## 成立条件

- 每组至少有 2 条成功的裁图轨迹。MedVR 只在 $|T^+|>1$ 时计算，≤1 时的 fallback 未定义（litscan:71995 degenerate_cases）。
- 策略已有基本 crop 能力：MedVR 无 SFT 冷启动，依赖 Qwen 指令/JSON/crop 先验（litscan:71995 pitfalls）；CAVE 先做 10k SFT（2605.16416 conditions）。
- 低分辨率坐标与原图裁剪的比例要对应（litscan:63255 Eq10 pitfalls）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:71995 | 成功框逐像素多数票 + IoU>.5 | Table2 p7 | 文本 RL 94.50/53.40/21.38；纯 tool 94.31/52.62/22.26；EVR+CCA 96.77/54.31/26.38；3B OmniMedVQA 文本 RL 93.8 > MedVR 92.1（Tables1/3） | 记录未覆盖 | 正（7B），3B 有反例 |
| litscan:63255 | 相对成功裁图均值面积罚 + 直答/工具平衡罚 | Eq8–10；§5.3；Fig4；Table1 | 33% 视觉 token 保留 97.9% 相对表现；无工具奖约 10 步塌到全直答；无 balance 则过度用工具 | 记录未覆盖 | 正（效率），MathVerse 42.3 < vanilla 46.3 |
| 2605.16416 | 熵目标面积，进展门控 | Table4a p8；Table5 p9 | 去 focus：TV 29.3 vs 31.3，Baby 16.5 vs 17.3，TRACER-Core 35.2 vs 36.9，MME-RS 57.6 vs 59.2；完整系统 DeepEyes 调用 1.97→2.03 | 记录未覆盖 | 正（准确率），未减少调用 |

## 成功条件 / 失败模式

**成功条件**
- 成功轨迹的框有共同的"正确区域"；
- 组内有面积差异；
- 门控只作用于成功轨迹。

**失败模式**
- **共识可能是共同偏差**：共享 fork 前缀带来样本相关，成功者给自己投票（litscan:71995 failure_boundary, pitfalls）；空 footprint 时 IoU 为 0/0（litscan:71995 degenerate_cases）。
- **面积只是相对的**：所有成功裁图等比例放大时，area/mean 不变，不保证绝对面积最小；只有一个成功裁图时没有罚（litscan:63255 invariance / degenerate_cases）。
- **平衡罚误伤直答**：$r<.2$ 时正确直答也被罚 −.1，不能恢复稀有的直答支撑（litscan:63255 Eq8 failure_boundary）。
- **CAVE 公式不全，且不罚冗余**：
  - NormEntropy 公式与 top-k 重归一化方式未给全（2605.16416 failure_boundary）；
  - 无进展时 af=0，不是负奖（2605.16416 failure_boundary）。

## 审稿期望

推断：
- 与 GT 框的一致率，在有框子集上报告；
- 打乱共识（换成别题的共识）对照；
- 单成功组、空共识的比例；
- 是否压低直答比例。

## 认知障碍

- 中间框标注昂贵，而"答对的轨迹大多看对了地方"这一假设成本为零。
- 但同一策略的成功样本共享前缀和偏差，共识不等于正确，更不等于必要。前人多把它当伪 GT，而没有做外部校准（litscan:71995 lesson）。

## 工程经验

- **用成功共识作伪标签时**：要单独消融"探索"与"共识奖"，检查自身投票、fork 相关性、空集与单成功分支（litscan:71995 lesson）。
- **用相对面积时**：要同时检查 direct 分支实际收到什么信号，以及各通道为空时的 fallback（litscan:63255 lesson：无正确样本时 r 为 0/0，无成功正确裁图时面积均值为空）。
- **teacher-forced 熵用于目标面积时**：scoring pass 不得进入 rollout（2605.16416 App.E pitfalls）。

