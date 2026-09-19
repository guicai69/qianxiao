<template>
  <!-- 首屏：蓝图上的球场。尺寸是真的（610 × 1340 单位＝厘米），
       白线自己画出来，往下滚镜头往前推。纯 CSS 3D + SVG，零依赖。 -->
  <div class="court-stage" aria-hidden="true">
    <div class="grid-paper"></div>
    <div class="lamps"></div>

    <div class="court-world">
      <div class="court-floor">
        <div class="floor-glow"></div>

        <!-- 球网：从底线看过去，网就是横在场地中间的一条白带加一片网影。
             画在地板平面里，不做反向旋转——反向旋转会被画家算法排到地板后面 -->
        <div class="court-net">
          <span class="net-tape"></span>
          <span class="net-mesh"></span>
        </div>

        <svg class="court-lines" viewBox="0 0 610 1340" preserveAspectRatio="none">
          <g fill="none" stroke="rgba(26, 95, 208, 0.72)" stroke-width="3.5" stroke-linecap="square">
            <rect class="ln" style="--i: 0" pathLength="1" x="2" y="2" width="606" height="1336" />
            <line class="ln" style="--i: 1" pathLength="1" x1="2" y1="670" x2="608" y2="670" />
            <line class="ln" style="--i: 2" pathLength="1" x1="305" y1="2" x2="305" y2="1338" />
            <line class="ln" style="--i: 3" pathLength="1" x1="2" y1="472" x2="608" y2="472" />
            <line class="ln" style="--i: 4" pathLength="1" x1="2" y1="868" x2="608" y2="868" />
            <line class="ln" style="--i: 5" pathLength="1" x1="2" y1="76" x2="608" y2="76" />
            <line class="ln" style="--i: 6" pathLength="1" x1="2" y1="1264" x2="608" y2="1264" />
            <line class="ln" style="--i: 7" pathLength="1" x1="46" y1="2" x2="46" y2="1338" />
            <line class="ln" style="--i: 8" pathLength="1" x1="564" y1="2" x2="564" y2="1338" />
          </g>
        </svg>
      </div>
    </div>

    <div class="court-veil"></div>
    <!-- 鼠标跟随的冷光：只在精确指针设备 + 不要求减少动效时才出现 -->
    <div ref="lightRef" class="cursor-light"></div>
  </div>
</template>

<script setup>
// 几乎无脚本：镜头推进与描边自绘全交给 CSS，这里只做一件 CSS 做不到的事——
// 鼠标跟随的冷光。两个开关都关着（触屏 / 要求减少动效）时一句都不执行。
import { onBeforeUnmount, onMounted, ref } from 'vue'

const lightRef = ref(null)
let detach = null

onMounted(() => {
  const FINE = matchMedia('(hover: hover) and (pointer: fine)').matches
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches
  const stage = lightRef.value?.parentElement
  if (!FINE || RM || !stage) return

  const host = stage.parentElement || stage
  let raf = 0
  const onMove = (e) => {
    if (raf) return
    raf = requestAnimationFrame(() => {
      raf = 0
      const r = stage.getBoundingClientRect()
      stage.style.setProperty('--mx', `${e.clientX - r.left}px`)
      stage.style.setProperty('--my', `${e.clientY - r.top}px`)
    })
  }
  host.addEventListener('pointermove', onMove, { passive: true })
  detach = () => {
    host.removeEventListener('pointermove', onMove)
    if (raf) cancelAnimationFrame(raf)
  }
})

onBeforeUnmount(() => detach?.())
</script>

