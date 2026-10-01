"""统一异常处理：所有 DRF 异常响应规范为 {code, message, fields?}。

- fields：字段级校验错误（原 {字段: [错误...]} 保留在里面，前端需要时仍可取）
- message：可直接展示的一句话（字段错误取第一条拼接；无字段错误取 detail）
- 视图里手动 return 的 {'detail': ...} 属正常响应不经此处理器，前端拦截器两种形态都兼容
"""
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    data = response.data if isinstance(response.data, dict) else {'detail': str(response.data)}
    detail = data.get('detail')
    fields = {k: v for k, v in data.items() if k != 'detail'}

    if fields:
        first = next(iter(fields.values()))
        message = str(first[0] if isinstance(first, list) else first)
    elif detail is not None:
        message = str(detail)
    else:
        message = str(data)

    response.data = {'code': response.status_code, 'message': message}
    if fields:
        response.data['fields'] = fields
    return response
