"""纯 Python 图形验证码：4 位数字 SVG，零第三方依赖。

- 答案存 Django 默认缓存（未配置 Redis 时自动用 LocMemCache，单进程够用）
- 一次性：校验通过即删除
- DJANGO_CAPTCHA_REQUIRED=0 时注册/登录不再要求验证码（本地开发兼容）
"""
import os
import random
import string

from django.core.cache import cache

CAPTCHA_TTL = 5 * 60
CAPTCHA_REQUIRED = os.environ.get('DJANGO_CAPTCHA_REQUIRED', '1') == '1'


def _key(captcha_id):
    return f'captcha:{captcha_id}'


def generate():
    """返回 (captcha_id, code, svg)。SVG 带干扰线，前端 v-html 渲染。"""
    code = ''.join(random.choices(string.digits, k=4))
    captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
    cache.set(_key(captcha_id), code, CAPTCHA_TTL)
    svg = _render_svg(code)
    return captcha_id, code, svg


def verify(captcha_id, code):
    """校验并删除（一次性）。未启用验证码时恒真。"""
    if not CAPTCHA_REQUIRED:
        return True
    if not captcha_id or not code:
        return False
    saved = cache.get(_key(captcha_id))
    if saved is None:
        return False
    cache.delete(_key(captcha_id))
    return str(saved) == str(code)


def _render_svg(code):
    # ponytail: 固定模板+随机偏移的干扰线，够挡住脚本即可，不做字体库
    def noise_lines():
        parts = []
        for _ in range(4):
            x1, y1 = random.randint(0, 120), random.randint(0, 36)
            x2, y2 = random.randint(0, 120), random.randint(0, 36)
            parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="rgba(26,95,208,.35)" stroke-width="1"/>'
            )
        return ''.join(parts)

    chars = []
    for i, ch in enumerate(code):
        x = 10 + i * 30
        y = 28
        rot = random.randint(-8, 8)
        chars.append(
            f'<text x="{x}" y="{y}" font-size="22" font-family="monospace" '
            f'fill="#1a5fd0" transform="rotate({rot} {x} {y})">{ch}</text>'
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="36" '
        'viewBox="0 0 120 36">'
        '<rect width="120" height="36" rx="6" fill="#eef2f8"/>'
        + noise_lines()
        + ''.join(chars)
        + '</svg>'
    )
