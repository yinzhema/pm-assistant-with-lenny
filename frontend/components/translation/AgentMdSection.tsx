'use client'

import type { AgentMdSection as AgentMdSectionType } from '@/types'

const CONFIDENCE_STYLES = {
  green:  { border: 'border-l-green-500/60',  badge: 'bg-green-500/10 text-green-400',  label: 'Derived' },
  yellow: { border: 'border-l-yellow-500/60', badge: 'bg-yellow-500/10 text-yellow-400', label: 'Inferred — review' },
  red:    { border: 'border-l-red-500/60',    badge: 'bg-red-500/10 text-red-400',       label: 'Missing' },
}

interface AgentMdSectionProps {
  section: AgentMdSectionType
  label: string
}

export default function AgentMdSection({ section, label }: AgentMdSectionProps) {
  const style = CONFIDENCE_STYLES[section.confidence] ?? CONFIDENCE_STYLES.yellow

  return (
    <div className={`border-l-2 pl-3 mb-4 ${style.border}`}>
      <div className="flex items-center gap-2 mb-1">
        <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
          {label}
        </span>
        <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${style.badge}`}>
          {style.label}
        </span>
      </div>
      <div
        className="prose prose-sm prose-invert max-w-none text-zinc-300 [&_p]:my-1 [&_ul]:my-1 [&_li]:my-0.5"
        dangerouslySetInnerHTML={{ __html: section.html || '<p class="text-zinc-600 italic">Not yet generated</p>' }}
      />
    </div>
  )
}
