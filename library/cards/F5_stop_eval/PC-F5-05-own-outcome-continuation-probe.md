---
id: PC-F5-05
name: 冻结宿主策略，用它自己续写的终局结果训练"继续价值"探针，低于阈值就停或弃答
family: F5_stop_eval
status: candidate_pattern
problems: {P35: 3, P31: 2, P33: 2, P34: 2, P24: 1, P04: 1}
members: [2604.18419, 2610.05400, 2606.15099, 2610.13821]
rs_patterns: [heterogeneous_decomposition, controlled_diagnostic_design]
---
## 操作
固定生成策略不训练，在它自己的完整轨迹上为每个前缀构造"继续下去的终局结果 / 现在停的结果"标签，训练一个轻量头（BCE probe、Ridge、校准 selector），部署时与一个外部效用比较决定停：
- Knowing When to Quit：$V_0(h)=P_\pi(r=1\mid h)$，$L=\mathbb E\sum_{t<c}\mathrm{BCE}(\hat V(h_t),r)$，$\hat V_\beta(h)<r_\perp$ 即弃答（2604.18419 Eqs8/12–13）。
- CASE：$g_\lambda=L_{stop}-\min_{\text{later or native}}L$，其中 $L=1[a\ne Y]+\lambda C/S$；Ridge 拟合，$\hat q+\lambda\hat c_\lambda\le$ boundary 即 STOP（2610.05400 Eq2–9，F1 digest）。
- Think Less Act Early：校准阶段用额外推理的边际改善做标签，gate $g(z)>\tau$ 即退出（2606.15099 signatures）。
- Learn When to Abstain：固定生成器，LoRA 以 True−False logits 做 BCE，校准集 logistic 映射后阈值筛选（2610.13821 Table2 signature）。

## 信息
宿主策略自身前缀的隐状态/因果特征；训练标签来自宿主自己续写的终局正确性（与成本）。部署时只用当前前缀，不看未来。估计者：外接头，不是策略本身。

## 成立条件
- 停止的备选效用固定（弃答 utility $r_\perp$ / 成本 λ）。
- 停止不改变后续可获得的信息——Quit 的终止是固定 utility；crop 后继续会有新观测，这一点不满足时不能直接类比（2604.18419 transfer_mapping）。

## 成员证据
| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2604.18419 Knowing When to Quit | BCE 价值探针 + 首次低于阈值即弃答 | §6.1/Fig2；Prop4.9 | Olympiad Phi3 基座 16%，90% 弃答时 selective 64% vs 最佳基线 34%；Qwen selective 91% vs 75%；动态通常比 input-only 省 token 少 | 5 seeds（42–46）独立重训探针，±1SD；校准 20 次随机半分 | 记录未覆盖 |
| 2606.15099 Think Less Act Early | 校准 gate 提前退出内部 latent 推理（VLA） | Table2；Table5 | 312→145 ms，latent 5→2.3 次；SR 98.0→98.3 | 记录未覆盖 | 记录未覆盖 |
| 2610.13821 Learn When to Abstain | 固定生成器 + 校准 selector，对比生成策略 RL | Table 2 | TriviaQA utility .0425/coverage 30.9%/risk 14.5%，原校准 filter .0242/20.2%/23.0%；NQ utility 仍 −.0120 | 记录未覆盖 | 记录未覆盖 |

## 成功条件 / 失败模式
- 成功条件：宿主固定、停止后不再有新信息、探针输入与标签时间下标对齐。
- 失败模式：
  - Selective accuracy 只算留下的样本，不等于总体正确率或 coverage 非劣（2604.18419 failure_boundary）。
  - 与 k>1 定点比较的优势需要"无 recovery-surplus"等条件，并非无条件支配；低当前值的轨迹未来可能恢复（2604.18419 degenerate_cases、why_non_obvious）。
  - CASE 的端到端增益包含 finalizer 变化；统一 finalizer 后为 −1.92pp（2610.05400 negative_results）。最佳已实现后缀是带前视的乐观 surrogate，不是无偏最优停止价值（2610.05400 why_non_obvious）。
  - NQ 上 selector 不胜"总是弃答"（2610.13821 failure_boundary）。

## 审稿期望
- 同时报 coverage 与 fallback 效用；把 oracle-value 保证、学到的排序表现、计算节省分开（2604.18419 lesson）。
- 两臂用同一 finalizer；控制器的 probe 开销与校准 fallback 计入报告（2610.05400 lesson）。
- 不把评测 bootstrap 当训练种子方差（2610.05400 pitfalls）。

## 认知障碍
要预测的是"最终成功"而不是"当前局部答案对不对"（2604.18419 why_non_obvious）；当前置信度不等于续看价值（2610.05400 why_non_obvious）；好的排序不保证分布外正效用，且中心化会吃掉阈值成本（2610.13821 why_non_obvious）。

## 工程经验
- 当用 hindsight 最佳未来答案构造停止标签时，部署特征不得含未来信息（2610.05400 pitfalls）。
- 当评估外接停止器时，强制 finalizer 必须两臂一致（2610.05400 lesson）。
- 当停止监督来自证据覆盖或终局结果时，要检查决策输入与标签的时间下标（2604.17866 lesson，见 PC-F5-06）。

