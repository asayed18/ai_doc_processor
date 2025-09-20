'use client'

import { useState, useEffect } from 'react'
import FileUpload from '@/components/FileUpload'
import QuestionManager from '@/components/QuestionManager'
import ChecklistProcessor from '@/components/ChecklistProcessor'
import { FileInfo, Question } from '@/types'
import { api, API_BASE_URL } from '@/lib/api'
import { Menu, X, ChevronDown, ChevronUp } from 'lucide-react'

export default function Home() {
  const [mounted, setMounted] = useState(false)
  const [files, setFiles] = useState<FileInfo[]>([])
  const [questions, setQuestions] = useState<Question[]>([])
  const [selectedFiles, setSelectedFiles] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [questionsExpanded, setQuestionsExpanded] = useState(true)

  const fetchFiles = async () => {
    try {
      const data = await api.get('/api/v1/files')
      setFiles(data)
    } catch (error) {
      console.error('Failed to fetch files:', error)
      setError('Failed to connect to backend')
    }
  }

  const fetchQuestions = async () => {
    try {
      const data = await api.get('/api/v1/questions')
      setQuestions(data)
    } catch (error) {
      console.error('Failed to fetch questions:', error)
      setError('Failed to connect to backend')
    }
  }

  const testBackendConnection = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.get('/')
      console.log('Backend test response:', data)
      alert(`Backend response: ${data.message}`)
      
      // Also test debug endpoint
      const debugData = await api.get('/debug')
      console.log('Debug info:', debugData)
      
      await Promise.all([fetchFiles(), fetchQuestions()])
    } catch (error) {
      console.error('Backend test failed:', error)
      setError('Backend connection test failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted) {
      const loadData = async () => {
        setLoading(true)
        setError(null)
        await Promise.all([fetchFiles(), fetchQuestions()])
        setLoading(false)
      }
      loadData()
    }
  }, [mounted])

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className="space-y-8">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } fixed lg:static lg:translate-x-0 inset-y-0 left-0 z-50 w-80 bg-white shadow-lg border-r border-gray-200 flex flex-col transition-transform duration-300 ease-in-out`}>
        {/* Sidebar Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Document Management</h2>
              <p className="text-sm text-gray-600 mt-1">Upload and select files</p>
            </div>
            <button
              className="lg:hidden p-2 rounded-md hover:bg-gray-100"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close sidebar"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Debug Info - Compact */}
        <div className="px-6 py-3 bg-blue-50 border-b border-blue-100">
          <div className="flex items-center justify-between text-xs">
            <span className={`flex items-center ${error ? 'text-red-600' : 'text-green-600'}`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${error ? 'bg-red-500' : 'bg-green-500'}`}></div>
              {error ? 'Disconnected' : 'Connected'}
            </span>
            <span className="text-gray-600">{files.length} files, {selectedFiles.length} selected</span>
          </div>
          {error && (
            <div className="mt-2">
              <button 
                onClick={testBackendConnection}
                disabled={loading}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Testing...' : 'Reconnect'}
              </button>
            </div>
          )}
        </div>

        {/* Error Display - Compact */}
        {error && (
          <div className="px-6 py-3 bg-red-50 border-b border-red-100">
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}

        {/* File Upload Section */}
        <div className="flex-1 p-6 overflow-y-auto">
          <FileUpload 
            onUploadSuccess={fetchFiles}
            files={files}
            selectedFiles={selectedFiles}
            onFileSelectionChange={setSelectedFiles}
          />
        </div>

        {/* Selection Summary */}
        {selectedFiles.length > 0 && (
          <div className="p-6 border-t border-gray-200 bg-blue-50">
            <div className="text-sm text-blue-800 font-medium">
              {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected
            </div>
            <div className="text-xs text-blue-600 mt-1">
              Ready for processing
            </div>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Main Content Header */}
        <div className="p-6 border-b border-gray-200 bg-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                className="lg:hidden p-2 rounded-md hover:bg-gray-100"
                onClick={() => setSidebarOpen(true)}
                aria-label="Open sidebar"
              >
                <Menu className="h-5 w-5 text-gray-500" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Checklist</h1>
                <p className="text-gray-600 mt-1">Manage questions and process documents against compliance criteria</p>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading data...</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        {!loading && (
          <div className="flex-1 overflow-y-auto">
            <div className="p-6 space-y-8">
              {/* Question Management Section */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Questions & Conditions</h2>
                    <p className="text-sm text-gray-600 mt-1">Define criteria and questions for document evaluation</p>
                  </div>
                  <button
                    onClick={() => setQuestionsExpanded(!questionsExpanded)}
                    className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    <span>{questionsExpanded ? 'Collapse' : 'Expand'}</span>
                    {questionsExpanded ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </button>
                </div>
                <QuestionManager 
                  questions={questions}
                  onQuestionsChange={fetchQuestions}
                  isExpanded={questionsExpanded}
                  onToggleExpanded={() => setQuestionsExpanded(!questionsExpanded)}
                />
              </div>

              {/* Checklist Processing Section */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">AI Processing</h2>
                    <p className="text-sm text-gray-600 mt-1">Process selected documents against defined questions</p>
                  </div>
                  <div className="text-sm text-gray-500">
                    {selectedFiles.length > 0 ? `${selectedFiles.length} file${selectedFiles.length !== 1 ? 's' : ''} ready` : 'No files selected'}
                  </div>
                </div>
                {selectedFiles.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                    <div className="text-gray-400 text-lg mb-2">📄</div>
                    <p className="text-gray-600">Select files from the sidebar to begin processing</p>
                    <button
                      className="mt-2 text-sm text-blue-600 hover:text-blue-700 lg:hidden"
                      onClick={() => setSidebarOpen(true)}
                    >
                      Open file selector
                    </button>
                  </div>
                ) : (
                  <ChecklistProcessor 
                    questions={questions}
                    selectedFiles={selectedFiles}
                  />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}