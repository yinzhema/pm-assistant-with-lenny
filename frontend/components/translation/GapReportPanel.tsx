'use client'

import { AlertTriangle, AlertCircle, Info } from 'lucide-react'
import type { GapItem } from '@/types'

const SEVERITY_ICON = {
  high:   <AlertTriangle className="h-3.5 w-3.5 text-red-400" />,
  medium: <AlertCircle className="h-3.5 w-3.5 text-yellow-400" />,
  low:    <Info className="h-3.5 w-3.5 text-zinc-500" />,
}

const CATEGORY_LABELS: Record<string, string> = {
  implicit_judgment:   'Implicit Human Judgment',
  missing_escalation:  'Missing Escalation Logic',
  ambiguous_scope:     'Ambiguous Scope',
  missing_constraints: 'Missing Constraints',
  metric_ambiguity:    'Metric Ambiguity',
  tool_permissions:    'Tool Permissions',
}

interface GapReportPanelProps {
  gaps: GapItem[]
}

export default function GapReportPanel({ gaps }: GapReportPanelProps) {
  if (gaps.length === 0) return null

  const grouped = gaps.reduce<Record<string, GapItem[]>>((acc, g) => {
    const cat = g.gap_category ?? 'other'
    ;(acc[cat] = acc[cat] ?? []).push(g)
    return acc
  }, {})

  return (
    <div className="rounded-lg border border-yellow-500/20 bg-yellow-500/5 p-4">
      <p className="text-xs font-semibold uppercase tracking-widest text-yellow-400 mb-3">
        Gap Report — {gaps.length} item{gaps.length !== 1 ? 's' : ''} found
      </p>
      <div className="space-y-3">
        {Object.entries(grouped).map(([cat, items]) => (
          <div key={cat}>
            <p className="text-xs font-medium text-zinc-400 mb-1">
              {CATEGORY_LABELS[cat] ?? cat}
            </p>
            {items.map((gap) => (
              <div key={gap.id} className="flex items-start gap-2 text-sm text-zinc-400 mb-1">
                <span className="mt-0.5">{SEVERITY_ICON[gap.severity]}</span>
                <span className="leading-snug">{gap.description}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
