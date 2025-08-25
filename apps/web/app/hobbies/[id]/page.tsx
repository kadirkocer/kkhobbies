'use client'

import { Suspense, useEffect, useMemo, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { entriesAPI, searchAPI } from '@/lib/shared/client'
import { EntryListItem } from '@/lib/shared/types'
import { t } from '@/lib/i18n'

type Tab = 'entries' | 'library' | 'links'

function HobbyInner() {
  const { id } = useParams<{id: string}>()
  const hobbyId = Number(id)
  const router = useRouter()
  const params = useSearchParams()
  const tab = (params.get('tab') as Tab) || 'entries'
  const [items, setItems] = useState<EntryListItem[]>([])
  const [loading, setLoading] = useState(false)

  // Forms state
  const [book, setBook] = useState({ title: '', author: '', isbn: '', publisher: '', year: '', cover_url: '', link: '', rating: '', notes: '', tags: '' })
  const [bookmark, setBookmark] = useState({ url: '', title: '', notes: '', tags: '' })
  const [brand, setBrand] = useState({ brand: '', url: '', category: '', notes: '', tags: '' })

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab])

  async function load() {
    setLoading(true)
    try {
      const base: any = { hobby_id: hobbyId, include_descendants: false }
      if (tab === 'library') base.type_key = 'book'
      if (tab === 'links') base.type_key = undefined // fetch both bookmark + brand_link
      const res = await searchAPI.search({ q: '*', ...base })
      const list = tab === 'links' ? res.items.filter(i => i.type_key === 'bookmark' || i.type_key === 'brand_link') : res.items
      setItems(list)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const setTab = (t: Tab) => {
    const sp = new URLSearchParams(params.toString())
    sp.set('tab', t)
    router.push(`/hobbies/${hobbyId}?${sp.toString()}`)
  }

  async function createBook(e: React.FormEvent) {
    e.preventDefault()
    const entry = await entriesAPI.createEntry({ hobby_id: hobbyId, type_key: 'book', title: book.title, description: book.notes, tags: book.tags })
    const props = [
      { key: 'author', value_text: book.author },
      { key: 'isbn', value_text: book.isbn },
      { key: 'publisher', value_text: book.publisher },
      { key: 'year', value_text: book.year },
      { key: 'cover_url', value_text: book.cover_url },
      { key: 'link', value_text: book.link },
      { key: 'rating', value_text: book.rating },
    ]
    await entriesAPI.updateEntryProps(entry.id, { props })
    setBook({ title: '', author: '', isbn: '', publisher: '', year: '', cover_url: '', link: '', rating: '', notes: '', tags: '' })
    load()
  }

  async function createBookmark(e: React.FormEvent) {
    e.preventDefault()
    const entry = await entriesAPI.createEntry({ hobby_id: hobbyId, type_key: 'bookmark', title: bookmark.title, description: bookmark.notes, tags: bookmark.tags })
    const props = [
      { key: 'url', value_text: bookmark.url },
      { key: 'title', value_text: bookmark.title },
      { key: 'notes', value_text: bookmark.notes },
    ]
    await entriesAPI.updateEntryProps(entry.id, { props })
    setBookmark({ url: '', title: '', notes: '', tags: '' })
    load()
  }

  async function createBrand(e: React.FormEvent) {
    e.preventDefault()
    const entry = await entriesAPI.createEntry({ hobby_id: hobbyId, type_key: 'brand_link', title: brand.brand, description: brand.notes, tags: brand.tags })
    const props = [
      { key: 'brand', value_text: brand.brand },
      { key: 'url', value_text: brand.url },
      { key: 'category', value_text: brand.category },
      { key: 'notes', value_text: brand.notes },
    ]
    await entriesAPI.updateEntryProps(entry.id, { props })
    setBrand({ brand: '', url: '', category: '', notes: '', tags: '' })
    load()
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <button onClick={()=>setTab('entries')} className={`px-3 py-1 rounded ${tab==='entries'?'bg-blue-600':'bg-gray-800'}`}>{t('tabs.entries')}</button>
          <button onClick={()=>setTab('library')} className={`px-3 py-1 rounded ${tab==='library'?'bg-blue-600':'bg-gray-800'}`}>{t('tabs.library')}</button>
          <button onClick={()=>setTab('links')} className={`px-3 py-1 rounded ${tab==='links'?'bg-blue-600':'bg-gray-800'}`}>{t('tabs.links')}</button>
        </div>

        {tab === 'entries' && (
          <div>
            {loading ? <div>...</div> : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {items.map(e => (
                  <div key={e.id} className="bg-gray-800 p-4 rounded">
                    <div className="text-sm text-gray-400">{e.type_key}</div>
                    <div className="font-semibold">{e.title || '—'}</div>
                    {e.tags && <div className="text-xs text-blue-400 mt-1">{e.tags}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'library' && (
          <div className="space-y-4">
            <form onSubmit={createBook} className="bg-gray-800 p-4 rounded grid md:grid-cols-3 gap-3">
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Başlık" value={book.title} onChange={e=>setBook({...book, title:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Yazar" value={book.author} onChange={e=>setBook({...book, author:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="ISBN" value={book.isbn} onChange={e=>setBook({...book, isbn:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Yayınevi" value={book.publisher} onChange={e=>setBook({...book, publisher:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Yıl" value={book.year} onChange={e=>setBook({...book, year:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Kapak URL" value={book.cover_url} onChange={e=>setBook({...book, cover_url:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Link" value={book.link} onChange={e=>setBook({...book, link:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Puan" value={book.rating} onChange={e=>setBook({...book, rating:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1 md:col-span-2" placeholder="Etiketler (virgülle)" value={book.tags} onChange={e=>setBook({...book, tags:e.target.value})} />
              <button className="px-3 py-1 bg-blue-600 rounded">{t('book.add')}</button>
            </form>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {items.map(e => (
                <div key={e.id} className="bg-gray-800 p-4 rounded">
                  <div className="text-sm text-gray-400">{e.type_key}</div>
                  <div className="font-semibold">{e.title || '—'}</div>
                  {e.tags && <div className="text-xs text-blue-400 mt-1">{e.tags}</div>}
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'links' && (
          <div className="space-y-6">
            <form onSubmit={createBookmark} className="bg-gray-800 p-4 rounded grid md:grid-cols-3 gap-3">
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="URL" value={bookmark.url} onChange={e=>setBookmark({...bookmark, url:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Başlık" value={bookmark.title} onChange={e=>setBookmark({...bookmark, title:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1 md:col-span-2" placeholder="Etiketler (virgülle)" value={bookmark.tags} onChange={e=>setBookmark({...bookmark, tags:e.target.value})} />
              <button className="px-3 py-1 bg-blue-600 rounded">{t('bookmark.add')}</button>
            </form>
            <form onSubmit={createBrand} className="bg-gray-800 p-4 rounded grid md:grid-cols-4 gap-3">
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Marka" value={brand.brand} onChange={e=>setBrand({...brand, brand:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="URL" value={brand.url} onChange={e=>setBrand({...brand, url:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1" placeholder="Kategori" value={brand.category} onChange={e=>setBrand({...brand, category:e.target.value})} />
              <input className="bg-gray-900 border border-gray-700 rounded px-2 py-1 md:col-span-2" placeholder="Etiketler (virgülle)" value={brand.tags} onChange={e=>setBrand({...brand, tags:e.target.value})} />
              <button className="px-3 py-1 bg-blue-600 rounded">{t('brandlink.add')}</button>
            </form>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {items.map(e => (
                <div key={e.id} className="bg-gray-800 p-4 rounded">
                  <div className="text-sm text-gray-400">{e.type_key}</div>
                  <div className="font-semibold">{e.title || '—'}</div>
                  {e.tags && <div className="text-xs text-blue-400 mt-1">{e.tags}</div>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function HobbyPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-900 text-white p-6">...</div>}>
      <HobbyInner />
    </Suspense>
  )
}
