'use client'

import { useAppStore } from '@/store/useAppStore'
import { MessageSquarePlus, X, MessageSquare } from 'lucide-react'
import { useState } from 'react'

const topbarBtnBase: React.CSSProperties = {
  background: 'white',
  color: '#6b7280',
  border: '1px solid #EAEAE5',
  borderRadius: '7px',
  padding: '0.3rem 0.8rem',
  fontSize: '0.8rem',
  fontWeight: 500,
  whiteSpace: 'nowrap',
  transition: 'all 0.15s',
  letterSpacing: '0.01em',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '0.375rem',
  fontFamily: 'inherit',
}

function TopBarButton({
  onClick,
  children,
  title,
}: {
  onClick: () => void
  children: React.ReactNode
  title?: string
}) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={onClick}
      title={title}
      style={{
        ...topbarBtnBase,
        background: hovered ? '#F9F8F5' : 'white',
        color: hovered ? '#111827' : '#6b7280',
        borderColor: hovered ? '#c4c0b8' : '#EAEAE5',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {children}
    </button>
  )
}

export default function TopBar() {
  const { workspaceActive, newChat, closeDocument, setShowFeedback, showFeedback } =
    useAppStore()
  const isWorkspace = workspaceActive()

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 flex items-center h-14 px-5 bg-white border-b border-border gap-3"
      style={{ boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <span className="text-lg" aria-hidden>
          🎙️
        </span>
        <span
          style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: '1.1rem',
            fontWeight: 400,
            fontStyle: 'italic',
            color: '#111827',
            letterSpacing: '0em',
            lineHeight: 1.2,
          }}
        >
          AskProduct
        </span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {isWorkspace && (
          <TopBarButton onClick={() => closeDocument()} title="Close document">
            <X size={13} />
            <span>Close Doc</span>
          </TopBarButton>
        )}

        <TopBarButton onClick={() => setShowFeedback(!showFeedback)}>
          <MessageSquare size={13} />
          <span>Feedback</span>
        </TopBarButton>

        <TopBarButton onClick={() => newChat()}>
          <MessageSquarePlus size={13} />
          <span>New Chat</span>
        </TopBarButton>
      </div>
    </header>
  )
}
