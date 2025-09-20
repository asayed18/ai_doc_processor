'use client'

import { useState } from 'react'
import { Upload, File, Trash2 } from 'lucide-react'
import { FileInfo } from '@/types'
import { api } from '@/lib/api'

interface FileUploadProps {
  onUploadSuccess: () => void
  files: FileInfo[]
  selectedFiles: number[]
  onFileSelectionChange: (files: number[]) => void
}

export default function FileUpload({ 
  onUploadSuccess, 
  files, 
  selectedFiles, 
  onFileSelectionChange 
}: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [deletingFiles, setDeletingFiles] = useState<Set<number>>(new Set())

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    setUploadError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      await api.post('/api/v1/files/upload', formData)
      onUploadSuccess()
      // Reset file input
      event.target.value = ''
    } catch (error) {
      setUploadError('Upload failed: ' + (error as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const handleFileSelection = (fileId: number) => {
    if (selectedFiles.includes(fileId)) {
      onFileSelectionChange(selectedFiles.filter(id => id !== fileId))
    } else {
      onFileSelectionChange([...selectedFiles, fileId])
    }
  }

  const handleDeleteFile = async (fileId: number) => {
    if (!confirm('Are you sure you want to delete this file?')) {
      return
    }

    setDeletingFiles(prev => new Set(prev).add(fileId))
    
    try {
      await api.delete(`/api/v1/files/${fileId}`)
      
      // Remove from selected files if it was selected
      if (selectedFiles.includes(fileId)) {
        onFileSelectionChange(selectedFiles.filter(id => id !== fileId))
      }
      
      // Refresh the file list
      onUploadSuccess()
    } catch (error) {
      console.error('Failed to delete file:', error)
      alert('Failed to delete file: ' + (error as Error).message)
    } finally {
      setDeletingFiles(prev => {
        const newSet = new Set(prev)
        newSet.delete(fileId)
        return newSet
      })
    }
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <label htmlFor="file-upload" className="cursor-pointer">
            <span className="mt-2 block text-sm font-medium text-gray-900">
              {uploading ? 'Uploading...' : 'Upload PDF documents'}
            </span>
            <input
              id="file-upload"
              name="file-upload"
              type="file"
              accept=".pdf"
              className="sr-only"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
        </div>
      </div>

      {uploadError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-sm text-red-600">{uploadError}</div>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-900">Uploaded Files</h3>
          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 min-w-0"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <label className="flex items-center cursor-pointer mr-2">
                    <input
                      type="checkbox"
                      checked={selectedFiles.includes(file.id)}
                      onChange={() => handleFileSelection(file.id)}
                      aria-label={`Select ${file.original_filename}`}
                      className="h-5 w-5 text-blue-600 bg-white border-2 border-gray-300 rounded-md focus:ring-blue-500 focus:ring-2 focus:ring-offset-1 hover:border-blue-400 transition-colors"
                    />
                  </label>
                  <File className="h-5 w-5 text-blue-500 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium text-gray-900 truncate" title={file.original_filename}>
                      {file.original_filename}
                    </div>
                    <div className="text-xs text-gray-500 whitespace-nowrap">
                      {new Date(file.upload_date).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2 ml-2">
                  <button
                    onClick={() => handleDeleteFile(file.id)}
                    disabled={deletingFiles.has(file.id)}
                    className="flex items-center space-x-1 px-2 py-1 rounded text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Delete file"
                  >
                    <Trash2 className="h-4 w-4" />
                    {deletingFiles.has(file.id) && (
                      <span className="text-xs">Deleting...</span>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
          {selectedFiles.length > 0 && (
            <div className="text-sm text-blue-600">
              {selectedFiles.length} file(s) selected for processing
            </div>
          )}
        </div>
      )}
    </div>
  )
}