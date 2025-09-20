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
      {/* Process Controls */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Process Documents
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>{selectedFiles.length} files selected</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>{questionsOnly.length} questions</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                <span>{conditionsOnly.length} conditions</span>
              </span>
            </div>
          </div>
          <button
            onClick={handleProcessChecklist}
            disabled={processing || selectedFiles.length === 0 || questions.length === 0}
            className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {processing ? (
              <>
                <Clock className="h-5 w-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                <span>Start Processing</span>
              </>
            )}
          </button>
        </div>

        {/* Prerequisites Check */}
        {(selectedFiles.length === 0 || questions.length === 0) && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="text-sm text-yellow-800">
              <span className="font-medium">Prerequisites:</span>
              <ul className="mt-1 list-disc list-inside space-y-1">
                {selectedFiles.length === 0 && <li>Select at least one file from the sidebar</li>}
                {questions.length === 0 && <li>Add at least one question or condition</li>}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <X className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-red-800">Processing Error</h4>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Processing Status */}
      {processing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <Clock className="h-6 w-6 text-blue-500 animate-spin" />
            <div>
              <h4 className="text-sm font-medium text-blue-800">Processing Documents...</h4>
              <p className="text-sm text-blue-600 mt-1">
                Analyzing {selectedFiles.length} document{selectedFiles.length !== 1 ? 's' : ''} against {questions.length} criteria
              </p>
            </div>
          </div>
          <div className="mt-4 w-full bg-blue-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full animate-pulse w-2/3"></div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Success Header */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-6 w-6 text-green-500" />
              <div>
                <h4 className="text-sm font-medium text-green-800">Processing Complete</h4>
                <p className="text-sm text-green-600 mt-1">
                  Successfully analyzed documents and evaluated all criteria
                </p>
              </div>
            </div>
          </div>

          {/* Question Answers */}
          {Object.keys(result.question_answers).length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-blue-50 px-6 py-4 border-b border-blue-200">
                <h4 className="text-lg font-semibold text-blue-900 flex items-center space-x-2">
                  <span>📋</span>
                  <span>Question Answers</span>
                  <span className="text-sm bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                    {Object.keys(result.question_answers).length}
                  </span>
                </h4>
              </div>
              <div className="p-6 space-y-6 max-h-96 overflow-y-auto">
                {Object.entries(result.question_answers).map(([question, answer], index) => (
                  <div key={index} className="border-l-4 border-blue-400 pl-4 bg-blue-50 rounded-r-lg p-4">
                    <div className="text-sm font-semibold text-gray-900 mb-3 flex items-start space-x-2">
                      <span className="flex-shrink-0 text-blue-600">Q{index + 1}:</span>
                      <span>{question}</span>
                    </div>
                    <div className="text-sm text-gray-700 bg-white p-4 rounded border border-blue-200">
                      <span className="text-blue-600 font-medium">Answer:</span> {answer}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Condition Evaluations */}
          {Object.keys(result.condition_evaluations).length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-green-50 px-6 py-4 border-b border-green-200">
                <h4 className="text-lg font-semibold text-green-900 flex items-center space-x-2">
                  <span>✅</span>
                  <span>Condition Evaluations</span>
                  <span className="text-sm bg-green-100 text-green-700 px-2 py-1 rounded-full">
                    {Object.keys(result.condition_evaluations).length}
                  </span>
                </h4>
              </div>
              <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
                {Object.entries(result.condition_evaluations).map(([condition, evaluation], index) => (
                  <div key={index} className={`p-4 rounded-lg border-l-4 ${
                    evaluation 
                      ? 'bg-green-50 border-green-400' 
                      : 'bg-red-50 border-red-400'
                  }`}>
                    <div className="flex items-start space-x-3">
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
                        <div className="text-sm text-gray-900 mb-2">{condition}</div>
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          evaluation 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {evaluation ? '✓ SATISFIED' : '✗ NOT SATISFIED'}
                        </div>
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
      {!result && !processing && !error && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center space-x-2">
            <span>💡</span>
            <span>How to use the Checklist Processor:</span>
          </h4>
          <ol className="text-sm text-gray-600 space-y-2 list-decimal list-inside">
            <li>Upload PDF documents using the sidebar upload area</li>
            <li>Select the files you want to analyze by clicking the checkbox</li>
            <li>Add questions and conditions in the section above</li>
            <li>Click "Start Processing" to analyze documents against your criteria</li>
          </ol>
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <p className="text-xs text-blue-700">
              <strong>Tip:</strong> Questions will be answered with detailed responses, while conditions will be evaluated as true/false.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}