// CSV 导出共用：带 token 拉 blob（绕过返回体拦截器），再触发下载。
import axios from 'axios'
import { useUserStore } from '@/store'

export async function fetchCsv(url, params) {
  const userStore = useUserStore()
  const res = await axios.get(url, {
    params,
    headers: { Authorization: `Bearer ${userStore.token}` },
    responseType: 'blob',
  })
  return res.data
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
