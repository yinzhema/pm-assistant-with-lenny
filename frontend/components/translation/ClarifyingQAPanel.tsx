'use client'

import { useState } from 'react'
import { Send, CheckCircle2 } from 'lucide-react'
import type { GapItem } from '@/types'

interface ClarifyingQAPanelProps {
  questions: GapItem[]
  answeredIds: Set<string>
  onAnswer: (questionId: string, answer: string) => void
}

export default function ClarifyingQAPanel({
  questions,
  answeredIds,
  onAnswer,
}: ClarifyingQAPanelProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const unanswered = questions.filter((q) => !answeredIds.has(q.id))
  if (unanswered.length === 0) return null

  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
        Clarifying Questions ({unanswered.length} remaining)
      </p>
      {questions.map((gap) => {
        const done = answeredIds.has(gap.id)
        return (
          <div
            key={gap.id}
            className={`rounded-lg border p-3 transition-colors ${
              done
                ? 'border-green-500/20 bg-green-500/5 opacity-60'
                : 'border-zinc-700 bg-zinc-800/40'
            }`}
          >
            <div className="flex items-start gap-2 mb-2">
              {done ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-400" />
              ) : (
                <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${
                  gap.severity === 'high' ? 'bg-red-400' :
                  gap.severity === 'medium' ? 'bg-yellow-400' : 'bg-zinc-500'
                }`} />
              )}
              <p className="text-sm text-zinc-200 leading-snug">{gap.question}</p>
            </div>
            {!done && (
              <div className="flex gap-2">
                <textarea
                  value={answers[gap.id] ?? ''}
                  onChange={(e) => setAnswers((prev) => ({ ...prev, [gap.id]: e.target.value }))}
                  rows={2}
                  placeholder="Your answer…"
                  className="flex-1 resize-none rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  onClick={() => {
                    const ans = answers[gap.id]?.trim()
                    if (!ans) return
                    onAnswer(gap.id, ans)
                  }}
                  disabled={!answers[gap.id]?.trim()}
                  className="self-end rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
