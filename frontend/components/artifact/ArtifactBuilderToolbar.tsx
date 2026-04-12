'use client'

import { Wand2, X } from 'lucide-react'

interface ArtifactBuilderToolbarProps {
  title: string
  allAnswered: boolean
  isSynthesizing: boolean
  onSynthesize: () => void
  onClose: () => void
}

export default function ArtifactBuilderToolbar({
  title,
  allAnswered,
  isSynthesizing,
  onSynthesize,
  onClose,
}: ArtifactBuilderToolbarProps) {
  return (
    <div className="flex h-12 shrink-0 items-center justify-between border-b border-zinc-800 px-4">
      <span className="text-sm font-semibold text-zinc-200 truncate">{title}</span>
      <div className="flex items-center gap-2">
        {allAnswered && !isSynthesizing && (
          <button
            onClick={onSynthesize}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-500 transition-colors"
          >
            <Wand2 className="h-3.5 w-3.5" />
            Synthesize &amp; Finish
          </button>
        )}
        {isSynthesizing && (
          <span className="flex items-center gap-1.5 text-xs text-blue-400">
            <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-blue-400 border-t-transparent" />
            Synthesizing with frontier model…
          </span>
        )}
        <button
          onClick={onClose}
          className="rounded p-1 text-zinc-500 hover:text-zinc-300 transition-colors"
          aria-label="Close builder"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
