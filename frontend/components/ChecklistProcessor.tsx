'use client'

import { useState } from 'react'
import { Play, CheckCircle, X, Clock } from 'lucide-react'
import { Question, ChecklistResult } from '@/types'
import { api } from '@/lib/api'

interface ChecklistProcessorProps {
  questions: Question[]
  selectedFiles: number[]
}

export default function ChecklistProcessor({ questions, selectedFiles }: ChecklistProcessorProps) {
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState<ChecklistResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleProcessChecklist = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file to process')
      return
    }

    if (questions.length === 0) {
      setError('Please add at least one question or condition')
      return
    }

    setProcessing(true)
    setError(null)
    setResult(null)

    try {
      const questionTexts = questions
        .filter(q => q.type === 'question')
        .map(q => q.text)
      
      const conditionTexts = questions
        .filter(q => q.type === 'condition')
        .map(q => q.text)

      const response = await api.post('/api/v1/checklist', {
        message: 'Process checklist items',
        file_ids: selectedFiles,
        questions: questionTexts,
        conditions: conditionTexts,
      })
      
      setResult(response)
    } catch (error) {
      setError('Processing failed: ' + (error as Error).message)
    } finally {
      setProcessing(false)
    }
  }

  const questionsOnly = questions.filter(q => q.type === 'question')
  const conditionsOnly = questions.filter(q => q.type === 'condition')

  return (
    <div className="space-y-6">
      {/* Process Button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            Process Documents
          </h3>
          <p className="text-sm text-gray-600">
            {selectedFiles.length} file(s) selected, {questions.length} item(s) to process
          </p>
        </div>
        <button
          onClick={handleProcessChecklist}
          disabled={processing || selectedFiles.length === 0 || questions.length === 0}
          className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {processing ? (
            <>
              <Clock className="h-5 w-5 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              <span>Process Checklist</span>
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center space-x-2">
            <X className="h-5 w-5 text-red-500" />
            <span className="text-sm text-red-600">{error}</span>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm text-green-600">
                Checklist processing completed successfully
              </span>
            </div>
          </div>

          {/* Question Answers */}
          {Object.keys(result.question_answers).length > 0 && (
            <div className="bg-white border rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Question Answers
              </h4>
              <div className="space-y-4">
                {Object.entries(result.question_answers).map(([question, answer], index) => (
                  <div key={index} className="border-l-4 border-blue-400 pl-4">
                    <div className="text-sm font-medium text-gray-900 mb-2">
                      Q: {question}
                    </div>
                    <div className="text-sm text-gray-700 bg-blue-50 p-3 rounded">
                      A: {answer}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Condition Evaluations */}
          {Object.keys(result.condition_evaluations).length > 0 && (
            <div className="bg-white border rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Condition Evaluations
              </h4>
              <div className="space-y-3">
                {Object.entries(result.condition_evaluations).map(([condition, evaluation], index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
                      evaluation ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {evaluation ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <X className="h-4 w-4 text-red-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-gray-900">{condition}</div>
                      <div className={`text-sm font-medium ${
                        evaluation ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {evaluation ? 'TRUE' : 'FALSE'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      {!result && !processing && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            How to use:
          </h4>
          <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
            <li>Upload PDF documents using the upload section</li>
            <li>Select files you want to process</li>
            <li>Add questions and conditions you want to evaluate</li>
            <li>Click "Process Checklist" to analyze the documents</li>
          </ol>
        </div>
      )}
    </div>
  )
}