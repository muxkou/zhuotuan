from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.enums.game import ArtifactSource, ValidationStatus


class ArtifactMeta(BaseModel):
    """描述一个 artifact 文件本身的元信息。"""

    model_config = ConfigDict(extra="forbid")

    artifact_type: str = Field(
        description="产物类型，例如 world、module、character、session、report。"
    )
    schema_version: str = Field(
        default="v1",
        description="当前 artifact 使用的 schema 版本号。",
    )
    generated_by: str = Field(description="生成该产物的脚本或服务名称。")
    case_id: str = Field(description="本次实验或样例的唯一标识，便于回放和追踪。")


class BaseArtifact(BaseModel):
    """所有核心领域产物共用的基础字段。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="领域对象唯一标识，例如某个 world、module 或 character 的 id。")
    version: str = Field(default="v1", description="该对象本身的版本号，用于后续演进和兼容控制。")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="对象创建时间，使用 UTC 保存。",
    )
    source: ArtifactSource = Field(
        default=ArtifactSource.SYSTEM,
        description="该对象来源，例如人工填写、LLM 生成、系统内置或导入。",
    )


class ErrorItem(BaseModel):
    """统一的错误或警告描述结构。"""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(description="错误码，供程序判断具体错误类型。")
    message: str = Field(description="给开发者或调用方看的可读错误说明。")
    field_path: str | None = Field(
        default=None,
        description="出错字段路径，例如 attributes.physique。",
    )
    severity: Literal["info", "warning", "error"] = Field(description="问题严重程度。")
    suggestion: str | None = Field(default=None, description="建议修复方式。")


class ValidationReport(BaseModel):
    """统一的校验结果报告结构。"""

    model_config = ConfigDict(extra="forbid")

    status: ValidationStatus = Field(description="整体校验结果：通过、警告或失败。")
    hard_errors: list[ErrorItem] = Field(default_factory=list, description="阻塞性错误列表。")
    warnings: list[ErrorItem] = Field(default_factory=list, description="非阻塞性警告列表。")
    suggestions: list[str] = Field(default_factory=list, description="面向修复或增强的建议列表。")
    metrics: dict[str, float | int | str] = Field(
        default_factory=dict,
        description="校验过程中的指标数据，例如耗时、数量、分数。",
    )
