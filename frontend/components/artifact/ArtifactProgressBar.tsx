'use client'

interface ArtifactProgressBarProps {
  current: number  // 0-based index
  total: number
  title: string
}

export default function ArtifactProgressBar({ current, total, title }: ArtifactProgressBarProps) {
  const step = current + 1
  const pct = Math.round((current / Math.max(total - 1, 1)) * 100)

  return (
    <div className="px-6 pt-5 pb-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-zinc-500 uppercase tracking-wide">{title}</span>
        <span className="text-xs text-zinc-400">
          {step} / {total}
        </span>
      </div>
      <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
