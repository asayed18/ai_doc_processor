'use client'

import { useState } from 'react'
import { Upload, File, Check } from 'lucide-react'
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
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center space-x-3">
                  <File className="h-5 w-5 text-blue-500" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {file.filename}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(file.upload_date).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleFileSelection(file.id)}
                  className={`flex items-center space-x-1 px-3 py-1 rounded text-sm ${
                    selectedFiles.includes(file.id)
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {selectedFiles.includes(file.id) && (
                    <Check className="h-4 w-4" />
                  )}
                  <span>
                    {selectedFiles.includes(file.id) ? 'Selected' : 'Select'}
                  </span>
                </button>
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