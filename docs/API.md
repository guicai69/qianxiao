# 羽毛球馆管理系统 API 接口文档

> 自动生成，共 104 个接口。在线可交互文档：后端启动后访问 /api/docs/（Swagger UI）；OpenAPI schema 见 docs/api-schema.yml。
>
> 「说明」列是 `应用_动作_方法` 的 operationId：`_list` 列表、`_create` 创建、`_retrieve` 详情、`_update` 更新、`_partial_update` 部分更新、`_destroy` 删除；其余为自定义动作（如 `cancel` 取消、`check_in` 签到、`recharge` 充值、`confirm_cash` 收款）。

## activities

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/activities/{id}/` | activities_destroy |
| GET | `/api/activities/` | activities_list |
| GET | `/api/activities/my/` | activities_my_retrieve |
| GET | `/api/activities/{id}/` | activities_retrieve |
| GET | `/api/activities/{id}/registrations/` | activities_registrations_retrieve |
| PATCH | `/api/activities/{id}/` | activities_partial_update |
| POST | `/api/activities/` | activities_create |
| POST | `/api/activities/{id}/cancel/` | activities_cancel_create |
| POST | `/api/activities/{id}/register/` | activities_register_create |
| PUT | `/api/activities/{id}/` | activities_update |

## announcements

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/announcements/{id}/` | announcements_destroy |
| GET | `/api/announcements/` | announcements_list |
| GET | `/api/announcements/{id}/` | announcements_retrieve |
| PATCH | `/api/announcements/{id}/` | announcements_partial_update |
| POST | `/api/announcements/` | announcements_create |
| POST | `/api/announcements/{id}/toggle_pin/` | announcements_toggle_pin_create |
| POST | `/api/announcements/{id}/toggle_publish/` | announcements_toggle_publish_create |
| PUT | `/api/announcements/{id}/` | announcements_update |

## auth

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/auth/captcha/` | auth_captcha_retrieve |
| POST | `/api/auth/change-password/` | auth_change_password_create |
| POST | `/api/auth/login/` | auth_login_create |
| POST | `/api/auth/register/` | auth_register_create |
| POST | `/api/auth/token/refresh/` | auth_token_refresh_create |

## bookings

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/bookings/{id}/` | bookings_destroy |
| GET | `/api/bookings/` | bookings_list |
| GET | `/api/bookings/export_csv/` | bookings_export_csv_retrieve |
| GET | `/api/bookings/my/` | bookings_my_retrieve |
| GET | `/api/bookings/{id}/` | bookings_retrieve |
| PATCH | `/api/bookings/{id}/` | bookings_partial_update |
| POST | `/api/bookings/` | bookings_create |
| POST | `/api/bookings/{id}/cancel/` | bookings_cancel_create |
| POST | `/api/bookings/{id}/check_in/` | bookings_check_in_create |
| PUT | `/api/bookings/{id}/` | bookings_update |

## coupons

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/coupons/{id}/` | coupons_destroy |
| GET | `/api/coupons/` | coupons_list |
| GET | `/api/coupons/my/` | coupons_my_retrieve |
| GET | `/api/coupons/{id}/` | coupons_retrieve |
| PATCH | `/api/coupons/{id}/` | coupons_partial_update |
| POST | `/api/coupons/` | coupons_create |
| POST | `/api/coupons/redeem/` | coupons_redeem_create |
| POST | `/api/coupons/{id}/claim/` | coupons_claim_create |
| PUT | `/api/coupons/{id}/` | coupons_update |

## courts

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/courts/{id}/` | courts_destroy |
| GET | `/api/courts/` | courts_list |
| GET | `/api/courts/{id}/` | courts_retrieve |
| PATCH | `/api/courts/{id}/` | courts_partial_update |
| POST | `/api/courts/` | courts_create |
| PUT | `/api/courts/{id}/` | courts_update |

## favorites

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/favorites/{id}/` | favorites_destroy |
| GET | `/api/favorites/` | favorites_list |
| GET | `/api/favorites/{id}/` | favorites_retrieve |
| PATCH | `/api/favorites/{id}/` | favorites_partial_update |
| POST | `/api/favorites/` | favorites_create |
| PUT | `/api/favorites/{id}/` | favorites_update |

## feedbacks

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/feedbacks/{id}/` | feedbacks_destroy |
| GET | `/api/feedbacks/` | feedbacks_list |
| GET | `/api/feedbacks/{id}/` | feedbacks_retrieve |
| PATCH | `/api/feedbacks/{id}/` | feedbacks_partial_update |
| POST | `/api/feedbacks/` | feedbacks_create |
| POST | `/api/feedbacks/{id}/process/` | feedbacks_process_create |
| PUT | `/api/feedbacks/{id}/` | feedbacks_update |

## payments

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/payments/` | payments_list |
| GET | `/api/payments/bonus_tiers/` | payments_bonus_tiers_retrieve |
| GET | `/api/payments/export_csv/` | payments_export_csv_retrieve |
| GET | `/api/payments/{id}/` | payments_retrieve |
| POST | `/api/payments/confirm_cash/` | payments_confirm_cash_create |
| POST | `/api/payments/pay/` | payments_pay_create |
| POST | `/api/payments/recharge/` | payments_recharge_create |

## reviews

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/reviews/{id}/` | reviews_destroy |
| GET | `/api/reviews/` | reviews_list |
| GET | `/api/reviews/{id}/` | reviews_retrieve |
| PATCH | `/api/reviews/{id}/` | reviews_partial_update |
| POST | `/api/reviews/` | reviews_create |
| POST | `/api/reviews/{id}/reply/` | reviews_reply_create |
| PUT | `/api/reviews/{id}/` | reviews_update |

## schema

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schema/` | schema_retrieve |

## stats

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats/court_usage/` | stats_court_usage_retrieve |
| GET | `/api/stats/overview/` | stats_overview_retrieve |
| GET | `/api/stats/popular_slots/` | stats_popular_slots_retrieve |
| GET | `/api/stats/revenue_trend/` | stats_revenue_trend_retrieve |

## time-slots

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/time-slots/{id}/` | time_slots_destroy |
| GET | `/api/time-slots/` | time_slots_list |
| GET | `/api/time-slots/{id}/` | time_slots_retrieve |
| PATCH | `/api/time-slots/{id}/` | time_slots_partial_update |
| POST | `/api/time-slots/` | time_slots_create |
| PUT | `/api/time-slots/{id}/` | time_slots_update |

## users

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/users/{id}/` | users_destroy |
| GET | `/api/users/` | users_list |
| GET | `/api/users/me/` | users_me_retrieve |
| GET | `/api/users/{id}/` | users_retrieve |
| PATCH | `/api/users/me/` | users_me_partial_update |
| PATCH | `/api/users/{id}/` | users_partial_update |
| POST | `/api/users/` | users_create |
| POST | `/api/users/{id}/blacklist/` | users_blacklist_create |
| POST | `/api/users/{id}/unblacklist/` | users_unblacklist_create |
| PUT | `/api/users/{id}/` | users_update |

## venues

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/venues/{id}/` | venues_destroy |
| GET | `/api/venues/` | venues_list |
| GET | `/api/venues/public/` | venues_public_retrieve |
| GET | `/api/venues/{id}/` | venues_retrieve |
| GET | `/api/venues/{id}/availability/` | venues_availability_retrieve |
| PATCH | `/api/venues/{id}/` | venues_partial_update |
| POST | `/api/venues/` | venues_create |
| PUT | `/api/venues/{id}/` | venues_update |
