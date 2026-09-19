<template>
  <!-- 登录 / 注册共用的外壳：左边球馆照片，右边纸面表单 -->
  <div class="auth-shell">
    <section class="auth-visual" data-plane="deep">
      <img
        class="auth-photo"
        src="/img/auth-visual.jpg"
        alt="室内羽毛球场上的挥拍瞬间"
        @error="hideBrokenImage"
      />
      <span class="auth-scrim"></span>

      <div class="auth-visual-inner">
        <div class="visual-top">
          <RouterLink to="/" class="visual-brand">
            <span class="visual-mark">
              <svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true">
                <rect x="4.2" y="3" width="15.6" height="18" rx="1.4" fill="none" stroke="currentColor" stroke-width="1.5" />
                <path d="M4.2 12h15.6" stroke="currentColor" stroke-width="1.5" />
                <path d="M12 3v18" stroke="currentColor" stroke-width="1" opacity=".45" />
              </svg>
            </span>
            <span>羽毛球馆预约</span>
          </RouterLink>
        </div>

        <div class="visual-bottom">
          <h2 class="display-2 visual-title">
            场馆、场地、时段，<br />一处看清。
          </h2>
          <p class="lede visual-lede">
            会员折扣在下单前就写进小票，到店前台签到即核销。广州五座球馆、24 片场地同一个入口。
          </p>
        </div>
      </div>
    </section>

    <section class="auth-panel">
      <div class="auth-card">
        <RouterLink to="/" class="back-home">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </RouterLink>
        <slot />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ArrowLeft } from '@element-plus/icons-vue'
import { hideBrokenImage } from '@/utils/venueVisual'
</script>

<style scoped>
.auth-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(400px, 520px);
  min-height: 100dvh;
  background: var(--page);
}

/* ---------- 左：球馆 ---------- */

.auth-visual {
  position: relative;
  isolation: isolate;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100dvh;
  padding: 36px 44px 52px;
  overflow: clip;
  background:
    radial-gradient(80% 60% at 50% 20%, rgba(91, 157, 255, 0.18), transparent 70%),
    linear-gradient(180deg, #101a2e 0%, #0b1220 100%);
}

.auth-photo {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.8) contrast(1.06) brightness(0.86);
}

.auth-scrim {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(9, 14, 26, 0.82) 0%, rgba(9, 14, 26, 0.3) 42%, rgba(9, 14, 26, 0.94) 100%),
    radial-gradient(110% 70% at 30% 80%, rgba(9, 14, 26, 0.5), transparent 70%);
}

.auth-visual-inner {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  min-height: 100%;
  gap: 40px;
}

.visual-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: var(--fs-14);
  font-weight: 700;
  color: rgba(240, 244, 236, 0.92);
}

.visual-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  color: var(--accent);
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(11, 18, 32, 0.5);
}

.visual-title {
  color: #f4f7f0;
  text-shadow: 0 2px 28px rgba(0, 0, 0, 0.5);
  max-width: 22ch;
}

.visual-lede {
  margin-top: 18px;
  color: rgba(238, 241, 233, 0.74);
  max-width: 42ch;
}

/* ---------- 右：表单 ---------- */

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
  background: var(--page);
  border-left: 1px solid var(--border);
}

.auth-card {
  width: 100%;
  max-width: 380px;
}

.back-home {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 30px;
  font-size: var(--fs-13);
  font-weight: 600;
  color: var(--ink-3);
  transition: color var(--dur-2) var(--ease-out);
}

.back-home:hover {
  color: var(--accent);
}

/* ---------- 断点 ---------- */

@media (max-width: 980px) {
  .auth-shell {
    grid-template-columns: minmax(0, 1fr);
  }

  .auth-visual {
    min-height: 0;
    padding: 26px 24px 30px;
  }

  .auth-visual-inner {
    gap: 26px;
  }

  .visual-title {
    max-width: none;
    font-size: clamp(22px, 6vw, 30px);
  }

  .visual-lede {
    display: none;
  }

  .auth-panel {
    padding: 32px 22px 44px;
    border-left: 0;
    border-top: 1px solid var(--border);
  }

  .auth-card {
    max-width: none;
  }
}
</style>
