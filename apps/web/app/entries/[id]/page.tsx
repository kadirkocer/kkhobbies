'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Upload, X, Save } from 'lucide-react'
import { entriesAPI, hobbyTypesAPI } from '@/lib/shared/client'
import { Entry, EntryProp, EntryMedia, HobbyType } from '@/lib/shared/types'
import Link from 'next/link'

export default function EntryDetailPage() {
  const params = useParams()
  const router = useRouter()
  const entryId = parseInt(params.id as string)

  const [entry, setEntry] = useState<Entry | null>(null)
  const [props, setProps] = useState<EntryProp[]>([])
  const [media, setMedia] = useState<EntryMedia[]>([])
  const [hobbyType, setHobbyType] = useState<HobbyType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isEditingProps, setIsEditingProps] = useState(false)
  const [isEditingDetails, setIsEditingDetails] = useState(false)
  const [propValues, setPropValues] = useState<Record<string, string>>({})
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [editTags, setEditTags] = useState('')
  const [actionError, setActionError] = useState('')

  useEffect(() => {
    if (entryId) {
      loadEntry()
    }
  }, [entryId])

  const loadEntry = async () => {
    setIsLoading(true)
    try {
      const [entryData, propsData, mediaData] = await Promise.all([
        entriesAPI.getEntry(entryId),
        entriesAPI.getEntryProps(entryId),
        entriesAPI.getEntryMedia(entryId)
      ])
      
      setEntry(entryData)
      setProps(propsData)
      setMedia(mediaData)
      // Prefill editable details
      setEditTitle(entryData.title || '')
      setEditDescription(entryData.description || '')
      setEditTags(entryData.tags || '')

      // Load hobby type schema
      if (entryData.type_key) {
        const hobbyTypes = await hobbyTypesAPI.getHobbyTypes()
        const type = hobbyTypes.find(t => t.key === entryData.type_key)
        if (type) {
          setHobbyType(type)
        }
      }

      // Initialize prop values
      const values: Record<string, string> = {}
      propsData.forEach(prop => {
        values[prop.key] = prop.value_text || ''
      })
      setPropValues(values)
    } catch (error) {
      console.error('Failed to load entry:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      await entriesAPI.uploadMedia(entryId, file)
      await loadEntry() // Reload to get updated media
    } catch (error) {
      console.error('Failed to upload file:', error)
    }
  }

  const handleDeleteMedia = async (mediaId: number) => {
    try {
      await entriesAPI.deleteMedia(entryId, mediaId)
      await loadEntry() // Reload to get updated media
    } catch (error) {
      console.error('Failed to delete media:', error)
    }
  }

  const handleSaveProps = async () => {
    try {
      const propsToSave = Object.entries(propValues).map(([key, value]) => ({
        key,
        value_text: value
      }))
      
      await entriesAPI.setEntryProps(entryId, propsToSave)
      setIsEditingProps(false)
      await loadEntry() // Reload to get updated props
    } catch (error) {
      console.error('Failed to save props:', error)
      setActionError('Failed to save properties')
    }
  }

  const handleSaveDetails = async () => {
    setActionError('')
    try {
      await entriesAPI.updateEntry(entryId, {
        title: editTitle || undefined,
        description: editDescription || undefined,
        tags: editTags || undefined,
      })
      setIsEditingDetails(false)
      await loadEntry()
    } catch (error) {
      console.error('Failed to save details:', error)
      setActionError('Failed to save entry details')
    }
  }

  const handleDeleteEntry = async () => {
    if (!confirm('Delete this entry? This cannot be undone.')) return
    setActionError('')
    try {
      await entriesAPI.deleteEntry(entryId)
      router.push('/entries')
    } catch (error) {
      console.error('Failed to delete entry:', error)
      setActionError('Failed to delete entry')
    }
  }

  const renderPropertyForm = () => {
    if (!hobbyType?.schema_json) return null

    try {
      const schema = JSON.parse(hobbyType.schema_json)
      const properties = schema.properties || {}

      return (
        <div className="space-y-4">
          {Object.entries(properties).map(([key, propSchema]: [string, any]) => (
            <div key={key}>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                {propSchema.title || key}
              </label>
              {propSchema.type === 'string' ? (
                <input
                  type="text"
                  value={propValues[key] || ''}
                  onChange={(e) => setPropValues(prev => ({
                    ...prev,
                    [key]: e.target.value
                  }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white"
                  placeholder={propSchema.description}
                />
              ) : propSchema.type === 'number' ? (
                <input
                  type="number"
                  value={propValues[key] || ''}
                  onChange={(e) => setPropValues(prev => ({
                    ...prev,
                    [key]: e.target.value
                  }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white"
                  placeholder={propSchema.description}
                />
              ) : (
                <input
                  type="text"
                  value={propValues[key] || ''}
                  onChange={(e) => setPropValues(prev => ({
                    ...prev,
                    [key]: e.target.value
                  }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white"
                  placeholder={propSchema.description}
                />
              )}
            </div>
          ))}
        </div>
      )
    } catch (error) {
      console.error('Failed to parse schema:', error)
      return <div className="text-red-400">Invalid schema format</div>
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (!entry) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Entry not found</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Link
              href="/entries"
              className="flex items-center gap-2 text-gray-400 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Entries
            </Link>
            <h1 className="text-2xl font-bold text-white">
              {entry.title || 'Untitled Entry'}
            </h1>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Entry Details */}
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Details</h2>
                {isEditingDetails ? (
                  <div className="flex gap-2">
                    <button
                      onClick={handleSaveDetails}
                      className="px-2 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setIsEditingDetails(false)
                        setEditTitle(entry.title || '')
                        setEditDescription(entry.description || '')
                        setEditTags(entry.tags || '')
                      }}
                      className="px-2 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => setIsEditingDetails(true)}
                      className="px-2 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                    >
                      Edit
                    </button>
                    <button
                      onClick={handleDeleteEntry}
                      className="px-2 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>

              {actionError && (
                <div className="mb-3 p-2 rounded bg-red-900/50 text-red-300 text-sm">{actionError}</div>
              )}

              {isEditingDetails ? (
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-400">Title</label>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Description</label>
                    <textarea
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                      rows={4}
                      className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Tags</label>
                    <input
                      type="text"
                      value={editTags}
                      onChange={(e) => setEditTags(e.target.value)}
                      placeholder="Comma-separated tags"
                      className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Type</label>
                    <p className="text-white">{entry.type_key}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Created</label>
                    <p className="text-white">{new Date(entry.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-400">Title</label>
                    <p className="text-white">{entry.title || 'No title'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Description</label>
                    <p className="text-white">{entry.description || 'No description'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Type</label>
                    <p className="text-white">{entry.type_key}</p>
                  </div>
                  {entry.tags && (
                    <div>
                      <label className="text-sm text-gray-400">Tags</label>
                      <p className="text-white">{entry.tags}</p>
                    </div>
                  )}
                  <div>
                    <label className="text-sm text-gray-400">Created</label>
                    <p className="text-white">{new Date(entry.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Media Gallery */}
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Media</h2>
                <div>
                  <input
                    type="file"
                    id="media-upload"
                    className="hidden"
                    onChange={handleFileUpload}
                    accept="image/*,video/*,audio/*,.pdf"
                  />
                  <label
                    htmlFor="media-upload"
                    className="flex items-center gap-2 px-3 py-1 bg-blue-600 text-white rounded text-sm cursor-pointer hover:bg-blue-700"
                  >
                    <Upload className="w-4 h-4" />
                    Upload
                  </label>
                </div>
              </div>

              {media.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  No media files. Upload some to get started!
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {media.map(item => (
                    <div key={item.id} className="relative group">
                      <div className="aspect-square bg-gray-700 rounded overflow-hidden">
                        {item.kind === 'image' ? (
                          <img
                            src={item.file_path}
                            alt="Media"
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-gray-400">
                            <span className="text-xs">{item.kind?.toUpperCase()}</span>
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleDeleteMedia(item.id)}
                        className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Properties Sidebar */}
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Properties</h2>
                {isEditingProps ? (
                  <div className="flex gap-2">
                    <button
                      onClick={handleSaveProps}
                      className="flex items-center gap-1 px-2 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                    >
                      <Save className="w-3 h-3" />
                      Save
                    </button>
                    <button
                      onClick={() => setIsEditingProps(false)}
                      className="px-2 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setIsEditingProps(true)}
                    className="px-2 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                  >
                    Edit
                  </button>
                )}
              </div>

              {isEditingProps ? (
                renderPropertyForm()
              ) : props.length === 0 ? (
                <div className="text-gray-400 text-sm">No properties set</div>
              ) : (
                <div className="space-y-3">
                  {props.map(prop => (
                    <div key={prop.id}>
                      <label className="text-sm text-gray-400">{prop.key}</label>
                      <p className="text-white">{prop.value_text || 'No value'}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
