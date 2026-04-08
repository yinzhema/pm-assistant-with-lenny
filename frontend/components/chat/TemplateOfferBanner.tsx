'use client'

import { useAppStore } from '@/store/useAppStore'
import { TEMPLATES } from '@/lib/templates'
import { generateDocument } from '@/lib/api'
import { useState } from 'react'
import { Sparkles } from 'lucide-react'

export default function TemplateOfferBanner() {
  const { offerTemplateId, offerTemplateName, clearOfferTemplate, openDocument, sessionId } =
    useAppStore()
  const [isGenerating, setIsGenerating] = useState(false)

  if (!offerTemplateId) return null

  const displayName = offerTemplateName || TEMPLATES[offerTemplateId] || offerTemplateId

  async function handleCreate() {
    if (!offerTemplateId) return
    setIsGenerating(true)
    try {
      const result = await generateDocument({
        template_id: offerTemplateId,
        context: '',
        session_id: sessionId,
      })
      openDocument(result.html, offerTemplateId, result.title)
    } catch (err) {
      console.error('Failed to generate document:', err)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="template-offer">
      <div className="template-offer-eyebrow">✨ Suggestion</div>
      <div
        style={{
          fontSize: '0.875rem',
          color: '#0f172a',
          marginBottom: '0.75rem',
          lineHeight: 1.55,
        }}
      >
        Want to work with a <strong>{displayName}</strong>?
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <button
          onClick={handleCreate}
          disabled={isGenerating}
          style={{
            background: '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '0.45rem 1rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: isGenerating ? 'not-allowed' : 'pointer',
            opacity: isGenerating ? 0.7 : 1,
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            transition: 'all 0.15s',
            fontFamily: 'inherit',
          }}
          onMouseEnter={(e) => {
            if (!isGenerating) {
              e.currentTarget.style.background = '#1d4ed8'
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#2563eb'
          }}
        >
          <Sparkles size={12} />
          {isGenerating ? 'Creating…' : `✦ Create ${displayName}`}
        </button>

        <button
          onClick={clearOfferTemplate}
          style={{
            background: 'transparent',
            color: '#6b7280',
            border: '1px solid #EAEAE5',
            borderRadius: '8px',
            padding: '0.45rem 0.85rem',
            fontSize: '0.8rem',
            fontWeight: 400,
            cursor: 'pointer',
            transition: 'all 0.15s',
            fontFamily: 'inherit',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#F9F8F5'
            e.currentTarget.style.color = '#111827'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.color = '#6b7280'
          }}
        >
          No thanks
        </button>
      </div>
    </div>
  )
}
