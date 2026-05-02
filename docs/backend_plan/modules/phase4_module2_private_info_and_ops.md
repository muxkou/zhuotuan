# 阶段四 模块二：私密信息与房间运维能力

## 1. 模块目标

支持多人房间中的私密信息、暗骰、权限与运维需求。

---

## 2. 输入输出 contract

输入：

- 房间成员列表
- 消息或状态对象
- 可见性规则

输出：

- 过滤后的可见事件
- 审计日志记录
- 权限矩阵

---

## 3. 建议脚本

1. `scripts/phase4/check_visibility_rules.py`
2. `scripts/phase4/simulate_secret_delivery.py`
3. `scripts/eval/eval_room_auditability.py`

---

## 4. 完成标准

1. 多人房间的隐私与运维边界清晰
2. 私密信息不会错误暴露给非目标玩家
3. 审计日志可还原关键操作
