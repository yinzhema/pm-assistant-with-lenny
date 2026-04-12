'use client'

import { useState } from 'react'
import { HelpCircle, SkipForward, Send } from 'lucide-react'
import type { Question } from '@/types'
import KbSnippetInline from './KbSnippetInline'

interface QuestionCardProps {
  question: Question
  kbSnippet: string | null
  onSubmit: (answer: string) => void
  onSkip: () => void
  isStreaming: boolean
}

export default function QuestionCard({
  question,
  kbSnippet,
  onSubmit,
  onSkip,
  isStreaming,
}: QuestionCardProps) {
  const [answer, setAnswer] = useState('')
  const [showTooltip, setShowTooltip] = useState(false)

  const handleSubmit = () => {
    if (!answer.trim() || isStreaming) return
    onSubmit(answer.trim())
    setAnswer('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex flex-col gap-3 px-6 py-4">
      {/* Question text + tooltip */}
      <div className="flex items-start gap-2">
        <p className="flex-1 text-base font-medium text-zinc-100 leading-snug">
          {question.text}
        </p>
        <div className="relative">
          <button
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            className="mt-0.5 text-zinc-500 hover:text-zinc-300 transition-colors"
            aria-label="Why this matters"
          >
            <HelpCircle className="h-4 w-4" />
          </button>
          {showTooltip && (
            <div className="absolute right-0 top-6 z-20 w-72 rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-xs text-zinc-300 shadow-xl leading-relaxed">
              <p className="font-semibold text-zinc-200 mb-1">Why this matters</p>
              {question.why_it_matters}
            </div>
          )}
        </div>
      </div>

      {/* KB Snippet */}
      {kbSnippet && <KbSnippetInline snippet={kbSnippet} />}

      {/* Answer textarea */}
      <textarea
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={question.placeholder}
        disabled={isStreaming}
        rows={4}
        className="w-full resize-none rounded-lg border border-zinc-700 bg-zinc-800/60 px-3 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 transition-colors"
      />

      {/* Actions */}
      <div className="flex items-center justify-between gap-2">
        {question.allow_skip && (
          <button
            onClick={onSkip}
            disabled={isStreaming}
            className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 disabled:opacity-40 transition-colors"
          >
            <SkipForward className="h-3.5 w-3.5" />
            I don't know yet
          </button>
        )}
        <button
          onClick={handleSubmit}
          disabled={!answer.trim() || isStreaming}
          className="ml-auto flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <Send className="h-3.5 w-3.5" />
          {isStreaming ? 'Generating…' : 'Submit'}
        </button>
      </div>
      <p className="text-xs text-zinc-600">⌘ + Enter to submit</p>
    </div>
  )
}
