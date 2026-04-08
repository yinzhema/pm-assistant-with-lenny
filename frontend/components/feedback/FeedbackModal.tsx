'use client'

import { useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { submitFeedback } from '@/lib/api'
import { X } from 'lucide-react'

export default function FeedbackModal() {
  const { setShowFeedback, sessionId } = useAppStore()
  const [comment, setComment] = useState('')
  const [rating, setRating] = useState<number | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  async function handleSubmit() {
    if (!comment.trim() && rating === null) return
    setIsSubmitting(true)
    try {
      await submitFeedback({
        session_id: sessionId,
        rating: rating ?? undefined,
        comment: comment.trim(),
      })
      setSubmitted(true)
      setTimeout(() => setShowFeedback(false), 1500)
    } catch (err) {
      console.error('Feedback submission failed:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="feedback-overlay"
        onClick={() => setShowFeedback(false)}
      />

      {/* Modal */}
      <div
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 150,
          width: 'min(480px, calc(100vw - 2rem))',
          background: 'white',
          border: '1px solid #EAEAE5',
          borderRadius: '14px',
          padding: '1.5rem',
          boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
        }}
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1.25rem',
          }}
        >
          <h2
            style={{
              fontFamily: "'Instrument Serif', Georgia, serif",
              fontStyle: 'italic',
              fontSize: '1.2rem',
              fontWeight: 400,
              color: '#0f172a',
              margin: 0,
            }}
          >
            Share Feedback
          </h2>
          <button
            onClick={() => setShowFeedback(false)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: '#9ca3af',
              padding: '0.25rem',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <X size={16} />
          </button>
        </div>

        {submitted ? (
          <div
            style={{
              textAlign: 'center',
              padding: '1.5rem 0',
              color: '#16a34a',
              fontWeight: 500,
            }}
          >
            ✓ Thanks for your feedback!
          </div>
        ) : (
          <>
            {/* Rating */}
            <div style={{ marginBottom: '1rem' }}>
              <label
                style={{
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  display: 'block',
                  marginBottom: '0.5rem',
                }}
              >
                How useful was this?
              </label>
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRating(star === rating ? null : star)}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '1.4rem',
                      opacity: rating !== null && star > rating ? 0.3 : 1,
                      transition: 'opacity 0.15s',
                      padding: '0.1rem',
                    }}
                  >
                    ⭐
                  </button>
                ))}
              </div>
            </div>

            {/* Comment */}
            <div style={{ marginBottom: '1.25rem' }}>
              <label
                style={{
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  display: 'block',
                  marginBottom: '0.5rem',
                }}
              >
                Comments
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="What's working well? What could be improved?"
                rows={4}
                style={{
                  width: '100%',
                  border: '1px solid #EAEAE5',
                  borderRadius: '8px',
                  padding: '0.65rem 0.85rem',
                  fontSize: '0.875rem',
                  lineHeight: 1.6,
                  color: '#1e293b',
                  fontFamily: 'inherit',
                  resize: 'vertical',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#2563eb'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#EAEAE5'
                }}
              />
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowFeedback(false)}
                style={{
                  background: 'transparent',
                  color: '#6b7280',
                  border: '1px solid #EAEAE5',
                  borderRadius: '8px',
                  padding: '0.5rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 400,
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  transition: 'all 0.15s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#F9F8F5'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                Cancel
              </button>

              <button
                onClick={handleSubmit}
                disabled={isSubmitting || (!comment.trim() && rating === null)}
                style={{
                  background: '#2563eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.5rem 1.25rem',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  cursor:
                    isSubmitting || (!comment.trim() && rating === null)
                      ? 'not-allowed'
                      : 'pointer',
                  opacity: isSubmitting || (!comment.trim() && rating === null) ? 0.6 : 1,
                  fontFamily: 'inherit',
                  transition: 'all 0.15s',
                }}
                onMouseEnter={(e) => {
                  if (!isSubmitting) e.currentTarget.style.background = '#1d4ed8'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#2563eb'
                }}
              >
                {isSubmitting ? 'Submitting…' : 'Submit'}
              </button>
            </div>
          </>
        )}
      </div>
    </>
  )
}
