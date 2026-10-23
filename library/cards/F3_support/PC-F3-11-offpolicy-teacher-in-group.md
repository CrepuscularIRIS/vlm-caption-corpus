---
id: PC-F3-11
name: 把离策略的教师/示范轨迹并入 GRPO 组内一起算优势，并对离策略 token 做概率重加权、取消 clip
family: F3_support
status: case
problems: {P25: 3, P29: 2, P27: 2, P01: 2}
members: [2504.14945]
rs_patterns: [heterogeneous_decomposition]
---

## 操作

每组 G=8：7 条当前策略 rollout + 1 条正确的教师轨迹，共用组内基线计算优势 $\hat A_i=R_i-\mathrm{mean}(G_{on}\cup G_{off})$（§4 实际训练为 mean-only；Eq4 展示版另除 std）。教师 token 的重要性比替换为 $f(\hat r)=\hat r/(\hat r+\gamma)$，$\gamma=0.1$，且不 clip（Eqs5–6）；学生 token 照常用 clipped ratio。熵系数 .01，KL 0（ROUTE 字段）。

## 信息

- 教师：DeepSeek-R1 的正确轨迹，45k 条、≤8192 token（COND 字段）；只用文本，不读教师 logprob（PIT：避免 tokenizer 不一致，因而是近似而非真实 IS）。
- 奖励：MathVerify 终答正确性，无格式/长度奖励。
- 推理时无教师。

## 成立条件

- 教师轨迹正确，且在当前协议下可以重放（数学单轮文本）。
- 教师路径对学生"陌生"，直接混入会偏向已高概率 token 导致熵塌缩，故需 f(p) 重加权（rs.why_non_obvious）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2504.14945 LUFFY | 7on+1off；f(p)=p/(p+.1)；off 不 clip | Table4 p21 | 同设置 on-policy 平均 45.5→50.1；mixed 44.4 → +shaping 47.8 → +NoClip 50.1；OOD 57.3→57.8 | 记录未覆盖 | 支持 |
| 同上（负结果） | on-policy 也加 shaping | Table4 | 45.5→42.0；+NoClip 44.9 | — | shaping 只对离策略 token 有用 |
| 同上（负结果） | Llama 底座 | Table3 | LUFFY 13.2 优于 on 9.6，但低于 Instruct 17.1 | — | 并非所有底座超指令版 |

## 成功条件 / 失败模式

- 成功条件：离策略样本只占组内少数（1/8），重加权避免熵塌缩。
- 失败模式 1：shaping 用在 on-policy token 上反而降分（Table4 42.0）。
- 失败模式 2：教师错误或教师行为在学生处无支持时不会自动解决；真实零概率 token 无法被有限的相对权重创造（DEGEN 字段）。
- 失败模式 3：Eq4/5 的 std 与 token 分母和 §4 的去 normalization 声明不一致，最终固定分母未列（PIT 字段）。

## 审稿期望

推断：要求对比"离策略样本先 SFT 再 RL"的同预算基线；要求报告教师 token 的梯度占比与熵曲线；要求说明近似 IS 的偏差。

## 认知障碍

- 直接混入教师会让策略偏向已高概率 token，导致熵塌缩；重加权改变了实际学到的 token（rs.why_non_obvious）。
- 普遍以为 off-policy 数据只能放在 SFT；这里放在 RL 组内与学生样本竞争基线。

## 工程经验

- 当把离策略样本放进组内时，只对离策略 token 做 shaping；对 on-policy token 做同样 shaping 会降分（2504.14945 Table4）。
- 当不读取教师 logprob 时，π_φ 设为 1，比率退化为 π_θ，这是近似 IS，需在文档中写明（ROUTE、PIT 字段）。
- 多轮视觉协议下，离策略轨迹的裁图观测必须按原 bbox 重新执行或复用原图像，并与 token 位置对齐（P54/P55 已知坑）。

