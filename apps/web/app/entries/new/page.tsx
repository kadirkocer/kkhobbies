'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Save } from 'lucide-react'
import { entriesAPI, hobbiesAPI, hobbyTypesAPI } from '@/lib/shared/client'
import { Hobby, HobbyType } from '@/lib/shared/types'

export default function NewEntryPage() {
  const router = useRouter()

  const [hobbies, setHobbies] = useState<Hobby[]>([])
  const [hobbyTypes, setHobbyTypes] = useState<HobbyType[]>([])
  const [selectedHobbyId, setSelectedHobbyId] = useState<number>()
  const [selectedTypeKey, setSelectedTypeKey] = useState<string>('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const load = async () => {
      try {
        const [hobbiesData, typesData] = await Promise.all([
          hobbiesAPI.getHobbies(),
          hobbyTypesAPI.getHobbyTypes(),
        ])
        setHobbies(hobbiesData)
        setHobbyTypes(typesData)

        // Set sensible defaults if available
        const firstHobby = flattenHobbies(hobbiesData)[0]
        if (firstHobby && selectedHobbyId === undefined) {
          setSelectedHobbyId(firstHobby.id)
        }
        if (typesData.length > 0 && !selectedTypeKey) {
          setSelectedTypeKey(typesData[0].key)
        }
      } catch (e) {
        console.error('Failed to load form data', e)
        setError('Failed to load form data')
      }
    }
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const flattenedHobbies = useMemo(() => flattenHobbies(hobbies), [hobbies])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')

    if (!selectedHobbyId) {
      setError('Please select a hobby')
      return
    }
    if (!selectedTypeKey) {
      setError('Please select a type')
      return
    }

    setIsSubmitting(true)
    try {
      const created = await entriesAPI.createEntry({
        hobby_id: selectedHobbyId,
        type_key: selectedTypeKey,
        title: title || undefined,
        description: description || undefined,
        tags: tags || undefined,
      })
      router.push(`/entries/${created.id}`)
    } catch (e: any) {
      console.error('Failed to create entry', e)
      setError(e?.message || 'Failed to create entry')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-3xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <Link href="/entries" className="flex items-center gap-2 text-gray-400 hover:text-white">
            <ArrowLeft className="w-4 h-4" />
            Back to Entries
          </Link>
          <h1 className="text-2xl font-bold text-white">New Entry</h1>
        </div>

        <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-6 space-y-4">
          {error && (
            <div className="p-3 rounded bg-red-900/50 text-red-300 text-sm">{error}</div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Hobby</label>
              <select
                value={selectedHobbyId ?? ''}
                onChange={(e) => setSelectedHobbyId(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
              >
                <option value="" disabled>
                  Select a hobby
                </option>
                {flattenedHobbies.map(h => (
                  <option key={h.id} value={h.id}>
                    {h.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300 mb-1">Type</label>
              <select
                value={selectedTypeKey}
                onChange={(e) => setSelectedTypeKey(e.target.value)}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
              >
                {hobbyTypes.map(t => (
                  <option key={t.key} value={t.key}>
                    {t.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Optional title"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
              rows={4}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Tags</label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="Comma-separated tags"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting || !selectedHobbyId || !selectedTypeKey}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              Create Entry
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Helpers
function flattenHobbies(hobbies: Hobby[]): { id: number; label: string }[] {
  const out: { id: number; label: string }[] = []
  const walk = (list: Hobby[], prefix = '') => {
    for (const h of list) {
      out.push({ id: h.id, label: `${prefix}${h.name}` })
      const children = list.filter(x => x.parent_id === h.id)
      if (children.length > 0) {
        // In this dataset, children are separate items; indent
        walk(children, `${prefix}• `)
      }
    }
  }
  // Start from top-level
  const roots = hobbies.filter(h => !h.parent_id)
  walk(roots)
  return out
}

