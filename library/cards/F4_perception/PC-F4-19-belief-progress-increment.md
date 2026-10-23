---
id: PC-F4-19
name: 以当前策略在相邻真实状态下对金答案的 teacher-forced 似然增量作为过程分，并汇入轨迹奖励
family: F4_perception
status: case
problems: {P43: 2, P14: 2, P17: 2, P11: 1}
members: [2605.16416]
rs_patterns: [heterogeneous_decomposition]
---
## 操作

在 rollout 结束后，对每个真实状态 $M_t$，把金答案正文 teacher-force 进当前策略，计算平均 token log-prob。相邻两个状态的差就是 belief 增量（2605.16416 Sec.3.2.1 p4）：

$$V_{bu}(M_t)=\tfrac1{|\mathcal A|}\sum_i\log p_\theta(y_i^*|M_t,y_{<i}^*),\qquad c_t^{bu}=V_{bu}(M_{t+1})-V_{bu}(M_t)$$

然后依次处理：
1. 把增量裁剪到 $[-1,2]$；
2. 乘衰减系数 $.8^{t-1}$ 并求和；
3. 与 evidence、focus 两个通道按 .4/.3/.3 混合；
4. 做组 mean/std 归一化（2605.16416 Sec.3.3 / Alg.1 p5）。

## 信息

- 读数用到金答案正文，只在独立的打分 pass 中使用，不进入 rollout（App.E）。
- 看不到的信息：
  - 同一状态下不执行该动作的结果（不是 MC，也不是反事实，information 字段）；
  - belief 的增量来自新像素还是来自生成的文本。

## 成立条件

- 能在真实多模态上下文中重新打分。
- 答案 span 准确，不计格式前后缀。
- 金答案不污染后续 rollout。
- 先做 10k 条冷启动 SFT（2605.16416 conditions）。

## 成员证据

| paper_key | 变体 | 位置 | 报告效果（数字） | 种子/置信 | 决定 |
|---|---|---|---|---|---|
| 2605.16416 | belief 增量（单独 / 与其他两通道合用） | Table2 p7；Table4a p8；Table5 p9 | Belief-only overall 29.6%，Full 33.3%，基座 25.9%；去掉 belief：Tunnel Vision 28.9 vs 31.3，TRACER-Core 34.1 vs 36.9，MME-RS 56.7 vs 59.2；完整系统使 DeepEyes 调用 1.97→2.03 | 记录未覆盖 | 正（准确率），未减少调用 |

## 成功条件 / 失败模式

- **成功条件**：答案 belief 的提升确实由新观测引起。
- **失败模式**：
  - **来源混淆**：belief 增益可以来自生成文本或答案自一致性，未证明由新增像素引起；teacher-forced likelihood 不等于自然答案成功率（2605.16416 failure_boundary）。
  - **不是严格 PBRS**：不裁剪、不衰减时求和可望远镜相消，但 $.8^{t-1}$ 乘在 $V_{next}-V$ 上，而非 $\gamma V_{next}-V$；clip 与正部破坏了相消（invariance，读者推导）。
  - **单通道不够**：只用 belief 时 29.6 < Full 33.3，不能覆盖前置证据获取（negative_results）。

## 审稿期望

推断：
- 与 MC 成功率的一致性；
- 打乱状态顺序的对照；
- 把 belief 增量中"文本带来的部分"与"像素带来的部分"分开（需要类似 PC-F4-08 的反事实）。

## 认知障碍

只奖终答、或只看单一答案信息增益，会漏掉"尚未提高答案 belief 的前置证据"（2605.16416 why_non_obvious）。用 teacher-forced 读数代替 MC 分叉成本很低。但"before→after 的进展"与"这块像素的作用"是两回事，作者没有给出因果必要性证明。

## 工程经验

- teacher-forced 的金答案只能放在独立的 reward pass 中，不能注入真实的后续状态（2605.16416 App.E pitfalls）。
- 优化时要把工具返回、系统提示和环境注入信息的 response mask 设为 0（同上 Sec.3.3 pitfalls）。
- 奖励权重用训练来源构造的独立 validation 集选定，不用测试 benchmark 调参（同上 App.D.1 pitfalls）。

