# models 模块说明

本文档梳理 `src/ai_stock/sector_rotation/models` 目录下的核心数据类与函数，解释它们在板块强弱及轮动预测中的角色与交互方式。

## multi_factor.py

### StrengthBreakdown
- 类型：`dataclass`
- 作用：保存单个板块在趋势、情绪（hype）、资金（capital）、龙头（leader）四个因子上的加权得分分解，便于后续查看贡献占比。
- 字段：`trend`、`hype`、`capital`、`leader`，分别对应输入因子的加权得分。
- 便利方法：`as_dict` 将分解结果转换成字典，方便序列化或直接展示。

### RotationBreakdown
- 类型：`dataclass`
- 作用：保存轮动模型在相对滞后、资金溢出、情绪溢出、技术准备度四个维度上的加权得分。
- 字段：`relative_lag`、`capital_spillover`、`hype_spillover`、`technical_readiness`。
- 便利方法：`as_dict` 同样将分解结果转换成字典。

### combine_strength_score(trend, hype, capital, leader, weights)
- 作用：根据配置的 `FactorWeights`，把各因子组件的原始得分乘以权重，生成 `StrengthBreakdown`。
- 参数：
  - `trend` (`TrendComponents`)
  - `hype` (`HypeComponents`)
  - `capital` (`CapitalComponents`)
  - `leader` (`LeaderComponents`)
  - `weights` (`FactorWeights`)：包含四个因子的权重。
- 返回：`StrengthBreakdown`，记录加权后的分解明细。

### combine_rotation_score(rotation, weights)
- 作用：对轮动组件的四个子因子应用 `RotationWeights`，输出 `RotationBreakdown`。
- 参数：
  - `rotation` (`RotationComponents`)
  - `weights` (`RotationWeights`)
- 返回：`RotationBreakdown`，用于后续计算轮动得分或直接展示分解。

### score_from_breakdown(breakdown)
- 作用：把 `StrengthBreakdown` 的四个部分求和，得到最终的综合强度得分。
- 返回：`float`，即趋势、情绪、资金、龙头四项加权得分之和。

### rotation_from_breakdown(breakdown)
- 作用：对 `RotationBreakdown` 的四个维度求和，得到轮动准备度的总分。
- 返回：`float`，即相对滞后、资金溢出、情绪溢出、技术准备度的加权总和。

## strong_board.py

### BoardScore
- 类型：`dataclass`
- 作用：描述单个板块的最终强度排序结果。
- 字段：`board`（板块代码）、`name`（板块名称）、`score`（加权总分）、`breakdown`（各因子得分的字典）。

### rank_boards(trend, hype, capital, leader, board_names, weights)
- 作用：将不同来源的因子得分整合成最终的板块强度排名。
- 步骤：
  1. 取趋势、情绪、资金三项共同覆盖的板块集合。
  2. 对每个板块，使用 `combine_strength_score` 计算加权分解；若缺失龙头数据则用 `create_empty_leader_components` 补零。
  3. 将分解的合计值作为最终得分，附带原始分解明细，构建 `BoardScore` 实例。
  4. 按得分从高到低排序返回。
- 返回：按得分降序排列的 `List[BoardScore]`，适用于展示强势板块榜单。

## rps_predict.py

### RpsCandidate
- 类型：`dataclass`
- 作用：描述潜在的下一阶段轮动候选板块。
- 字段：`board`、`name`、`predicted`（预测得分）、`breakdown`（四个轮动子因子的字典表示）。

### predict_next_session(rotation, weights, smoothing=0.7)
- 作用：对当前轮动组件应用权重并进行平滑，生成下一交易日的轮动预测分数。
- 算法：
  1. 用 `combine_rotation_score` 得到分解后基准分数。
  2. 将基准分数乘以 `smoothing`（默认 0.7），再加上资金与情绪溢出项的原始值，增强短期信号响应。
- 返回：`Dict[str, float]`，键为板块代码，值为平滑后的轮动预测分。

### predict_rotation_candidates(strengths, rotation, weights, top_n=5, exclude_current=True, board_names=None)
- 作用：基于轮动因子选出最有可能出现资金切换的板块候选名单。
- 逻辑：
  1. 根据 `exclude_current` 决定是否排除当前强势榜单中的板块。
  2. 为每个候选板块计算 `RotationBreakdown` 与总分（`rotation_from_breakdown`）。
  3. 生成 `RpsCandidate`，记录预测总分及分解详情。
  4. 按预测分排序并截取前 `top_n` 个候选。
- 返回：长度不超过 `top_n` 的 `List[RpsCandidate]`，用于提示潜在的轮动方向。

## 模块间协作关系
- `multi_factor` 提供统一的权重组合与得分汇总工具，既可以用于当前强度打分，也能用于轮动准备度的计算。
- `strong_board` 使用 `multi_factor` 的强度组合函数，将各因子输出转化为可排序的榜单。
- `rps_predict` 借助 `multi_factor` 的轮动组合函数和 `strong_board` 生成的强势榜单，筛选潜在的下一波轮动对象，实现从“当前强势”到“未来候选”的衔接。
