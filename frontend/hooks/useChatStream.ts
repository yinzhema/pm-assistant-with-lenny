'use client'

import { useCallback, useRef } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { Source } from '@/types'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'

export function useChatStream() {
  const {
    addUserMessage,
    appendStreamToken,
    finalizeAssistantMessage,
    setOfferTemplate,
    openDocument,
    sessionId,
    messages,
  } = useAppStore()

  const abortRef = useRef<AbortController | null>(null)

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return

      // Cancel any in-flight request
      if (abortRef.current) {
        abortRef.current.abort()
      }
      abortRef.current = new AbortController()

      addUserMessage(content)

      const conversationHistory = messages
        .slice(-20)
        .map((m) => ({ role: m.role, content: m.content }))

      try {
        const res = await fetch(`${API}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: content,
            history: conversationHistory,
          }),
          signal: abortRef.current.signal,
        })

        if (!res.ok) {
          throw new Error(`Chat API error: ${res.status}`)
        }

        if (!res.body) {
          throw new Error('No response body')
        }

        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        const collectedSources: Source[] = []

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

            let event: Record<string, unknown>
            try {
              event = JSON.parse(raw)
            } catch {
              continue
            }

            const type = event.type as string

            if (type === 'token') {
              appendStreamToken(event.content as string)
            } else if (type === 'sources') {
              const srcs = event.sources as Source[]
              collectedSources.push(...srcs)
            } else if (type === 'template_offer') {
              setOfferTemplate(event.template_id as string, event.template_name as string)
            } else if (type === 'template_created') {
              openDocument(
                event.html as string,
                event.template_id as string,
                event.title as string
              )
            } else if (type === 'done') {
              finalizeAssistantMessage(collectedSources)
            } else if (type === 'error') {
              appendStreamToken(
                `\n\n_Error: ${event.message as string}_`
              )
              finalizeAssistantMessage([])
            }
          }
        }

        // Finalize in case done event was missed
        finalizeAssistantMessage(collectedSources)
      } catch (err) {
        if ((err as Error).name === 'AbortError') return
        console.error('Chat stream error:', err)
        appendStreamToken('\n\n_Sorry, something went wrong. Please try again._')
        finalizeAssistantMessage([])
      }
    },
    [
      addUserMessage,
      appendStreamToken,
      finalizeAssistantMessage,
      setOfferTemplate,
      openDocument,
      sessionId,
      messages,
    ]
  )

  const abort = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort()
    }
  }, [])

  return { sendMessage, abort }
}
