# 阶段五 模块二：创作者发布与分发 API

## 1. 模块目标

将模组蓝图包的发布、检索、版本管理与评价相关能力 API 化。

---

## 2. 建议 API

1. `POST /v1/creator/packages`
2. `POST /v1/creator/packages/{package_id}:validate`
3. `POST /v1/creator/packages/{package_id}:publish`
4. `GET /v1/packages`
5. `GET /v1/packages/{package_id}`

---

## 3. 契约要求

1. 发布接口只接受通过校验的蓝图包
2. 查询接口返回包元数据和兼容性信息

---

## 4. 完成标准

1. 创作者生态具备后端发布入口
2. 分发能力与运行时引擎兼容
3. 发布 API 只接受合法蓝图包
