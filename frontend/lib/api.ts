import type {
  Document,
  DocumentVersion,
  GenerateDocumentRequest,
  ImproveSelectionRequest,
  FeedbackRequest,
  ArtifactType,
  Question,
  GapItem,
} from '@/types'

const API = process.env.NEXT_PUBLIC_API_URL || '/backend/api'

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

// ── Document generation ──

export async function generateDocument(
  req: GenerateDocumentRequest
): Promise<{ html: string }> {
  return apiFetch('/documents/generate', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

// ── Document CRUD ──

export async function saveDocument(
  doc: Omit<Document, 'id' | 'created_at' | 'updated_at'>
): Promise<{ id: string }> {
  return apiFetch('/documents', {
    method: 'POST',
    body: JSON.stringify(doc),
  })
}

export async function updateDocument(
  id: string,
  updates: Partial<Pick<Document, 'title' | 'content_html'>>
): Promise<{ id: string; updated_at: string }> {
  return apiFetch(`/documents/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
}

export async function getDocument(id: string): Promise<Document> {
  return apiFetch(`/documents/${id}`)
}

export async function listDocuments(sessionId: string): Promise<Document[]> {
  const res = await apiFetch<{ documents: Document[] }>(
    `/documents?session_id=${encodeURIComponent(sessionId)}`
  )
  return res.documents
}

export async function getVersions(documentId: string): Promise<DocumentVersion[]> {
  const res = await apiFetch<{ versions: DocumentVersion[] }>(
    `/documents/${documentId}/versions`
  )
  return res.versions
}

export async function restoreVersion(
  documentId: string,
  versionId: string
): Promise<{ html: string }> {
  return apiFetch(`/documents/${documentId}/restore`, {
    method: 'POST',
    body: JSON.stringify({ version_id: versionId }),
  })
}

// ── AI Co-editing ──

export async function improveSelection(
  req: ImproveSelectionRequest
): Promise<{ html: string }> {
  return apiFetch('/documents/improve', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export async function critiqueDocument(
  documentHtml: string,
  templateId: string
): Promise<{ html: string }> {
  return apiFetch('/documents/critique', {
    method: 'POST',
    body: JSON.stringify({ document_html: documentHtml, template_id: templateId }),
  })
}

// ── Export (returns Blob) ──

export async function exportMarkdown(html: string, title: string): Promise<Blob> {
  const res = await fetch(`${API}/export/markdown`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_html: html, title }),
  })
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  return res.blob()
}

export async function exportExcel(html: string, title: string): Promise<Blob> {
  const res = await fetch(`${API}/export/excel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_html: html, title }),
  })
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  return res.blob()
}

export async function exportDocx(html: string, title: string): Promise<Blob> {
  const res = await fetch(`${API}/export/docx`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_html: html, title }),
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

export async function exportPdf(html: string, title: string): Promise<Blob> {
  const res = await fetch(`${API}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_html: html, title }),
  })
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  return res.blob()
}

// ── Health ──

export async function getHealth(): Promise<{ status: string; version: string }> {
  return apiFetch('/health')
}

// ── Artifact Builder ──────────────────────────────────────────────────────────

export interface StartArtifactSessionResponse {
  artifact_session_id: string
  artifact_type: ArtifactType
  questions: Question[]
}

export async function startArtifactSession(
  sessionId: string,
  artifactType: ArtifactType
): Promise<StartArtifactSessionResponse> {
  return apiFetch('/artifacts/sessions', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, artifact_type: artifactType }),
  })
}

export function openArtifactAnswerStream(
  artifactSessionId: string,
  questionId: string,
  answer: string,
  signal?: AbortSignal
): Promise<Response> {
  return fetch(`${API}/artifacts/sessions/${artifactSessionId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_id: questionId, answer }),
    signal,
  })
}

export async function skipArtifactQuestion(
  artifactSessionId: string,
  questionId: string
): Promise<void> {
  await apiFetch(`/artifacts/sessions/${artifactSessionId}/skip`, {
    method: 'POST',
    body: JSON.stringify({ question_id: questionId }),
  })
}

export async function jumpToArtifactQuestion(
  artifactSessionId: string,
  questionId: string
): Promise<{ current_index: number }> {
  return apiFetch(`/artifacts/sessions/${artifactSessionId}/jump`, {
    method: 'POST',
    body: JSON.stringify({ question_id: questionId }),
  })
}

export function openArtifactSynthesisStream(
  artifactSessionId: string,
  signal?: AbortSignal
): Promise<Response> {
  return fetch(`${API}/artifacts/sessions/${artifactSessionId}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
    signal,
  })
}

export async function getArtifactTypes(): Promise<{ artifact_types: Array<{ id: ArtifactType; title: string; description: string; icon: string; question_count: number }> }> {
  return apiFetch('/artifacts/types')
}

// ── Translation ───────────────────────────────────────────────────────────────

export function openPrdTranslationStream(
  sessionId: string,
  prdText: string,
  signal?: AbortSignal
): Promise<Response> {
  return fetch(`${API}/translation/prd-to-agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, prd_text: prdText }),
    signal,
  })
}

export function openClarifyGapStream(
  translationSessionId: string,
  questionId: string,
  answer: string,
  signal?: AbortSignal
): Promise<Response> {
  return fetch(`${API}/translation/prd-to-agent/${translationSessionId}/clarify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_id: questionId, answer }),
    signal,
  })
}

export function openFinalizeTranslationStream(
  translationSessionId: string,
  signal?: AbortSignal
): Promise<Response> {
  return fetch(`${API}/translation/prd-to-agent/${translationSessionId}/finalize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
    signal,
  })
}
