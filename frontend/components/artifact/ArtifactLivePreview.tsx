'use client'

import type { ArtifactSession, ArtifactSectionPreview } from '@/types'
import ArtifactSection from './ArtifactSection'

interface ArtifactLivePreviewProps {
  session: ArtifactSession
  previews: Record<string, ArtifactSectionPreview>
  onSectionClick: (questionId: string) => void
}

export default function ArtifactLivePreview({
  session,
  previews,
  onSectionClick,
}: ArtifactLivePreviewProps) {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="shrink-0 border-b border-zinc-800 px-6 py-4">
        <h2 className="text-sm font-semibold text-zinc-200">Live Preview</h2>
        <p className="text-xs text-zinc-500 mt-0.5">Updates as you answer each question</p>
      </div>

      {/* Sections */}
      <div className="flex-1 overflow-y-auto px-6 py-5 space-y-1">
        {session.questions.map((q) => {
          const preview = previews[q.section_key]
          if (!preview) return null
          return (
            <ArtifactSection
              key={q.id}
              section={preview}
              onClick={() => onSectionClick(q.id)}
            />
          )
        })}
      </div>
    </div>
  )
}
