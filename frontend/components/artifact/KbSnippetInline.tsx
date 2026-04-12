'use client'

import { BookOpen, X } from 'lucide-react'
import { useState } from 'react'

interface KbSnippetInlineProps {
  snippet: string
}

export default function KbSnippetInline({ snippet }: KbSnippetInlineProps) {
  const [dismissed, setDismissed] = useState(false)
  if (dismissed || !snippet) return null

  return (
    <div className="mx-6 mb-3 flex gap-2 rounded-lg border border-blue-500/20 bg-blue-500/5 p-3 text-sm">
      <BookOpen className="mt-0.5 h-4 w-4 shrink-0 text-blue-400" />
      <p className="flex-1 text-zinc-300 leading-relaxed italic">{snippet}</p>
      <button
        onClick={() => setDismissed(true)}
        className="shrink-0 text-zinc-500 hover:text-zinc-300"
        aria-label="Dismiss"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  )
}
