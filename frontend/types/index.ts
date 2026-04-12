export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: string
}

export interface Source {
  number: number
  guest: string
  author: string
  title: string
  youtube_url: string
  url: string
  timestamp: string
  source_name: string
  similarity_score: number
}

export type TemplateId =
  | 'prd-1pager'
  | 'prd-full'
  | 'strategy-doc'
  | 'rice'
  | 'ice'
  | 'moscow'
  | 'kano'
  | 'wsjf'
  | 'now-next-later'
  | 'outcome-roadmap'
  | 'jtbd'
  | 'opp-solution-tree'

export interface Document {
  id: string
  session_id: string
  title: string
  template_id: string
  content_html: string
  created_at: string
  updated_at: string
}

export interface DocumentVersion {
  id: string
  document_id: string
  content_html: string
  version_number: number
  created_at: string
}

export interface ChatRequest {
  message: string
  history: Array<{ role: string; content: string }>
}

export interface GenerateDocumentRequest {
  template_id: string
  user_context: string
  history?: Array<{ role: string; content: string }>
}

export interface ImproveSelectionRequest {
  action: 'improve' | 'expand' | 'critique' | 'simplify'
  selected_text: string
  full_html: string
}

export interface FeedbackRequest {
  session_id: string
  rating?: number
  comment: string
}

// ── Artifact Builder ──────────────────────────────────────────────────────────

export type ArtifactType = 'play-to-win' | 'opportunity-assessment' | 'idea-to-agent'

export interface ArtifactTypeInfo {
  id: ArtifactType
  title: string
  description: string
  icon: string
  question_count: number
}

export interface Question {
  id: string
  text: string
  section_key: string
  section_label: string
  placeholder: string
  why_it_matters: string
  kb_query: string | null
  allow_skip: boolean
}

export interface ArtifactSession {
  id: string                          // backend UUID
  artifactType: ArtifactType
  questions: Question[]
  currentIndex: number
  answers: Record<string, string>     // questionId → answer text
  skipped: string[]                   // questionId list
  status: 'in_progress' | 'complete'
}

export interface ArtifactSectionPreview {
  sectionKey: string
  sectionLabel: string
  placeholder: string
  html: string
  isStreaming: boolean
  isAnswered: boolean
  isSkipped: boolean
}

// ── Translation ───────────────────────────────────────────────────────────────

export type TranslationMode = 'prd-to-agent' | 'idea-to-agent'

export interface AgentMdSection {
  section_key: string
  html: string
  confidence: 'green' | 'yellow' | 'red'
}

export interface GapItem {
  id: string
  gap_category: string
  section: string
  question: string
  severity: 'high' | 'medium' | 'low'
  description: string
}

export interface TranslationSession {
  id: string
  translationMode: TranslationMode
  prdText: string
  agentSections: AgentMdSection[]
  gaps: GapItem[]
  clarifications: Record<string, string>
  status: 'extracting' | 'generating' | 'gap_analysis' | 'clarifying' | 'finalizing' | 'complete'
}
