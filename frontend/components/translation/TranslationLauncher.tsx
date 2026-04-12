'use client'

import { useState } from 'react'
import { X, Bot, FileCode2 } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import { useTranslationStream } from '@/hooks/useTranslationStream'
import { startArtifactSession } from '@/lib/api'
import PrdUploadPanel from './PrdUploadPanel'

interface TranslationLauncherProps {
  onClose: () => void
}

export default function TranslationLauncher({ onClose }: TranslationLauncherProps) {
  const { sessionId, startArtifactSession: storeStartArtifact, closeTranslation } = useAppStore()
  const { startTranslation, phase } = useTranslationStream()
  const [mode, setMode] = useState<'choose' | 'prd' | 'idea'>('choose')

  const handlePrdSubmit = async (prdText: string) => {
    await startTranslation(sessionId, prdText)
    onClose()
  }

  const handleIdeaToAgent = async () => {
    try {
      const res = await startArtifactSession(sessionId, 'idea-to-agent')
      storeStartArtifact(res.artifact_session_id, res.artifact_type, res.questions)
      onClose()
    } catch (err) {
      console.error('Failed to start idea-to-agent', err)
    }
  }

  if (mode === 'prd') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div className="w-full max-w-2xl h-[80vh] rounded-2xl border border-zinc-700 bg-zinc-900 shadow-2xl flex flex-col overflow-hidden">
          <div className="flex items-center justify-between border-b border-zinc-800 px-6 py-4 shrink-0">
            <h2 className="text-base font-semibold text-zinc-100">PRD → agent.md</h2>
            <button onClick={onClose} className="rounded p-1 text-zinc-500 hover:text-zinc-300">
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="flex-1 overflow-hidden">
            <PrdUploadPanel
              onSubmit={handlePrdSubmit}
              isLoading={phase !== 'idle'}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl border border-zinc-700 bg-zinc-900 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 px-6 py-4">
          <div>
            <h2 className="text-base font-semibold text-zinc-100">AI-Era Artifact</h2>
            <p className="text-sm text-zinc-500 mt-0.5">Build or translate an agent.md</p>
          </div>
          <button onClick={onClose} className="rounded p-1 text-zinc-500 hover:text-zinc-300">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Options */}
        <div className="p-6 space-y-3">
          <button
            onClick={handleIdeaToAgent}
            className="w-full flex items-start gap-4 rounded-xl border border-zinc-700 bg-zinc-800/50 p-4 text-left hover:border-blue-500/50 hover:bg-zinc-800 transition-colors"
          >
            <Bot className="mt-0.5 h-5 w-5 text-blue-400 shrink-0" />
            <div>
              <p className="font-medium text-zinc-100">Start from Idea</p>
              <p className="text-sm text-zinc-400 mt-0.5 leading-snug">
                Answer 9 guided questions to generate a complete agent.md from scratch.
              </p>
            </div>
          </button>

          <button
            onClick={() => setMode('prd')}
            className="w-full flex items-start gap-4 rounded-xl border border-zinc-700 bg-zinc-800/50 p-4 text-left hover:border-blue-500/50 hover:bg-zinc-800 transition-colors"
          >
            <FileCode2 className="mt-0.5 h-5 w-5 text-blue-400 shrink-0" />
            <div>
              <p className="font-medium text-zinc-100">Translate Existing PRD</p>
              <p className="text-sm text-zinc-400 mt-0.5 leading-snug">
                Paste or upload a PRD — AskProduct extracts structure, generates agent.md,
                and surfaces gaps for you to fill.
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}
