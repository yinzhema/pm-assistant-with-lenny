'use client'

import { useEffect, useRef } from 'react'
import { useAppStore } from '@/store/useAppStore'
import MessageUser from '@/components/chat/MessageUser'
import MessageAssistant from '@/components/chat/MessageAssistant'
import ThinkingIndicator from '@/components/chat/ThinkingIndicator'

export default function ChatMessages() {
  const { messages, isStreaming, streamingContent } = useAppStore()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent, isStreaming])

  return (
    <div className="flex flex-col gap-1">
      {messages.map((message) =>
        message.role === 'user' ? (
          <MessageUser key={message.id} message={message} />
        ) : (
          <MessageAssistant key={message.id} message={message} />
        )
      )}

      {/* Streaming partial assistant message */}
      {isStreaming && streamingContent && (
        <MessageAssistant
          message={{
            id: '__streaming__',
            role: 'assistant',
            content: streamingContent,
            timestamp: new Date().toISOString(),
          }}
          isStreaming
        />
      )}

      {/* Thinking indicator when streaming but no content yet */}
      {isStreaming && !streamingContent && <ThinkingIndicator />}

      <div ref={bottomRef} />
    </div>
  )
}
