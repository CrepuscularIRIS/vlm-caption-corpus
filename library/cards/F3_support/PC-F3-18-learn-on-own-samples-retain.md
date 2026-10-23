---
id: PC-F3-18
name: 在当前策略自己的样本上学习（RL、逐轮刷新的自采 SFT、稳定教师的在线自蒸馏）以减少遗忘
family: F3_support
status: candidate_pattern
problems: {P61: 3, P63: 2, P62: 2, P42: 2}
members: ["litscan:76009", "litscan:75750", 2606.08719, "litscan:64330", "litscan:75845"]
rs_patterns: [self_supervised_signal_engineering, controlled_diagnostic_design]
---

## 操作

让训练数据来自当前策略的分布，而不是固定的外部或初始数据：
- 逐轮从当前策略重新采样正确答案做 SFT（Iterative-SFT，litscan:76009）；
- 学生自己 rollout，带示范/特权信息的教师在**同一学生前缀**上给分布，最小化反向 KL（litscan:75750 §3.1；2606.08719 Eq1）；
- RL 中对自己的"正确且格式有效"样本加辅助 CE（litscan:75845 Eqs1–4）。

## 信息

- 当前策略的样本；教师额外看到示范 c（litscan:75750）、GT crops 与答案（2606.08719）、或只是历史参数（litscan:64330，无额外 GT）。
- 不看动作必要性。

## 成立条件

- 当前策略在目标行为上有正确支持；否则自采数据为空（litscan:76009 DEGEN："当前策略完全没有正确支持时，正确筛选 Self/Iterative-SFT 无可用数据"）。
- 教师不能与学生同步更新：2606.08719 的在线教师（每次更新用当前学生）在三个基准上得 0.0（Table4 §5.3）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| litscan:76009 RetainDo | GRPO / 无优势 REINFORCE / 正确样本 SFT / 逐轮刷新 SFT | Table1 | Llama8B Countdown：SFT gain 25.5 / drop 36.4；REINFORCE 7.5 / −.8；GRPO 60.4 / −.5 | 记录未覆盖 | 支持：on-policy 数据遗忘少 |
| litscan:75750 SDFT | 示范条件化 EMA 教师，学生前缀反向 KL | Appendix Table5 | 科学 QA 新任务 70.2 vs SFT 66.2；旧任务均值 64.5 vs SFT 53.4、base 65.5；IFEval 66.8 低于 base 74.3 | 记录未覆盖 | 支持；非零遗忘 |
| 2606.08719 Imagine-OPD | 冻结特权教师（同 base，见 GT crops + 答案）在学生前缀上逐 token KL | Table4; §5.3 | Qwen3-VL-4B base/GRPO/frozen OPD：V* 80.1/83.8/88.0；在线教师 0.0 | 未报告 | 支持冻结教师；在线教师崩溃 |
| litscan:64330 GTR-Turbo | TIES 合并历史 checkpoint 作教师，thought-only KL（负估计截断）从 PPO 优势中减去 | Table2; Eq6–7 | Points24 成功率 SFT 22.0 → KL 版 53.5，GTR 44.5；初始成功 <5% 可能失败 | 记录未覆盖 | 支持 |
| litscan:75845 Spotlight | GSPO + 对正确且格式有效的自身样本加 λ·CE，λ 1→.01 | Eqs1–4; §3.2–3.3; Table4 | GRPO/GSPO 约 300 步工具语法退化；持续更新 reference 降低准确率 | 未报告 | 支持（防退化） |

## 成功条件 / 失败模式

- 成功条件：on-policy 数据 + 稳定教师。
- 失败模式 1：教师同步更新 → 崩溃（2606.08719 Table4：0.0；作者未独立诊断原因）。
- 失败模式 2：仍有遗忘，非零（litscan:75750 Table5：IFEval 66.8 < 74.3）。
- 失败模式 3：当前策略在该行为上无正确支持时，所有 on-policy 保留方法都没有数据（litscan:76009 DEGEN）——这正是 P29 后的直答。
- 失败模式 4：单峰 Gaussian 下反向 KL 反而更遗忘，多峰只是直觉（litscan:76009 §3.2–3.3）。
- 失败模式 5：采样 logprob 差当 KL 奖励时，负估计会反向激励偏离，需截断（litscan:64330 LESSON）。

## 审稿期望

推断：要求同目标收益下比较遗忘（RetainDo 指出 REINFORCE 遗忘少但收益也低）；要求报告教师更新频率的消融（GTR-Turbo 有 EMA α 扫描：极高/低 α 退化）。

## 认知障碍

- mode-seeking 通常被认为丢模式，但在多模式策略中只移动新模式反而保留旧模式（litscan:76009 rs.why_non_obvious）。
- 同初始化不等于实时共享策略；冻结的特权教师有效而在线教师归零（2606.08719 LESSON）。

## 工程经验

- 当用特权输入做自蒸馏时，先钉住教师，显式记录 GT 答案/区域与学生可见像素，并用信息消融排除"只靠答案提示"的解释（2606.08719 LESSON）。
- 当 teacher 由当前 student 条件化而来时，直接同步容易放大概率扰动，用 EMA 稳住（litscan:75750 LESSON）。
- 当只用初始策略的固定正确样本 SFT 仍遗忘时，试逐轮刷新采样，并同时追踪原能力、目标收益和采样总量（litscan:76009 LESSON）。

