---
name: django-model
description: Django Model 字段规范、Meta 约定、外键命名模板 — 本项目标准
---

# django-model — Django Model 规范模板

本项目使用 Django ORM，所有 Model 遵循以下约定。

## 命名规范

| 项 | 规范 | 示例 |
|----|------|------|
| Model 类名 | 单数、驼峰 | `Venue`, `Court`, `Booking` |
| 表名(db_table) | 蛇形、复数 | `venues`, `courts`, `bookings` |
| 外键字段 | `<related_model>_id`（Django 自动） | `venue_id`, `user_id` |
| related_name | 蛇形、语义化 | `bookings`, `courts` |
| 布尔字段 | `is_<adj>` 或 `has_<noun>` | `is_active`, `has_paid` |

## 基类

所有 Model 继承自项目基类 `BaseModel`：

```python
from django.db import models

class BaseModel(models.Model):
    """项目公共基类 — 所有 Model 必须继承"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
```

## 字段类型速查

| 业务场景 | 字段类型 | 约束 |
|----------|----------|------|
| 手机号 | `CharField(max_length=11)` | `unique=True` |
| 密码 | `CharField(max_length=128)` | Django 内置哈希 |
| 金额 | `DecimalField(max_digits=10, decimal_places=2)` | 不用 FloatField |
| 状态/角色 | `CharField(max_length=20, choices=XXX)` | 枚举常量定义在 Model 顶部 |
| 日期 | `DateField` | — |
| 时间 | `TimeField` | — |
| 日期时间 | `DateTimeField` | — |
| 软删除 | `BooleanField(default=False)` | `is_deleted` |
| JSON 数据 | `JSONField` | Django 3.1+ |

## choices 定义规范

```python
class Booking(BaseModel):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待支付'),
        (STATUS_PAID, '已支付'),
        (STATUS_CANCELLED, '已取消'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='状态',
    )
```

## Meta 类约定

```python
class Meta:
    db_table = 'bookings'           # 表名
    verbose_name = '预约订单'        # 单数中文名
    verbose_name_plural = verbose_name
    ordering = ['-created_at']       # 默认排序：最新在前
    indexes = [
        models.Index(fields=['user', 'status']),
        models.Index(fields=['court', 'date']),
    ]
    constraints = [
        # 同一场地同一日期同一时段唯一
        models.UniqueConstraint(
            fields=['court', 'date', 'time_slot'],
            name='uq_court_date_timeslot',
        ),
    ]
```

## 外键 & 级联

```python
# 场馆 (一对多：场地)
court = models.ForeignKey(
    'venues.Court',
    on_delete=models.PROTECT,        # 已被预约的场地不可删除
    related_name='bookings',
    verbose_name='场地',
)

# 用户 (一对多：订单)
user = models.ForeignKey(
    'users.User',
    on_delete=models.CASCADE,        # 删用户则删其订单
    related_name='bookings',
    verbose_name='用户',
)
```

## __str__ 规范

```python
def __str__(self):
    return f"Booking #{self.id} - {self.user.phone} @ {self.court.name}"
```
