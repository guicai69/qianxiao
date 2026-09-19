<template>
  <!-- 球馆首屏：从底线望过去的球场。尺寸是真的（610 × 1340 单位＝厘米），
       白线自己画出来，往下滚镜头往前推。纯 CSS 3D + SVG，零依赖。 -->
  <div class="court-stage" aria-hidden="true">
    <div class="court-lamps"></div>

    <div class="court-world">
      <div class="court-floor">
        <div class="floor-glow"></div>

        <!-- 球网：从底线看过去，网就是横在场地中间的一条白带加一片网影。
             画在地板平面内，不做反向旋转——那样会被画家算法排到地板后面 -->
        <div class="court-net">
          <span class="net-tape"></span>
          <span class="net-mesh"></span>
        </div>

        <svg class="court-lines" viewBox="0 0 610 1340" preserveAspectRatio="none">
          <g fill="none" stroke="rgba(248, 252, 246, 0.66)" stroke-width="3.5" stroke-linecap="square">
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
  </div>
</template>

<script setup>
// 无脚本：动效全部交给 CSS（滚动驱动 / 描边自绘 / 减少动态效果兜底）。
// 组件保持零依赖，是为了答辩现场拔掉网络也照样跑。
</script>

<style scoped>
.court-stage {
  position: absolute;
  inset: 0;
  overflow: clip;
  perspective: 860px;
  perspective-origin: 50% 26%;
  background:
    radial-gradient(140% 80% at 50% 84%, rgba(232, 163, 61, 0.09), transparent 62%),
    linear-gradient(180deg, #0a0f0c 0%, #0d1411 42%, #0b100e 100%);
}

/* 顶灯：四盏打在场地上的暖光 */
.court-lamps {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(22% 30% at 26% 6%, rgba(255, 226, 178, 0.15), transparent 72%),
    radial-gradient(22% 30% at 74% 6%, rgba(255, 226, 178, 0.12), transparent 72%),
    radial-gradient(40% 22% at 50% 0%, rgba(255, 238, 205, 0.12), transparent 72%);
  filter: blur(6px);
}

/* 世界：整体缩放，绕着 X 轴放平，镜头沿球场纵深推进 */
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
  background: linear-gradient(180deg, #22402f 0%, #1a2f24 44%, #142219 100%);
  box-shadow: inset 0 0 120px rgba(0, 0, 0, 0.55);
}

.floor-glow {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(46% 26% at 50% 30%, rgba(255, 219, 158, 0.24), transparent 74%),
    radial-gradient(70% 30% at 50% 88%, rgba(232, 163, 61, 0.14), transparent 76%);
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
  opacity: 0.9;
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

/* 球网：从底线看过去，网就是横在场地中间的一条白带加一片网影。
   画在地板平面里，不做反向旋转——反向旋转会被画家算法排到地板后面去 */
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
  background: linear-gradient(180deg, rgba(252, 253, 250, 0.95), rgba(238, 244, 236, 0.42));
  box-shadow: 0 0 30px rgba(255, 236, 200, 0.5);
}

.net-mesh {
  position: absolute;
  top: 24px;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: repeating-linear-gradient(
    90deg,
    rgba(240, 246, 240, 0.34) 0 3px,
    transparent 3px 18px
  );
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.85), transparent);
}

/* 尽头：不搭 3D 墙（那样会变成一条横在脸上的黑板），
   只在球的尽头压一层暖光，读作球馆深处的灯 */
.court-farwall {
  display: none;
}

/* 压暗：把视线拉到中间，同时保证文字对比度 */
.court-veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(10, 15, 12, 0.86) 0%, rgba(10, 15, 12, 0.32) 38%, rgba(10, 15, 12, 0.72) 100%),
    radial-gradient(120% 80% at 50% 42%, transparent 52%, rgba(10, 15, 12, 0.66) 100%);
  pointer-events: none;
}

/* 滚动推进：只驱动 transform，且不支持滚动时间线时停在构图最好的一帧 */
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
  .court-stage { perspective: 620px; perspective-origin: 50% 22%; }
  .court-world { --s: 0.52; top: 62%; }
}

@media (max-width: 480px) {
  .court-world { --s: 0.4; }
}
</style>
