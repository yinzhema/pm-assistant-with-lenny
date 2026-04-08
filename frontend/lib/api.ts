import type {
  Document,
  DocumentVersion,
  GenerateDocumentRequest,
  ImproveSelectionRequest,
  FeedbackRequest,
} from '@/types'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    const error = await res.text().catch(() => res.statusText)
    throw new Error(`API error ${res.status}: ${error}`)
  }

  return res.json() as Promise<T>
}

// ── Document CRUD ──

export async function generateDocument(
  req: GenerateDocumentRequest
): Promise<{ document_id: string; html: string; title: string }> {
  return apiFetch('/documents/generate', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export async function saveDocument(
  doc: Omit<Document, 'id' | 'created_at' | 'updated_at'>
): Promise<Document> {
  return apiFetch('/documents', {
    method: 'POST',
    body: JSON.stringify(doc),
  })
}

export async function updateDocument(
  id: string,
  updates: Partial<Pick<Document, 'title' | 'content_html'>>
): Promise<Document> {
  return apiFetch(`/documents/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
}

export async function getDocument(id: string): Promise<Document> {
  return apiFetch(`/documents/${id}`)
}

export async function listDocuments(sessionId: string): Promise<Document[]> {
  return apiFetch(`/documents?session_id=${encodeURIComponent(sessionId)}`)
}

export async function getVersions(documentId: string): Promise<DocumentVersion[]> {
  return apiFetch(`/documents/${documentId}/versions`)
}

export async function restoreVersion(
  documentId: string,
  versionId: string
): Promise<Document> {
  return apiFetch(`/documents/${documentId}/versions/${versionId}/restore`, {
    method: 'POST',
  })
}

// ── AI Co-editing ──

export async function improveSelection(
  req: ImproveSelectionRequest
): Promise<{ replacement_html: string }> {
  return apiFetch('/documents/improve', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export async function critiqueDocument(
  documentId: string,
  contentHtml: string
): Promise<{ critique: string }> {
  return apiFetch('/documents/critique', {
    method: 'POST',
    body: JSON.stringify({ document_id: documentId, content_html: contentHtml }),
  })
}

// ── Export (returns Blob) ──

export async function exportMarkdown(documentId: string): Promise<Blob> {
  const res = await fetch(`${API}/documents/${documentId}/export/markdown`, {
    method: 'GET',
    headers: { Accept: 'text/markdown' },
  })
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  return res.blob()
}

export async function exportExcel(documentId: string): Promise<Blob> {
  const res = await fetch(`${API}/documents/${documentId}/export/excel`, {
    method: 'GET',
    headers: {
      Accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    },
  })
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  return res.blob()
}

// ── Feedback ──

export async function submitFeedback(req: FeedbackRequest): Promise<{ success: boolean }> {
  return apiFetch('/feedback', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

// ── Health ──

export async function getHealth(): Promise<{ status: string; version: string }> {
  return apiFetch('/health')
}
