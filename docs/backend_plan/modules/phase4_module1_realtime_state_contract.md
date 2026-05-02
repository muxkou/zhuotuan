# 阶段四 模块一：多人在线状态契约

## 1. 模块目标

在已有稳定回合引擎基础上，补足多人在线场景需要的状态契约与事件流设计。

---

## 2. 建议代码落点

```text
backend/app/domain/schemas/realtime.py
backend/app/application/services/event_stream_builder.py
backend/app/application/services/state_recovery_service.py
```

---

## 3. 输入输出 contract

输入：

- `TurnRecordSchema`
- `SessionRuntimeState`

输出：

- `RoomEvent`
- `StateSnapshot`
- `StateDelta`

---

## 4. 建议脚本

1. `scripts/phase4/simulate_room_event_stream.py`
2. `scripts/phase4/replay_incremental_updates.py`
3. `scripts/eval/eval_realtime_consistency.py`

---

## 5. 完成标准

1. 单场回合可转成事件流
2. 断线后能用快照 + 增量恢复
3. 连续 50 个事件回放一致性为 100%
