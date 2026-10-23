---
id: PC-F4-06
name: 用当前策略"有/无视觉输入（或去掉该视觉步）"的两次前向或续写之差作在线奖励
family: F4_perception
status: candidate_pattern
problems: {P41: 2, P42: 2, P43: 2, P01: 2, P29: 1}
members: [2608.21883, litscan:75333, 2605.18641]
rs_patterns: [heterogeneous_decomposition, self_supervised_signal_engineering]
---
## 操作

对同一已生成前缀，用当前策略各算一次"有视觉"和"去掉视觉（或去掉该视觉步）"的读数，取差作奖励。三种形式：

**1. VIG（2608.21883 Eq2–4）**：熵差，think 段内取均值后 clip，进入序列奖励。

$$\mathrm{VIG}(t)=H_{txt}(t)-H_{vis}(t),\quad R=.1R_{fmt}+R_{acc}+\operatorname{clip}(\overline{\mathrm{VIG}},-1,1)$$

**2. MIRL（litscan:75333 Eq5；C.3 Eq18–19）**：描述前缀的 log-prob 差。

$$s(D)=\tfrac1{|D|}\sum_t[\log p(y_t|I,q,y_{<t})-\log p(y_t|q,y_{<t})],\quad r_{MI}=\operatorname{clip}(s,0,.5)/.5$$

- 先按 $s(D)$ 选 top-K 描述再分叉推理；
- 描述与推理分开给奖励。

**3. 去视觉步续写（2605.18641 App.E Eq5）**：从同一前缀去掉 latent 块后重新续写，按四格给奖：

| 带 latent | 去 latent | 奖励 |
|---|---|---|
| 对 | 错 | +n |
| 对 | 对 | −n/2 |
| 错 | 对 | −n/2 |
| 错 | 错 | 0 |

## 信息

- **估计者**：当前在线策略，同一权重，非冻结读者。
- **前缀**：VIG 与 MIRL 只做打分前向（stop-grad）；RN 要再生成一条续写。
- **"无图"条件的局限**：
  - 前缀仍由看图的策略生成，可携带先前的视觉信息；
  - "无图"本身对模型是分布外输入，会产生负的 VIG（2608.21883 §3.2.2；App.C）。
- **看不到**：
  - 视觉事实的真假，高分幻觉无法排除（2608.21883 failure_boundary）；
  - 裁图相对直答的动作价值。

## 成立条件

- 两种模式（如 latent / 无 latent）都在策略支撑内（2605.18641 conditions）。
- 奖励中保留结果正确性。MI-only 弱于组合：68.81 vs 70.22（litscan:75333 Table2）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2608.21883 | 熵差 VIG，序列奖励 | Table1；Table5(a)；Table6(a) p16 | 8B：VIG AvgACC 64.92 / TLen 1524.3；GRPO 62.88 / 1975.4。五基准：VIG 71.37，confidence-only 68.21。**删除 50% 最低 VIG 句后 ACC 72.36，删最高 VIG 句 80.75** | 单次训练，未报跨种子 | 压缩有效；低 VIG ≠ 可删 |
| litscan:75333 | 描述 log-prob 差筛前缀 + 分段奖励 | Table2；Table3 | top-MI 70.22，同 fork random 68.74，MI-only 68.81；Table3 VL task-only 65.23 > decoupled 63.46 | 记录未覆盖 | 弱正，正文与附录定义冲突 |
| 2605.18641 | 去 latent 续写的四格必要性奖励 | App.E pp.16–17 Eq5；Fig2；Table10 | 比 VLPO **更快压低 latent 使用**；MathVista 60.5→71.3，但 MMVP 73.0→65.0 | 单 run | 驱动模式消失 |

## 成功条件 / 失败模式

**成功条件**
- 结果正确性仍是主奖励；
- 有/无视觉的对照只用于加权或筛选。

**失败模式**
- **低依赖 ≠ 可删。** VIG 训练后删除最低分句子伤害最大（72.36 vs 80.75），GRPO 链上的排序则相反（2608.21883 Table6(a)/(b)）。
- **均值稀释关键细节。** 单个关键视觉细节会被长代数推导稀释；密度奖励改变内容偏好，且不保持最优策略（2608.21883 invariance, degenerate_cases）。
- **RN 推向模式移除。** 对"冗余但成功"的 latent 记 −n/2，会把 latent 模式推向消失（2605.18641 failure_boundary）；单次再生成噪声大，"双错=0"也不能证明搜索合理。
- **分段路由定义不一致。** MIRL 正文 3.3、Table3 与 C.3 三处的路由说法互相冲突（litscan:75333 signal_routing）。

## 审稿期望

推断：
- confidence-only 对照（2608.21883 有）；
- 图像打乱负对照；
- 等 token 删除；
- 当前策略的匹配反事实，即同形替换而非删除（见 PC-F4-08）；
- 多种子。

## 认知障碍

"去掉图像看模型变多少"直观且只需前向；它被当成互信息的代理（2608.21883 Eq1）。但删除输入制造的是分布外条件，而且有图前缀已泄露视觉信息。作者自己的删除实验推翻了"低分可删"的强解释（2608.21883 Table6）。

## 工程经验

- **算有图/去图熵差时**：分开审计打分 mask 与 actor loss mask。整链优势仍会改写终答（2608.21883 lesson）。
- **去图 span 时**：要干净删除并保持同一文本位置的对应。负 VIG 来自无图分布外输入和数值误差；clip 只是把值限定在区间内，不能修正负值（2608.21883 pitfalls）。
- **缓存前缀分叉时**：单独核对共享前缀的 loss 计权、未被选中分支的 accuracy 缺失，以及总前向成本（litscan:75333 lesson：Table5 含开销为 86.3%，不是省 25%）。

