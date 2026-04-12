'use client'

import { useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { useTranslationStream } from '@/hooks/useTranslationStream'
import AgentMdSection from './AgentMdSection'
import GapReportPanel from './GapReportPanel'
import ClarifyingQAPanel from './ClarifyingQAPanel'
import { Wand2, Download } from 'lucide-react'
import { exportMarkdown } from '@/lib/api'

const SECTION_LABELS: Record<string, string> = {
  purpose: 'Purpose',
  users: 'Users',
  capabilities: 'Capabilities',
  tools_integrations: 'Tools & Integrations',
  decision_authority: 'Decision Authority',
  constraints: 'Constraints',
  success_metrics: 'Success Metrics',
  communication_style: 'Communication Style',
  edge_cases: 'Edge Cases & Fallbacks',
}

export default function PrdTranslationLayout() {
  const { translationSession, translationMode } = useAppStore()
  const { clarifyGap, finalize, phase, clarifyingQuestions } = useTranslationStream()
  const [answeredIds, setAnsweredIds] = useState<Set<string>>(new Set())
  const [finalHtml, setFinalHtml] = useState<string | null>(null)

  if (!translationSession) return null

  const { prdText, agentSections, gaps, status } = translationSession

  const handleAnswer = async (questionId: string, answer: string) => {
    await clarifyGap(questionId, answer)
    setAnsweredIds((prev) => { const next = new Set(prev); next.add(questionId); return next })
  }

  const handleFinalize = () => {
    finalize((html) => setFinalHtml(html))
  }

  const handleDownload = async () => {
    const html = finalHtml ?? ''
    const blob = await exportMarkdown(html, 'agent.md')
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'agent.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  const phaseLabel: Record<string, string> = {
    extracting: 'Phase 1/4 — Extracting PRD structure…',
    generating: 'Phase 2/4 — Generating agent.md sections…',
    gap_analysis: 'Phase 3/4 — Analyzing gaps…',
    clarifying: 'Phase 4/4 — Clarifying gaps',
    finalizing: 'Finalizing agent.md with frontier model…',
  }

  const currentPhaseLabel = phaseLabel[phase] ?? ''

  return (
    <div className="flex w-full h-full overflow-hidden bg-zinc-950">
      {/* Left: original PRD */}
      <div className="flex w-1/2 flex-col border-r border-zinc-800 overflow-hidden">
        <div className="shrink-0 border-b border-zinc-800 px-5 py-3 flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-widest text-zinc-500">Original PRD</span>
        </div>
        <div className="flex-1 overflow-y-auto px-5 py-4">
          <pre className="text-xs text-zinc-400 whitespace-pre-wrap leading-relaxed font-mono">
            {prdText}
          </pre>
        </div>
      </div>

      {/* Right: agent.md output */}
      <div className="flex w-1/2 flex-col overflow-hidden">
        {/* Toolbar */}
        <div className="shrink-0 border-b border-zinc-800 px-5 py-3 flex items-center justify-between gap-2">
          <div>
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-500">agent.md</span>
            {currentPhaseLabel && (
              <span className="ml-3 text-xs text-blue-400">{currentPhaseLabel}</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {status === 'clarifying' && answeredIds.size > 0 && (
              <button
                onClick={handleFinalize}
                disabled={phase === 'finalizing'}
                className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-500 disabled:opacity-40 transition-colors"
              >
                <Wand2 className="h-3.5 w-3.5" />
                Finalize
              </button>
            )}
            {finalHtml && (
              <button
                onClick={handleDownload}
                className="flex items-center gap-1.5 rounded-lg border border-zinc-700 px-3 py-1.5 text-xs text-zinc-400 hover:border-zinc-600 hover:text-zinc-200 transition-colors"
              >
                <Download className="h-3.5 w-3.5" />
                Download .md
              </button>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {/* Sections */}
          {agentSections.length > 0 && (
            <div>
              {agentSections.map((section) => (
                <AgentMdSection
                  key={section.section_key}
                  section={section}
                  label={SECTION_LABELS[section.section_key] ?? section.section_key}
                />
              ))}
            </div>
          )}

          {/* Gap report */}
          {gaps.length > 0 && <GapReportPanel gaps={gaps} />}

          {/* Clarifying Q&A */}
          {clarifyingQuestions.length > 0 && (
            <ClarifyingQAPanel
              questions={clarifyingQuestions}
              answeredIds={answeredIds}
              onAnswer={handleAnswer}
            />
          )}

          {/* Empty state */}
          {agentSections.length === 0 && phase !== 'idle' && (
            <div className="flex items-center gap-2 text-sm text-zinc-500 py-8">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-600 border-t-zinc-300" />
              Processing your PRD…
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
