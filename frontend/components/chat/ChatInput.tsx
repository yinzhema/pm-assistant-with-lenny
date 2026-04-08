'use client'

import { useState, useRef, useCallback, KeyboardEvent } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { useChatStream } from '@/hooks/useChatStream'
import { ArrowUp } from 'lucide-react'

export default function ChatInput() {
  const [value, setValue] = useState('')
  const { isStreaming } = useAppStore()
  const { sendMessage } = useChatStream()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = useCallback(async () => {
    const trimmed = value.trim()
    if (!trimmed || isStreaming) return
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    await sendMessage(trimmed)
  }, [value, isStreaming, sendMessage])

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`
  }

  const canSubmit = value.trim().length > 0 && !isStreaming

  return (
    <div
      style={{
        background: 'white',
        border: '1px solid #EAEAE5',
        borderRadius: '14px',
        padding: '0.6rem 0.6rem 0.6rem 1rem',
        display: 'flex',
        alignItems: 'flex-end',
        gap: '0.5rem',
        boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
      }}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => {
          setValue(e.target.value)
          handleInput()
        }}
        onKeyDown={handleKeyDown}
        placeholder="Ask about product management…"
        rows={1}
        disabled={isStreaming}
        style={{
          flex: 1,
          resize: 'none',
          border: 'none',
          outline: 'none',
          background: 'transparent',
          fontSize: '0.9rem',
          lineHeight: 1.6,
          color: '#1e293b',
          fontFamily: 'inherit',
          maxHeight: '180px',
          overflowY: 'auto',
        }}
      />

      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        title="Send message"
        style={{
          flexShrink: 0,
          width: '34px',
          height: '34px',
          borderRadius: '9px',
          border: 'none',
          background: canSubmit ? '#2563eb' : '#E5E7EB',
          color: canSubmit ? 'white' : '#9ca3af',
          cursor: canSubmit ? 'pointer' : 'not-allowed',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.15s',
          flexDirection: 'column',
        }}
        onMouseEnter={(e) => {
          if (canSubmit) e.currentTarget.style.background = '#1d4ed8'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = canSubmit ? '#2563eb' : '#E5E7EB'
        }}
      >
        {isStreaming ? (
          <span
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '2px',
              background: 'currentColor',
            }}
          />
        ) : (
          <ArrowUp size={16} />
        )}
      </button>
    </div>
  )
}
