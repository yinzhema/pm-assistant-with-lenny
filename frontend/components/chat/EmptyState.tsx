'use client'

import { useChatStream } from '@/hooks/useChatStream'

const SAMPLE_QUESTIONS = [
  'How do I prioritize features when I have limited engineering capacity?',
  'What are the best frameworks for conducting user discovery interviews?',
  'How should I structure a product strategy document?',
  'What does Lenny say about shipping fast vs. shipping right?',
  'How do I make a compelling case to leadership for my roadmap?',
  'What metrics should I track for a B2B SaaS product?',
]

export default function EmptyState() {
  const { sendMessage } = useChatStream()

  return (
    <div className="empty-state">
      {/* Icon */}
      <div className="empty-state-icon" style={{ margin: '0 auto 1.4rem' }}>
        <span style={{ fontSize: '1.75rem' }}>🎙️</span>
      </div>

      {/* Heading */}
      <h1>AskProduct</h1>

      {/* Subtitle */}
      <p>
        PM wisdom from Lenny&apos;s Podcast — 300+ episodes of expert advice,
        <br />
        instantly searchable.
      </p>

      {/* Sample questions label */}
      <div
        style={{
          fontSize: '0.7rem',
          fontWeight: 600,
          color: '#9ca3af',
          textTransform: 'uppercase',
          letterSpacing: '0.09em',
          marginBottom: '0.75rem',
        }}
      >
        Try asking
      </div>

      {/* Question cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '0.6rem',
          maxWidth: '640px',
          margin: '0 auto',
        }}
      >
        {SAMPLE_QUESTIONS.map((question) => (
          <button
            key={question}
            onClick={() => sendMessage(question)}
            style={{
              background: '#ffffff',
              color: '#374151',
              border: '1px solid #EAEAE5',
              borderRadius: '10px',
              fontSize: '0.875rem',
              padding: '0.85rem 1rem',
              textAlign: 'left',
              fontWeight: 400,
              lineHeight: 1.5,
              transition: 'all 0.18s ease',
              cursor: 'pointer',
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              fontFamily: 'inherit',
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget
              el.style.background = '#F9F8F5'
              el.style.borderColor = '#c4c0b8'
              el.style.color = '#111827'
              el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.07)'
              el.style.transform = 'translateY(-1px)'
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget
              el.style.background = '#ffffff'
              el.style.borderColor = '#EAEAE5'
              el.style.color = '#374151'
              el.style.boxShadow = '0 1px 3px rgba(0,0,0,0.04)'
              el.style.transform = 'translateY(0)'
            }}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}
