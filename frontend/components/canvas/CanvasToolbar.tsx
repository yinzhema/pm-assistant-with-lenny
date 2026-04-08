'use client'

import { useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { useDocumentActions } from '@/hooks/useDocumentActions'
import { useAutosave } from '@/hooks/useAutosave'
import { Save, FileText, Sheet, Clock, X } from 'lucide-react'
import type { DocumentVersion } from '@/types'

export default function CanvasToolbar() {
  const { documentTitle, updateDocumentTitle, closeDocument } = useAppStore()
  const {
    isSaving,
    isExportingMd,
    isExportingXlsx,
    versions,
    showVersions,
    setShowVersions,
    handleSave,
    handleExportMarkdown,
    handleExportExcel,
    handleLoadVersions,
    handleRestoreVersion,
  } = useDocumentActions()
  const { isDirty, isSaving: isAutosaving, lastSavedAt } = useAutosave()

  const [editingTitle, setEditingTitle] = useState(false)

  function formatSavedAt(date: Date | null) {
    if (!date) return null
    return `Saved at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  }

  return (
    <div
      style={{
        borderBottom: '1px solid #EAEAE5',
        padding: '0.6rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        background: 'white',
        flexWrap: 'wrap',
        position: 'relative',
      }}
    >
      {/* Canvas label */}
      <span
        style={{
          fontSize: '0.7rem',
          fontWeight: 600,
          color: '#9ca3af',
          textTransform: 'uppercase',
          letterSpacing: '0.09em',
          marginRight: '0.25rem',
          flexShrink: 0,
        }}
      >
        Canvas
      </span>

      {/* Title input */}
      {editingTitle ? (
        <input
          autoFocus
          value={documentTitle}
          onChange={(e) => updateDocumentTitle(e.target.value)}
          onBlur={() => setEditingTitle(false)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') setEditingTitle(false)
          }}
          style={{
            flex: 1,
            minWidth: 0,
            border: '1px solid #2563eb',
            borderRadius: '6px',
            padding: '0.2rem 0.5rem',
            fontSize: '0.875rem',
            fontWeight: 500,
            color: '#111827',
            fontFamily: 'inherit',
            outline: 'none',
          }}
        />
      ) : (
        <button
          onClick={() => setEditingTitle(true)}
          title="Click to edit title"
          style={{
            flex: 1,
            minWidth: 0,
            textAlign: 'left',
            background: 'none',
            border: 'none',
            cursor: 'text',
            fontSize: '0.875rem',
            fontWeight: 500,
            color: '#111827',
            padding: '0.2rem 0.25rem',
            fontFamily: 'inherit',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {documentTitle}
          {isDirty && (
            <span style={{ color: '#9ca3af', fontWeight: 400 }}> •</span>
          )}
        </button>
      )}

      {/* Autosave status */}
      {!isDirty && lastSavedAt && (
        <span
          style={{
            fontSize: '0.68rem',
            color: '#9ca3af',
            flexShrink: 0,
          }}
        >
          {formatSavedAt(lastSavedAt)}
        </span>
      )}
      {isAutosaving && (
        <span style={{ fontSize: '0.68rem', color: '#9ca3af', flexShrink: 0 }}>
          Saving…
        </span>
      )}

      {/* Action buttons */}
      <ToolbarButton
        icon={<Save size={12} />}
        label={isSaving ? 'Saving…' : '💾'}
        title="Save document"
        onClick={handleSave}
        disabled={isSaving}
      />

      <ToolbarButton
        icon={<FileText size={12} />}
        label="⬇️ .md"
        title="Export as Markdown"
        onClick={handleExportMarkdown}
        disabled={isExportingMd}
      />

      <ToolbarButton
        icon={<Sheet size={12} />}
        label="📊 .xlsx"
        title="Export as Excel"
        onClick={handleExportExcel}
        disabled={isExportingXlsx}
      />

      <ToolbarButton
        icon={<Clock size={12} />}
        label="🕐"
        title="Version history"
        onClick={handleLoadVersions}
      />

      <ToolbarButton
        icon={<X size={12} />}
        label="✕"
        title="Close canvas"
        onClick={closeDocument}
        danger
      />

      {/* Versions popover */}
      {showVersions && versions.length > 0 && (
        <VersionsPopover
          versions={versions}
          onRestore={handleRestoreVersion}
          onClose={() => setShowVersions(false)}
        />
      )}
    </div>
  )
}

interface ToolbarButtonProps {
  icon?: React.ReactNode
  label: string
  title: string
  onClick: () => void
  disabled?: boolean
  danger?: boolean
}

function ToolbarButton({ label, title, onClick, disabled, danger }: ToolbarButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      style={{
        background: 'white',
        color: danger ? '#ef4444' : '#6b7280',
        border: `1px solid ${danger ? '#fecaca' : '#EAEAE5'}`,
        borderRadius: '6px',
        padding: '0.28rem 0.5rem',
        fontSize: '0.75rem',
        fontWeight: 500,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        transition: 'all 0.15s',
        fontFamily: 'inherit',
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        gap: '0.25rem',
        whiteSpace: 'nowrap',
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.background = danger ? '#fef2f2' : '#F9F8F5'
          e.currentTarget.style.color = danger ? '#dc2626' : '#111827'
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'white'
        e.currentTarget.style.color = danger ? '#ef4444' : '#6b7280'
      }}
    >
      {label}
    </button>
  )
}

interface VersionsPopoverProps {
  versions: DocumentVersion[]
  onRestore: (versionId: string) => void
  onClose: () => void
}

function VersionsPopover({ versions, onRestore, onClose }: VersionsPopoverProps) {
  return (
    <div
      style={{
        position: 'absolute',
        top: '100%',
        right: '1.5rem',
        zIndex: 100,
        background: 'white',
        border: '1px solid #EAEAE5',
        borderRadius: '10px',
        padding: '0.5rem',
        boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
        minWidth: '220px',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.25rem 0.5rem 0.5rem',
          borderBottom: '1px solid #EAEAE5',
          marginBottom: '0.25rem',
        }}
      >
        <span
          style={{
            fontSize: '0.7rem',
            fontWeight: 600,
            color: '#9ca3af',
            textTransform: 'uppercase',
            letterSpacing: '0.09em',
          }}
        >
          Version History
        </span>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#9ca3af',
            padding: '0',
          }}
        >
          <X size={12} />
        </button>
      </div>

      {versions.map((v) => (
        <div
          key={v.id}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.4rem 0.5rem',
            borderRadius: '6px',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#F9F8F5'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
          }}
        >
          <div>
            <div style={{ fontSize: '0.8rem', color: '#374151', fontWeight: 500 }}>
              Version {v.version_number}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
              {new Date(v.created_at).toLocaleString([], {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </div>
          </div>
          <button
            onClick={() => onRestore(v.id)}
            style={{
              background: 'none',
              border: '1px solid #EAEAE5',
              borderRadius: '5px',
              padding: '0.2rem 0.5rem',
              fontSize: '0.7rem',
              color: '#6b7280',
              cursor: 'pointer',
              fontFamily: 'inherit',
            }}
          >
            Restore
          </button>
        </div>
      ))}
    </div>
  )
}
