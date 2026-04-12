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
  exportDocx,
  exportPdf,
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
  } = useAppStore()

  const [isSaving, setIsSaving] = useState(false)
  const [isExportingMd, setIsExportingMd] = useState(false)
  const [isExportingXlsx, setIsExportingXlsx] = useState(false)
  const [isExportingDocx, setIsExportingDocx] = useState(false)
  const [isExportingPdf, setIsExportingPdf] = useState(false)
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
    if (!documentHtml.trim()) return
    setIsExportingMd(true)
    setError(null)
    try {
      const blob = await exportMarkdown(documentHtml, documentTitle)
      const safeName = documentTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase()
      triggerDownload(blob, `${safeName}.md`)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsExportingMd(false)
    }
  }, [documentHtml, documentTitle])

  const handleExportExcel = useCallback(async () => {
    if (!documentHtml.trim()) return
    setIsExportingXlsx(true)
    setError(null)
    try {
      const blob = await exportExcel(documentHtml, documentTitle)
      const safeName = documentTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase()
      triggerDownload(blob, `${safeName}.xlsx`)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsExportingXlsx(false)
    }
  }, [documentHtml, documentTitle])

  const handleExportDocx = useCallback(async () => {
    if (!documentHtml.trim()) return
    setIsExportingDocx(true)
    setError(null)
    try {
      const blob = await exportDocx(documentHtml, documentTitle)
      const safeName = documentTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase()
      triggerDownload(blob, `${safeName}.docx`)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsExportingDocx(false)
    }
  }, [documentHtml, documentTitle])

  const handleExportPdf = useCallback(async () => {
    if (!documentHtml.trim()) return
    setIsExportingPdf(true)
    setError(null)
    try {
      const blob = await exportPdf(documentHtml, documentTitle)
      const safeName = documentTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase()
      triggerDownload(blob, `${safeName}.pdf`)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsExportingPdf(false)
    }
  }, [documentHtml, documentTitle])

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
        updateDocumentHtml(restored.html)
        setShowVersions(false)
      } catch (err) {
        setError((err as Error).message)
      }
    },
    [documentId, updateDocumentHtml]
  )

  return {
    isSaving,
    isExportingMd,
    isExportingXlsx,
    isExportingDocx,
    isExportingPdf,
    versions,
    showVersions,
    setShowVersions,
    error,
    handleSave,
    handleExportMarkdown,
    handleExportExcel,
    handleExportDocx,
    handleExportPdf,
    handleLoadVersions,
    handleRestoreVersion,
  }
}
