'use client'

import { useState } from 'react'
import { Plus, Trash2, MessageCircle, CheckCircle } from 'lucide-react'
import { Question, QuestionCreate } from '@/types'

interface QuestionManagerProps {
  questions: Question[]
  onQuestionsChange: () => void
}

export default function QuestionManager({ questions, onQuestionsChange }: QuestionManagerProps) {
  const [newQuestion, setNewQuestion] = useState('')
  const [questionType, setQuestionType] = useState<'question' | 'condition'>('question')
  const [adding, setAdding] = useState(false)

  const handleAddQuestion = async () => {
    if (!newQuestion.trim()) return

    setAdding(true)
    try {
      const response = await fetch('http://localhost:8000/questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: newQuestion.trim(),
          type: questionType,
        }),
      })

      if (response.ok) {
        setNewQuestion('')
        onQuestionsChange()
      }
    } catch (error) {
      console.error('Failed to add question:', error)
    } finally {
      setAdding(false)
    }
  }

  const handleDeleteQuestion = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/questions/${id}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        onQuestionsChange()
      }
    } catch (error) {
      console.error('Failed to delete question:', error)
    }
  }

  const questionsOnly = questions.filter(q => q.type === 'question')
  const conditionsOnly = questions.filter(q => q.type === 'condition')

  return (
    <div className="space-y-6">
      {/* Add New Question/Condition */}
      <div className="space-y-3">
        <div className="flex space-x-2">
          <button
            onClick={() => setQuestionType('question')}
            className={`px-3 py-2 rounded text-sm ${
              questionType === 'question'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            Question
          </button>
          <button
            onClick={() => setQuestionType('condition')}
            className={`px-3 py-2 rounded text-sm ${
              questionType === 'condition'
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            Condition
          </button>
        </div>

        <div className="flex space-x-2">
          <input
            type="text"
            value={newQuestion}
            onChange={(e) => setNewQuestion(e.target.value)}
            placeholder={`Add a new ${questionType}...`}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && handleAddQuestion()}
          />
          <button
            onClick={handleAddQuestion}
            disabled={adding || !newQuestion.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
          >
            <Plus className="h-4 w-4" />
            <span>{adding ? 'Adding...' : 'Add'}</span>
          </button>
        </div>
      </div>

      {/* Questions Section */}
      {questionsOnly.length > 0 && (
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <MessageCircle className="h-5 w-5 text-blue-500" />
            <h3 className="text-lg font-medium text-gray-900">Questions</h3>
          </div>
          <div className="space-y-2">
            {questionsOnly.map((question) => (
              <div
                key={question.id}
                className="flex items-start justify-between p-3 bg-blue-50 rounded-lg"
              >
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{question.text}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Added: {new Date(question.created_date).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteQuestion(question.id)}
                  className="ml-2 p-1 text-red-500 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conditions Section */}
      {conditionsOnly.length > 0 && (
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <h3 className="text-lg font-medium text-gray-900">Conditions</h3>
          </div>
          <div className="space-y-2">
            {conditionsOnly.map((condition) => (
              <div
                key={condition.id}
                className="flex items-start justify-between p-3 bg-green-50 rounded-lg"
              >
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{condition.text}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Added: {new Date(condition.created_date).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteQuestion(condition.id)}
                  className="ml-2 p-1 text-red-500 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {questions.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No questions or conditions yet.</p>
          <p className="text-sm">Add some above to get started.</p>
        </div>
      )}
    </div>
  )
}