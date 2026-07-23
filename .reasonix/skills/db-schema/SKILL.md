---
name: db-schema
description: MySQL 建表规范、索引建议、Django 迁移检查清单 — 本项目数据库规范
---

# db-schema — MySQL 建表规范模板

本项目使用 MySQL + Django ORM，建表遵循以下规范。

## 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 数据库名 | 蛇形、全小写 | `badminton_venue` |
| 表名 | 蛇形、复数 | `venues`, `bookings`, `time_slots` |
| 主键 | `id` (bigint AUTO_INCREMENT) | Django 默认 |
| 外键 | `<related>_id` | `venue_id`, `user_id` |
| 索引名 | `idx_<table>_<col>` | `idx_bookings_status` |
| 唯一约束 | `uq_<table>_<cols>` | `uq_court_date_timeslot` |

## 字符集

```sql
-- 数据库级别
CREATE DATABASE badminton_venue
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

Django settings：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'badminton_venue',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

## 核心表设计

```sql
-- 用户表（Django 自定义 User）
CREATE TABLE users (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    phone       VARCHAR(11)  NOT NULL UNIQUE,
    password    VARCHAR(128) NOT NULL,
    nickname    VARCHAR(50)  DEFAULT '',
    role        VARCHAR(20)  NOT NULL DEFAULT 'member',  -- admin / reception / member
    level       VARCHAR(20)  DEFAULT 'normal',           -- normal / gold
    balance     DECIMAL(10,2) DEFAULT 0.00,
    is_active   BOOLEAN      DEFAULT TRUE,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 场馆表
CREATE TABLE venues (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    address     VARCHAR(255) DEFAULT '',
    phone       VARCHAR(20)  DEFAULT '',
    is_active   BOOLEAN      DEFAULT TRUE,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 场地表
CREATE TABLE courts (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    venue_id    BIGINT       NOT NULL,
    name        VARCHAR(50)  NOT NULL,          -- 如 "1号场"
    is_active   BOOLEAN      DEFAULT TRUE,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (venue_id) REFERENCES venues(id),
    UNIQUE KEY uq_venue_name (venue_id, name),
    INDEX idx_courts_venue (venue_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 时段表
CREATE TABLE time_slots (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    start_time  TIME         NOT NULL,          -- 09:00
    end_time    TIME         NOT NULL,          -- 10:00
    price       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    is_active   BOOLEAN      DEFAULT TRUE,
    UNIQUE KEY uq_slot_time (start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 预约订单表
CREATE TABLE bookings (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT       NOT NULL,
    court_id     BIGINT       NOT NULL,
    date         DATE         NOT NULL,
    time_slot_id BIGINT       NOT NULL,
    status       VARCHAR(20)  NOT NULL DEFAULT 'pending',  -- pending / paid / cancelled
    amount       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (court_id) REFERENCES courts(id),
    FOREIGN KEY (time_slot_id) REFERENCES time_slots(id),
    UNIQUE KEY uq_court_date_timeslot (court_id, date, time_slot_id),
    INDEX idx_bookings_user (user_id),
    INDEX idx_bookings_court_date (court_id, date),
    INDEX idx_bookings_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 支付记录表
CREATE TABLE payments (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    booking_id  BIGINT       DEFAULT NULL,              -- 可为空（充值场景）
    user_id     BIGINT       NOT NULL,
    type        VARCHAR(20)  NOT NULL,                  -- recharge / booking
    amount      DECIMAL(10,2) NOT NULL,
    method      VARCHAR(20)  NOT NULL DEFAULT 'balance', -- balance / wechat / alipay
    status      VARCHAR(20)  NOT NULL DEFAULT 'success',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_payments_user (user_id),
    INDEX idx_payments_booking (booking_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 索引原则

| 原则 | 说明 |
|------|------|
| 主键 | 每表必须有自增 `id`（Django 默认） |
| 外键索引 | 所有 FK 字段建索引（Django 默认自动建） |
| 查询热点 | `WHERE` / `JOIN` 中频繁出现的列建索引 |
| 唯一约束 | 业务唯一性用 `UniqueConstraint` |
| 避免过度索引 | 写入频繁的表，索引不超过 5-6 个 |
| 联合索引 | 最左前缀原则，区分度高的列放左边 |

## Django 迁移检查清单

每次 `makemigrations` 后检查生成的 SQL：

```bash
python manage.py sqlmigrate <app_label> <migration_number>
```

检查要点：
1. 表名/字段名是否符合命名规范
2. 外键 `ON DELETE` 行为是否正确（PROTECT vs CASCADE vs SET_NULL）
3. 是否有意外删除列/表（Django 迁移安全但需人工确认）
4. `ALTER TABLE` 在大表上可能锁表（开发阶段忽略）

## 引擎

- 全部使用 **InnoDB**（支持事务、外键、行级锁）
- 不使用 MyISAM
