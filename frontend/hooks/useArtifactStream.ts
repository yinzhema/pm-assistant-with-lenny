'use client'

import { useCallback, useRef, useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import {
  openArtifactAnswerStream,
  openArtifactSynthesisStream,
  skipArtifactQuestion,
  jumpToArtifactQuestion,
} from '@/lib/api'

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
      try {
        onEvent(JSON.parse(raw))
      } catch {
        // ignore parse errors
      }
    }
  }
}

export function useArtifactStream() {
  const store = useAppStore()
  const abortRef = useRef<AbortController | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isSynthesizing, setIsSynthesizing] = useState(false)
  const [kbSnippets, setKbSnippets] = useState<Record<string, string>>({})

  const sendAnswer = useCallback(
    async (questionId: string, answer: string) => {
      const session = store.artifactSession
      if (!session || isStreaming) return

      if (abortRef.current) abortRef.current.abort()
      abortRef.current = new AbortController()

      setIsStreaming(true)

      // Find section_key for this question
      const question = session.questions.find((q) => q.id === questionId)
      if (!question) return

      // Optimistically mark section as streaming
      store.setArtifactSectionStreaming(question.section_key, true)

      try {
        const res = await openArtifactAnswerStream(
          session.id,
          questionId,
          answer,
          abortRef.current.signal
        )

        if (!res.ok) throw new Error(`Answer stream error: ${res.status}`)

        await readSseStream(res, (event) => {
          const type = event.type as string

          if (type === 'kb_snippet') {
            setKbSnippets((prev) => ({
              ...prev,
              [event.question_id as string]: event.snippet as string,
            }))
          } else if (type === 'preview_chunk') {
            store.appendArtifactSectionChunk(
              event.section_key as string,
              event.content as string
            )
          } else if (type === 'preview_done') {
            store.markArtifactSectionAnswered(event.section_key as string)
          } else if (type === 'done') {
            // Advance to next question
            store.setArtifactAnswer(questionId, answer)
          }
        })
      } catch (err) {
        if ((err as Error).name === 'AbortError') return
        console.error('Answer stream error:', err)
        store.markArtifactSectionAnswered(question.section_key)
      } finally {
        setIsStreaming(false)
      }
    },
    [store, isStreaming]
  )

  const skipQuestion = useCallback(
    async (questionId: string) => {
      const session = store.artifactSession
      if (!session) return

      const question = session.questions.find((q) => q.id === questionId)
      if (!question) return

      await skipArtifactQuestion(session.id, questionId)
      store.markArtifactSectionSkipped(question.section_key)
      // Advance index
      const currentIdx = session.questions.findIndex((q) => q.id === questionId)
      if (currentIdx < session.questions.length - 1) {
        store.setArtifactCurrentIndex(currentIdx + 1)
      }
    },
    [store]
  )

  const jumpToQuestion = useCallback(
    async (questionId: string) => {
      const session = store.artifactSession
      if (!session) return

      const { current_index } = await jumpToArtifactQuestion(session.id, questionId)
      store.setArtifactCurrentIndex(current_index)
    },
    [store]
  )

  const synthesize = useCallback(
    async (onComplete: (html: string, title: string) => void) => {
      const session = store.artifactSession
      if (!session || isSynthesizing) return

      if (abortRef.current) abortRef.current.abort()
      abortRef.current = new AbortController()

      setIsSynthesizing(true)

      try {
        const res = await openArtifactSynthesisStream(
          session.id,
          abortRef.current.signal
        )
        if (!res.ok) throw new Error(`Synthesis error: ${res.status}`)

        await readSseStream(res, (event) => {
          const type = event.type as string
          if (type === 'synthesis_done') {
            onComplete(event.html as string, event.title as string)
          }
        })
      } catch (err) {
        if ((err as Error).name === 'AbortError') return
        console.error('Synthesis error:', err)
      } finally {
        setIsSynthesizing(false)
      }
    },
    [store, isSynthesizing]
  )

  return {
    sendAnswer,
    skipQuestion,
    jumpToQuestion,
    synthesize,
    isStreaming,
    isSynthesizing,
    kbSnippets,
  }
}
