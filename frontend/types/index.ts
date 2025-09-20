export interface FileInfo {
  id: number
  filename: string
  original_filename: string
  anthropic_file_id: string
  upload_date: string
}

export interface Question {
  id: number
  text: string
  type: 'question' | 'condition'
  created_date: string
}

export interface QuestionCreate {
  text: string
  type: 'question' | 'condition'
}

export interface ChatRequest {
  message: string
  file_ids?: number[]
  questions?: string[]
  conditions?: string[]
}

export interface ChecklistResult {
  question_answers: Record<string, string>
  condition_evaluations: Record<string, boolean>
}