<style scoped>
.court-stage {
  position: absolute;
  inset: 0;
  overflow: clip;
  perspective: 900px;
  perspective-origin: 50% 26%;
  background:
    radial-gradient(120% 70% at 50% 92%, rgba(26, 95, 208, 0.1), transparent 62%),
    linear-gradient(180deg, #f5f9ff 0%, #eaf1fb 52%, #e4ecf8 100%);
}

/* 蓝图格纸：整站隐喻的底纹，画在球场底下 */
.grid-paper {
  position: absolute;
  inset: 0;
  opacity: 0.9;
  background-image:
    repeating-linear-gradient(90deg, var(--blueprint-line) 0 1px, transparent 1px 30px),
    repeating-linear-gradient(0deg, var(--blueprint-line) 0 1px, transparent 1px 30px);
  mask-image: radial-gradient(120% 90% at 50% 40%, #000 30%, transparent 78%);
}

/* 顶灯：冷白高光 */
.lamps {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(24% 26% at 24% 4%, rgba(255, 255, 255, 0.85), transparent 72%),
    radial-gradient(24% 26% at 76% 4%, rgba(255, 255, 255, 0.7), transparent 72%),
    radial-gradient(44% 20% at 50% 0%, rgba(214, 232, 255, 0.75), transparent 74%);
  filter: blur(7px);
}

/* 世界：整体缩放，绕 X 轴放平，镜头沿球场纵深推进 */
.court-world {
  --s: 1;
  --z: -60px;
  position: absolute;
  left: 57%;
  top: 72%;
  width: 610px;
  height: 1340px;
  transform-style: preserve-3d;
  transform: translate(-50%, -50%) scale(var(--s)) rotateX(72deg) translateZ(var(--z));
}

.court-floor {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, var(--court-mat-a) 0%, var(--court-mat-b) 100%);
  box-shadow:
    inset 0 0 90px rgba(26, 95, 208, 0.16),
    0 0 0 1px rgba(26, 95, 208, 0.18);
}

.floor-glow {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(46% 26% at 50% 28%, rgba(255, 255, 255, 0.8), transparent 74%),
    radial-gradient(70% 30% at 50% 90%, rgba(26, 95, 208, 0.08), transparent 76%);
}

.court-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* 白线自绘：作者状态就是画完的状态，动画从"没画"进来 */
.ln {
  stroke-dasharray: 1;
}

@media (prefers-reduced-motion: no-preference) {
  .ln {
    animation: draw 900ms var(--ease-out) both;
    animation-delay: calc(var(--i) * 80ms);
  }
}

@keyframes draw {
  from { stroke-dashoffset: 1; }
  to { stroke-dashoffset: 0; }
}

/* 球网：从底线看过去就是一条白带加一片网影，画在地板平面里 */
.court-net {
  position: absolute;
  left: 0;
  right: 0;
  top: 636px;
  height: 92px;
}

.net-tape {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 24px;
  background: linear-gradient(180deg, #ffffff, rgba(255, 255, 255, 0.55));
  box-shadow: 0 0 26px rgba(26, 95, 208, 0.35);
}

.net-mesh {
  position: absolute;
  top: 24px;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: repeating-linear-gradient(
    90deg,
    rgba(26, 95, 208, 0.34) 0 3px,
    transparent 3px 18px
  );
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.9), transparent);
}

/* 压一下四周：把视线拉到球场，同时保证左侧文字背景够干净 */
.court-veil {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(100deg, rgba(245, 249, 255, 0.94) 0%, rgba(245, 249, 255, 0.55) 34%, rgba(245, 249, 255, 0) 62%),
    radial-gradient(130% 90% at 50% 45%, transparent 52%, rgba(228, 236, 248, 0.72) 100%);
}

/* 滚动推进：只驱动 transform；不支持滚动时间线时停在构图最好的一帧 */
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: scroll()) {
    .court-world {
      animation: dolly linear both;
      animation-timeline: scroll(root block);
      animation-range: 0 90vh;
    }
  }
}

@keyframes dolly {
  from { transform: translate(-50%, -50%) scale(var(--s)) rotateX(72deg) translateZ(-300px); }
  to { transform: translate(-50%, -50%) scale(var(--s)) rotateX(72deg) translateZ(340px); }
}

@media (max-width: 1100px) {
  .court-world { --s: 0.78; top: 66%; }
}

@media (max-width: 760px) {
  .court-stage { perspective: 640px; perspective-origin: 50% 22%; }
  .court-world { --s: 0.52; top: 62%; }
}

@media (max-width: 480px) {
  .court-world { --s: 0.4; }
}
</style>
