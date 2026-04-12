'use client'

import type { ArtifactSectionPreview } from '@/types'

interface ArtifactSectionProps {
  section: ArtifactSectionPreview
  onClick?: () => void
}

export default function ArtifactSection({ section, onClick }: ArtifactSectionProps) {
  const isEmpty = !section.isAnswered && !section.isSkipped && !section.isStreaming

  let borderClass = 'border-zinc-700/50'
  if (section.isAnswered) borderClass = 'border-l-2 border-l-green-500/60 border-r-0 border-t-0 border-b-0 rounded-none pl-3'
  if (section.isSkipped) borderClass = 'border-l-2 border-l-zinc-600 border-r-0 border-t-0 border-b-0 rounded-none pl-3 opacity-50'
  if (section.isStreaming) borderClass = 'border-l-2 border-l-blue-500 border-r-0 border-t-0 border-b-0 rounded-none pl-3 animate-pulse'

  return (
    <div
      className={`group border ${borderClass} mb-4 cursor-pointer`}
      onClick={onClick}
      title={onClick ? `Click to jump back to this question` : undefined}
    >
      <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500 mb-1 group-hover:text-zinc-400 transition-colors">
        {section.sectionLabel}
        {section.isSkipped && <span className="ml-2 normal-case tracking-normal font-normal text-zinc-600">— skipped</span>}
      </p>

      {isEmpty ? (
        <p className="text-sm text-zinc-600 italic leading-relaxed">{section.placeholder}</p>
      ) : section.isStreaming || section.isAnswered ? (
        <div
          className="prose prose-sm prose-invert max-w-none text-zinc-300 [&_p]:my-1 [&_ul]:my-1 [&_li]:my-0.5"
          dangerouslySetInnerHTML={{ __html: section.html || section.placeholder }}
        />
      ) : (
        <p className="text-sm text-zinc-600 italic leading-relaxed">{section.placeholder}</p>
      )}
    </div>
  )
}
