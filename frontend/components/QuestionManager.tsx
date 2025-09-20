'use client'

import { useState } from 'react'
import { Plus, Trash2, MessageCircle, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { Question, QuestionCreate } from '@/types'
import { api } from '@/lib/api'

interface QuestionManagerProps {
  questions: Question[]
  onQuestionsChange: () => void
  isExpanded?: boolean
  onToggleExpanded?: () => void
}

export default function QuestionManager({ 
  questions, 
  onQuestionsChange, 
  isExpanded = true, 
  onToggleExpanded 
}: QuestionManagerProps) {
  const [newQuestion, setNewQuestion] = useState('')
  const [questionType, setQuestionType] = useState<'question' | 'condition'>('question')
  const [adding, setAdding] = useState(false)
  const [activeTab, setActiveTab] = useState<'questions' | 'conditions' | 'all'>('all')

  const handleAddQuestion = async () => {
    if (!newQuestion.trim()) return

    setAdding(true)
    try {
      await api.post('/api/v1/questions', {
        text: newQuestion.trim(),
        type: questionType,
      })
      
      setNewQuestion('')
      onQuestionsChange()
    } catch (error) {
      console.error('Failed to add question:', error)
    } finally {
      setAdding(false)
    }
  }

  const handleDeleteQuestion = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return
    
    try {
      await api.delete(`/api/v1/questions/${id}`)
      onQuestionsChange()
    } catch (error) {
      console.error('Failed to delete question:', error)
    }
  }

  const questionsOnly = questions.filter(q => q.type === 'question')
  const conditionsOnly = questions.filter(q => q.type === 'condition')

  const getDisplayedItems = () => {
    switch (activeTab) {
      case 'questions':
        return questionsOnly
      case 'conditions':
        return conditionsOnly
      default:
        return questions
    }
  }

  return (
    <div className="space-y-6">
      {/* Collapsible Content */}
      {isExpanded && (
        <div className="space-y-6">
          {/* Add New Item */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-4">
            <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">Add New Item</h3>
          <div className="flex space-x-1">
            <button
              onClick={() => setQuestionType('question')}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                questionType === 'question'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              Question
            </button>
            <button
              onClick={() => setQuestionType('condition')}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                questionType === 'condition'
                  ? 'bg-blue-300 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              Condition
            </button>
          </div>
        </div>

        <div className="flex space-x-2">
          <input
            type="text"
            value={newQuestion}
            onChange={(e) => setNewQuestion(e.target.value)}
            placeholder={`Enter a ${questionType} to evaluate...`}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            onKeyPress={(e) => e.key === 'Enter' && handleAddQuestion()}
          />
          <button
            onClick={handleAddQuestion}
            disabled={adding || !newQuestion.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1 text-sm"
          >
            <Plus className="h-4 w-4" />
            <span>{adding ? 'Adding...' : 'Add'}</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('all')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'all'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            All ({questions.length})
          </button>
          <button
            onClick={() => setActiveTab('questions')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'questions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Questions ({questionsOnly.length})
          </button>
          <button
            onClick={() => setActiveTab('conditions')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'conditions'
                ? 'border-blue-300 text-blue-500'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Conditions ({conditionsOnly.length})
          </button>
        </nav>
      </div>

      {/* Items List */}
      <div className="space-y-1.5 max-h-96 overflow-y-auto">
        {getDisplayedItems().length > 0 ? (
          getDisplayedItems().map((item) => (
            <div
              key={item.id}
              className={`group mx-6 p-4 rounded-lg border-2 transition-colors hover:shadow-sm bg-white ${
                item.type === 'question'
                  ? 'border-blue-400 hover:border-blue-500'
                  : 'border-blue-200 hover:border-blue-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    {item.type === 'question' ? (
                      <MessageCircle className="h-4 w-4 text-blue-500 flex-shrink-0" />
                    ) : (
                      <CheckCircle className="h-4 w-4 text-blue-400 flex-shrink-0" />
                    )}
                    <span className={`text-xs font-medium px-2 py-1 rounded-full border ${
                      item.type === 'question'
                        ? 'border-blue-400 text-blue-700 bg-blue-50'
                        : 'border-blue-200 text-blue-600 bg-blue-50 bg-opacity-50'
                    }`}>
                      {item.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-900 leading-relaxed">{item.text}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Added: {new Date(item.created_date).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteQuestion(item.id)}
                  className="ml-3 p-1 text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Delete item"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 text-gray-500">
            <div className="mb-3">
              {activeTab === 'questions' ? (
                <MessageCircle className="h-8 w-8 text-gray-300 mx-auto" />
              ) : activeTab === 'conditions' ? (
                <CheckCircle className="h-8 w-8 text-gray-300 mx-auto" />
              ) : (
                <div className="flex justify-center space-x-1">
                  <MessageCircle className="h-6 w-6 text-gray-300" />
                  <CheckCircle className="h-6 w-6 text-gray-300" />
                </div>
              )}
            </div>
            <p className="text-sm">
              {activeTab === 'all' 
                ? 'No questions or conditions yet'
                : `No ${activeTab} yet`
              }
            </p>
            <p className="text-xs text-gray-400 mt-1">Add some above to get started</p>
          </div>
        )}
      </div>
        </div>
      )}
    </div>
  )
}