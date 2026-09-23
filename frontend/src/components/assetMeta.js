export const ASSET_TYPE_META = {
  extinguisher: { label: 'Fire Extinguisher', emoji: '🧯' },
  hose_cabinet: { label: 'Hose Cabinet', emoji: '🚒' },
  hose_reel: { label: 'Hose Reel', emoji: '🌀' },
  branch: { label: 'Branch/Nozzle', emoji: '🔫' },
  mcp: { label: 'Manual Call Point', emoji: '📟' },
}

export function assetTypeLabel(type) {
  return ASSET_TYPE_META[type]?.label || type
}

export function assetTypeEmoji(type) {
  return ASSET_TYPE_META[type]?.emoji || '🔹'
}
