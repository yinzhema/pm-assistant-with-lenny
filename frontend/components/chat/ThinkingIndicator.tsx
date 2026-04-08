'use client'

export default function ThinkingIndicator() {
  return (
    <div
      className="message-assistant"
      style={{ width: 'fit-content', padding: '0.75rem 1.1rem' }}
    >
      <div className="thinking-dots">
        <span className="thinking-dot" />
        <span className="thinking-dot" />
        <span className="thinking-dot" />
      </div>
    </div>
  )
}
