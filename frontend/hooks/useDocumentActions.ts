'use client'

import { useCallback, useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import {
  saveDocument,
  updateDocument,
  getVersions,
  restoreVersion,
  exportMarkdown,
  exportExcel,
} from '@/lib/api'
import { triggerDownload } from '@/lib/utils'
import type { DocumentVersion } from '@/types'

export function useDocumentActions() {
  const {
    documentHtml,
    documentTitle,
    documentId,
    templateId,
    sessionId,
    setDocumentId,
    updateDocumentHtml,
    updateDocumentTitle,
  } = useAppStore()

  const [isSaving, setIsSaving] = useState(false)
  const [isExportingMd, setIsExportingMd] = useState(false)
  const [isExportingXlsx, setIsExportingXlsx] = useState(false)
  const [versions, setVersions] = useState<DocumentVersion[]>([])
  const [showVersions, setShowVersions] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSave = useCallback(async () => {
    if (!documentHtml.trim()) return
    setIsSaving(true)
    setError(null)
    try {
      if (documentId) {
        await updateDocument(documentId, {
          title: documentTitle,
          content_html: documentHtml,
        })
      } else {
        const saved = await saveDocument({
          session_id: sessionId,
          title: documentTitle,
          template_id: templateId ?? 'unknown',
          content_html: documentHtml,
        })
        setDocumentId(saved.id)
      }
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsSaving(false)
    }
  }, [documentHtml, documentTitle, documentId, sessionId, templateId, setDocumentId])

  const handleExportMarkdown = useCallback(async () => {
    if (!documentId) {
      // Save first then export
      await handleSave()
      return
    }
    setIsExportingMd(true)
    setError(null)
    try {
      const blob = await exportMarkdown(documentId)
      const safeName = documentTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase()
      triggerDownload(blob, `${safeName}.md`)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsExportingMd(false)
    }
  }, [documentId, documentTitle, handleSave])

  const handleExportExcel = useCallback(async () => {
    if (!documentId) {
      await handleSave()
      return
    }
    setIsExportingXlsx(true)
    setError(null)
    try {
      const blob = await exportExcel(documentId)
      const safeName = documentTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase()
      triggerDownload(blob, `${safeName}.xlsx`)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsExportingXlsx(false)
    }
  }, [documentId, documentTitle, handleSave])

  const handleLoadVersions = useCallback(async () => {
    if (!documentId) return
    setError(null)
    try {
      const versionList = await getVersions(documentId)
      setVersions(versionList)
      setShowVersions(true)
    } catch (err) {
      setError((err as Error).message)
    }
  }, [documentId])

  const handleRestoreVersion = useCallback(
    async (versionId: string) => {
      if (!documentId) return
      setError(null)
      try {
        const restored = await restoreVersion(documentId, versionId)
        updateDocumentHtml(restored.content_html)
        updateDocumentTitle(restored.title)
        setShowVersions(false)
      } catch (err) {
        setError((err as Error).message)
      }
    },
    [documentId, updateDocumentHtml, updateDocumentTitle]
  )

  return {
    isSaving,
    isExportingMd,
    isExportingXlsx,
    versions,
    showVersions,
    setShowVersions,
    error,
    handleSave,
    handleExportMarkdown,
    handleExportExcel,
    handleLoadVersions,
    handleRestoreVersion,
  }
}
