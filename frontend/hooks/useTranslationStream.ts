'use client'

import { useCallback, useRef, useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import {
  openPrdTranslationStream,
  openClarifyGapStream,
  openFinalizeTranslationStream,
} from '@/lib/api'
import type { GapItem } from '@/types'

async function readSseStream(
  response: Response,
  onEvent: (event: Record<string, unknown>) => void
) {
  if (!response.body) return
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const raw = line.slice(6).trim()
      if (!raw || raw === '[DONE]') continue
      try { onEvent(JSON.parse(raw)) } catch { /* ignore */ }
    }
  }
}

export function useTranslationStream() {
  const store = useAppStore()
  const abortRef = useRef<AbortController | null>(null)
  const [phase, setPhase] = useState<'idle' | 'extracting' | 'generating' | 'gap_analysis' | 'clarifying' | 'finalizing'>('idle')
  const [clarifyingQuestions, setClarifyingQuestions] = useState<GapItem[]>([])
  const [translationSessionId, setTranslationSessionId] = useState<string | null>(null)

  const startTranslation = useCallback(
    async (sessionId: string, prdText: string) => {
      if (abortRef.current) abortRef.current.abort()
      abortRef.current = new AbortController()

      store.startTranslationSession('', 'prd-to-agent', prdText)
      setPhase('extracting')

      try {
        const res = await openPrdTranslationStream(sessionId, prdText, abortRef.current.signal)
        if (!res.ok) throw new Error(`Translation stream error: ${res.status}`)

        await readSseStream(res, (event) => {
          const type = event.type as string

          if (type === 'extraction_done') {
            setPhase('generating')
            store.setTranslationStatus('generating')
          } else if (type === 'agent_section_done') {
            setPhase('generating')
            store.addAgentSection({
              section_key: event.section_key as string,
              html: event.html as string,
              confidence: event.confidence as 'green' | 'yellow' | 'red',
            })
          } else if (type === 'gap_analysis_done') {
            setPhase('gap_analysis')
            store.setTranslationGaps(event.gaps as GapItem[])
            store.setTranslationStatus('gap_analysis')

            // Update translationSession id from the event
            const tid = event.translation_session_id as string
            if (tid) {
              setTranslationSessionId(tid)
              // Patch the store session id
              const sess = store.translationSession
              if (sess) {
                store.startTranslationSession(tid, 'prd-to-agent', prdText)
              }
            }
          } else if (type === 'clarifying_questions') {
            const qs = event.questions as GapItem[]
            setClarifyingQuestions(qs)
            store.setTranslationStatus('clarifying')

            const tid = event.translation_session_id as string
            if (tid) setTranslationSessionId(tid)
          }
        })
      } catch (err) {
        if ((err as Error).name === 'AbortError') return
        console.error('Translation stream error:', err)
      } finally {
        if (phase !== 'clarifying') setPhase('idle')
      }
    },
    [store, phase]
  )

  const clarifyGap = useCallback(
    async (questionId: string, answer: string) => {
      const tid = translationSessionId ?? store.translationSession?.id
      if (!tid) return

      store.addTranslationClarification(questionId, answer)

      try {
        const res = await openClarifyGapStream(tid, questionId, answer)
        if (!res.ok) throw new Error(`Clarify error: ${res.status}`)

        await readSseStream(res, (event) => {
          const type = event.type as string
          if (type === 'section_updated') {
            store.updateAgentSection(
              event.section_key as string,
              event.html as string,
              event.confidence as 'green' | 'yellow' | 'red'
            )
          }
        })
      } catch (err) {
        console.error('Clarify error:', err)
      }
    },
    [store, translationSessionId]
  )

  const finalize = useCallback(
    async (onComplete: (html: string) => void) => {
      const tid = translationSessionId ?? store.translationSession?.id
      if (!tid) return

      setPhase('finalizing')
      store.setTranslationStatus('finalizing')

      try {
        const res = await openFinalizeTranslationStream(tid)
        if (!res.ok) throw new Error(`Finalize error: ${res.status}`)

        await readSseStream(res, (event) => {
          const type = event.type as string
          if (type === 'final_agent_html') {
            store.setTranslationStatus('complete')
            onComplete(event.html as string)
          }
        })
      } catch (err) {
        console.error('Finalize error:', err)
      } finally {
        setPhase('idle')
      }
    },
    [store, translationSessionId]
  )

  return {
    startTranslation,
    clarifyGap,
    finalize,
    phase,
    clarifyingQuestions,
    translationSessionId,
  }
}
