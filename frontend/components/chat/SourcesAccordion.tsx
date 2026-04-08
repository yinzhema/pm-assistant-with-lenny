'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink, Youtube } from 'lucide-react'
import { Source } from '@/types'

interface Props {
  sources: Source[]
}

export default function SourcesAccordion({ sources }: Props) {
  const [open, setOpen] = useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div
      style={{
        marginTop: '0.25rem',
        fontSize: '0.8rem',
        border: '1px solid #EAEAE5',
        borderRadius: '8px',
        overflow: 'hidden',
        background: 'white',
      }}
    >
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.5rem 0.85rem',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: '#6b7280',
          fontWeight: 500,
          fontSize: '0.78rem',
          letterSpacing: '0.01em',
          fontFamily: 'inherit',
        }}
      >
        <span>📚 View Sources ({sources.length})</span>
        {open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {open && (
        <div
          style={{
            borderTop: '1px solid #EAEAE5',
            padding: '0.5rem 0',
          }}
        >
          {sources.map((source) => (
            <SourceItem key={source.number} source={source} />
          ))}
        </div>
      )}
    </div>
  )
}

function SourceItem({ source }: { source: Source }) {
  const label = source.guest || source.author || 'Unknown'
  const link = source.youtube_url || source.url
  const isYoutube = !!source.youtube_url

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.6rem',
        padding: '0.4rem 0.85rem',
        borderBottom: '1px solid #F3F2EF',
      }}
    >
      {/* Number badge */}
      <span
        style={{
          flexShrink: 0,
          width: '18px',
          height: '18px',
          borderRadius: '50%',
          background: '#F3F2EF',
          color: '#6b7280',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.65rem',
          fontWeight: 600,
          marginTop: '1px',
        }}
      >
        {source.number}
      </span>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontWeight: 500,
            color: '#374151',
            fontSize: '0.78rem',
            marginBottom: '1px',
          }}
        >
          {label}
        </div>
        {source.title && (
          <div
            style={{
              color: '#6b7280',
              fontSize: '0.73rem',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {source.title}
          </div>
        )}
        {source.timestamp && (
          <div style={{ color: '#9ca3af', fontSize: '0.68rem' }}>
            {source.timestamp}
          </div>
        )}
      </div>

      {/* Link */}
      {link && (
        <a
          href={link}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            flexShrink: 0,
            color: '#6b7280',
            display: 'flex',
            alignItems: 'center',
            marginTop: '2px',
          }}
          title={isYoutube ? 'Open on YouTube' : 'Open article'}
        >
          {isYoutube ? <Youtube size={13} /> : <ExternalLink size={13} />}
        </a>
      )}
    </div>
  )
}
