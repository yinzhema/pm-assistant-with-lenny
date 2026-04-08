'use client'

import { useEffect, useRef, useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { updateDocument, saveDocument } from '@/lib/api'

const AUTOSAVE_DELAY_MS = 60_000 // 60 seconds

export function useAutosave() {
  const { documentHtml, documentTitle, documentId, templateId, sessionId, setDocumentId } =
    useAppStore()

  const [isDirty, setIsDirty] = useState(false)
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const previousHtmlRef = useRef(documentHtml)

  useEffect(() => {
    // Track if the document has changed since last save
    if (documentHtml !== previousHtmlRef.current) {
      setIsDirty(true)
      previousHtmlRef.current = documentHtml
    }
  }, [documentHtml])

  useEffect(() => {
    // Only autosave if document is dirty and has content
    if (!isDirty || !documentHtml.trim()) return

    // Clear any existing timer
    if (timerRef.current) {
      clearTimeout(timerRef.current)
    }

    timerRef.current = setTimeout(async () => {
      setIsSaving(true)
      try {
        if (documentId) {
          await updateDocument(documentId, {
            title: documentTitle,
            content_html: documentHtml,
          })
        } else if (documentHtml.trim()) {
          const { id } = await saveDocument({
            session_id: sessionId,
            title: documentTitle,
            template_id: templateId ?? 'unknown',
            content_html: documentHtml,
          })
          setDocumentId(id)
        }
        setIsDirty(false)
        setLastSavedAt(new Date())
      } catch (err) {
        console.error('Autosave failed:', err)
      } finally {
        setIsSaving(false)
      }
    }, AUTOSAVE_DELAY_MS)

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [isDirty, documentHtml, documentTitle, documentId, templateId, sessionId, setDocumentId])

  // Reset dirty state when document is closed
  useEffect(() => {
    if (!documentHtml) {
      setIsDirty(false)
      setLastSavedAt(null)
      previousHtmlRef.current = ''
    }
  }, [documentHtml])

  return { isDirty, isSaving, lastSavedAt }
}
