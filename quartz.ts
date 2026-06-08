import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"
import { Explorer } from "./.quartz/plugins"

Explorer({
  sortFn: (a, b) => {
    const folderOrder = ["projects", "writing", "other"]
    if (a.isFolder && b.isFolder) {
      const aIdx = folderOrder.indexOf(a.slugSegment ?? "")
      const bIdx = folderOrder.indexOf(b.slugSegment ?? "")
      if (aIdx !== -1 && bIdx !== -1) return aIdx - bIdx
      if (aIdx !== -1) return -1
      if (bIdx !== -1) return 1
      return (a.displayName ?? "").localeCompare(b.displayName ?? "", undefined, {
        numeric: true,
        sensitivity: "base",
      })
    }
    if (!a.isFolder && !b.isFolder) {
      return (a.displayName ?? "").localeCompare(b.displayName ?? "", undefined, {
        numeric: true,
        sensitivity: "base",
      })
    }
    return a.isFolder ? -1 : 1
  },
})

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
