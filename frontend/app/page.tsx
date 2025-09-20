'use client'

import { useState, useEffect } from 'react'
import FileUpload from '@/components/FileUpload'
import QuestionManager from '@/components/QuestionManager'
import ChecklistProcessor from '@/components/ChecklistProcessor'
import { FileInfo, Question } from '@/types'
import { api, API_BASE_URL } from '@/lib/api'

export default function Home() {
  const [mounted, setMounted] = useState(false)
  const [files, setFiles] = useState<FileInfo[]>([])
  const [questions, setQuestions] = useState<Question[]>([])
  const [selectedFiles, setSelectedFiles] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
    <div className="space-y-8">
      {/* Debug Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800">Debug Information</h3>
        <div className="mt-2 text-sm text-blue-700">
          <p>Backend: {error ? '❌ Disconnected' : '✅ Connected'}</p>
          <p>Files loaded: {files.length}</p>
          <p>Questions loaded: {questions.length}</p>
          <p>Selected files: {selectedFiles.length}</p>
          <p>Loading: {loading ? 'Yes' : 'No'}</p>
        </div>
        <button
          onClick={testBackendConnection}
          disabled={loading}
          className="mt-2 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Testing...' : 'Test Backend Connection'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-red-800">Connection Error</h3>
          <p className="mt-2 text-sm text-red-700">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading data...</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* File Upload Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Document Upload</h2>
          <FileUpload 
            onUploadSuccess={fetchFiles}
            files={files}
            selectedFiles={selectedFiles}
            onFileSelectionChange={setSelectedFiles}
          />
        </div>

        {/* Question Management Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Questions & Conditions</h2>
          <QuestionManager 
            questions={questions}
            onQuestionsChange={fetchQuestions}
          />
        </div>
      </div>

      {/* Checklist Processing Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Checklist Processing</h2>
        <ChecklistProcessor 
          questions={questions}
          selectedFiles={selectedFiles}
        />
      </div>
    </div>
  )
}