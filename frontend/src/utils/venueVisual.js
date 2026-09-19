// 场馆 → 印相表格子上的编号与封面
// 编号跟着区走，保证列表顺序变化时 01–05 不会乱跳。

// 封面用球场图纸（1200x800 SVG，同一族、等尺寸、不含人物）。
// 想换成实拍照片：把文件丢进 frontend/public/img/ 再改这里即可。
const DISTRICTS = [
  { key: '天河', file: '/img/court-01.svg' },
  { key: '海珠', file: '/img/court-02.svg' },
  { key: '白云', file: '/img/court-03.svg' },
  { key: '番禺', file: '/img/court-04.svg' },
  { key: '越秀', file: '/img/court-05.svg' },
]

const FALLBACK_COVERS = DISTRICTS.map((d) => d.file)

function districtIndex(venue) {
  const name = venue?.name || ''
  const i = DISTRICTS.findIndex((d) => name.includes(d.key))
  return i
}

/** 按区的固定顺序排列场馆，返回带上编号与封面的新数组 */
export function asContactSheet(venues = []) {
  const sorted = [...venues].sort((a, b) => {
    const ia = districtIndex(a)
    const ib = districtIndex(b)
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib)
  })
  return sorted.map((v, i) => {
    const di = districtIndex(v)
    return { ...v, no: String(i + 1).padStart(2, '0') }
  })
}

/** 场馆封面：按区取图，取不到就用兜底的一张 */
export function coverUrl(venue) {
  const i = districtIndex(venue)
  if (i >= 0) return DISTRICTS[i].file
  const n = Number(venue?.id) || 0
  return FALLBACK_COVERS[n % FALLBACK_COVERS.length]
}

/** 区名（用于格子上的一行小字） */
export function districtOf(venue) {
  const di = districtIndex(venue)
  return di >= 0 ? DISTRICTS[di].key : '广州'
}

/** 图片挂了就藏掉，露出底下的场地漆渐变，不要露出破图标 */
export function hideBrokenImage(e) {
  e.target.style.display = 'none'
}
