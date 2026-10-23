---
id: PC-F5-10
name: 用同题配对的胜/负账本和单侧检验做验收，并只在未参与选择的不相交集上判一次
family: F5_stop_eval
status: candidate_pattern
problems: {P51: 3, P47: 3, P61: 2, P49: 1, P69: 1}
members: [2609.36043, 2610.12601, 2406.19314]
rs_patterns: [controlled_diagnostic_design, identify_hidden_assumption]
---
## 操作
- 逐题配对候选与现任：分别计 wins（错→对）与 regressions（对→错），用非对称准则加单侧配对检验决定接受，否则 abstain（2609.36043 signatures、rs.key_step）。
- 判定集与选择集不相交：按主题划分 train/validation/held-out（24/24 题、各 12 个 topic，held-out 500 题 254 个 topic），冻结候选后在新主题上复测（2610.12601 information）。
- 题池按时间刷新：每月替换约 1/6，最新 1/6 暂不公开；任务→类别→总体逐层平均（2406.19314 rs.key_step、signatures）。

## 信息
每题二值成功（候选 vs 现任）；题目的主题/来源标签；题目发布时间。

## 成立条件
- 候选在判定前已冻结；判定集从未用于选择（2609.36043 notes：作者 §5.2 明确重复使用 validation 不能控制轨迹级错误接受，见 readings/2609.36043.json notes）。
- 主题划分要真正不相交；2610.12601 按 article slug 定义 topic，是否语义去重未知（readings/2610.12601.json notes）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2609.36043 SAGE | 非对称配对准则 + 单侧检验，预算匹配 | Abstract | 19/20 配置回归率下降、1 个持平；DeepSeek-V4 LiveMath 回归率 36.5%→0，最终 34.15→48.78 | 记录未覆盖 | 记录未覆盖 |
| 2610.12601 反思式 prompt 优化 | topic-disjoint held-out + 配对题 bootstrap + 胜负计数 | Abstract；§4.2 | Δ.079 CI[.051,.107]，但 287 win / 147 loss / 66 tie | 3 optimizer seeds | 记录未覆盖 |
| 2406.19314 LiveBench | 时间刷新、部分私有、客观评分 | Table1 / §3.4 | 两次更新排名相关均 >0.997，但 mean/median 分约下降 1.2% | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：判定只做一次；回归计数与均值同时报告。
- 失败模式：
  - 平均提升掩盖退化：Δ 显著为正时仍有 147 题由对变错（2610.12601 §4.2）。
  - SAGE 的统计保证只针对固定的一对候选，不能替代多种子封存的非劣协议（2609.36043 known_failure_check）。
  - SAGE 记录中公式与主表数字缺失，§3.3 截断，检验统计量、阈值和样本量**记录未覆盖**（2609.36043 failure_boundary）。
  - 时间刷新不证明无污染；公开后仍可能泄漏；版本不同不能当完全相同的测量（2406.19314 failure_boundary、why_non_obvious）。
  - 验证−测试差不是记忆量的可靠估计（2610.12601 why_non_obvious）。

## 审稿期望
- 报告已会题的回归率，不只报均值（2609.36043 relevance P51）。
- 说明最终测试集从未用于设计；topic/来源不相交（2610.12601 relevance P47）。
- 固定版本、解析规则与类别权重，防跨版本误比（2406.19314 relevance P49）。

## 认知障碍
平均增益能掩盖已会题的退化，且"从多个候选里挑最好的"本身受噪声偏差（2609.36043 why_non_obvious）。公开题会很快进入训练数据（2406.19314 why_non_obvious）。领域习惯是在同一个 dev 集上反复挑方法、报点估计。

## 工程经验
- 当用配对胜负账本判定时，要保存逐题、逐采样的原始输出，而不是只存汇总准确率，否则事后无法重算（推断，自 2609.36043 与 2610.12601 的逐 item 统计要求）。
- 当 benchmark 版本更新时，必须固定版本号与解析规则，跨版本成绩不能直接相减（2406.19314 relevance P49）。

