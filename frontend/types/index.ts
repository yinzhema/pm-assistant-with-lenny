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
