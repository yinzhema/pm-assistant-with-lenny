'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Message } from '@/types'
import SourcesAccordion from '@/components/chat/SourcesAccordion'

interface Props {
  message: Message
  isStreaming?: boolean
}

export default function MessageAssistant({ message, isStreaming }: Props) {
  return (
    <div className="flex flex-col gap-1">
      <div className="message-assistant">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {message.content}
        </ReactMarkdown>
        {isStreaming && (
          <span
            style={{
              display: 'inline-block',
              width: '2px',
              height: '1rem',
              background: '#6b7280',
              marginLeft: '2px',
              verticalAlign: 'middle',
              animation: 'cursorBlink 0.9s step-end infinite',
            }}
          />
        )}
      </div>
      {message.sources && message.sources.length > 0 && (
        <SourcesAccordion sources={message.sources} />
      )}
    </div>
  )
}
