'use client'

import { useEffect, useState } from 'react'
import { usersAPI } from '@/lib/shared/client'
import { t } from '@/lib/i18n'

export default function SettingsPage() {
  const [name, setName] = useState('')
  const [bio, setBio] = useState('')
  const [avatarPreview, setAvatarPreview] = useState<string>('')
  const [theme, setTheme] = useState<'dark'|'light'>('dark')
  const [lang] = useState<'tr'>('tr')
  const [toast, setToast] = useState<string>('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    (async () => {
      try {
        const me = await usersAPI.getCurrentUser()
        setName(me.name || '')
        setBio(me.bio || '')
        if (me.avatar_path) setAvatarPreview(me.avatar_path)
        const savedTheme = (localStorage.getItem('theme') as 'dark'|'light') || 'dark'
        setTheme(savedTheme)
        if (savedTheme === 'dark') document.documentElement.classList.add('dark')
        else document.documentElement.classList.remove('dark')
      } catch {}
    })()
  }, [])

  const save = async () => {
    setSaving(true)
    try {
      await usersAPI.updateCurrentUser({ name, bio })
      setToast(t('toast.saved'))
      setTimeout(() => setToast(''), 2000)
    } catch {
      setToast(t('toast.error'))
      setTimeout(() => setToast(''), 2000)
    } finally {
      setSaving(false)
    }
  }

  const onAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const updated = await usersAPI.uploadAvatar(file)
      if (updated.avatar_path) setAvatarPreview(updated.avatar_path)
      setToast(t('toast.saved'))
      setTimeout(() => setToast(''), 2000)
    } catch {
      setToast(t('toast.error'))
      setTimeout(() => setToast(''), 2000)
    }
  }

  const toggleTheme = (next: 'dark'|'light') => {
    setTheme(next)
    localStorage.setItem('theme', next)
    if (next === 'dark') document.documentElement.classList.add('dark')
    else document.documentElement.classList.remove('dark')
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold">{t('settings.title')}</h1>

        {toast && (
          <div className="p-2 rounded bg-green-700/30 text-green-300 text-sm">{toast}</div>
        )}

        <section className="bg-gray-800 rounded-lg p-4 space-y-4">
          <h2 className="font-semibold">{t('settings.profile')}</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-1">{t('settings.name')}</label>
              <input value={name} onChange={(e)=>setName(e.target.value)} className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded" />
            </div>
            <div>
              <label className="block text-sm mb-1">{t('settings.avatar')}</label>
              <div className="flex items-center gap-3">
                {avatarPreview && <img src={avatarPreview} className="w-12 h-12 rounded-full object-cover" alt="avatar" />}
                <input type="file" accept="image/*" onChange={onAvatarChange} />
              </div>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm mb-1">{t('settings.bio')}</label>
              <textarea value={bio} onChange={(e)=>setBio(e.target.value)} rows={4} className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded" />
            </div>
          </div>
          <div className="flex justify-end">
            <button onClick={save} disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50">
              {t('button.save')}
            </button>
          </div>
        </section>

        <section className="bg-gray-800 rounded-lg p-4 space-y-3">
          <h2 className="font-semibold">{t('settings.theme')}</h2>
          <div className="flex gap-3">
            <button onClick={()=>toggleTheme('dark')} className={`px-3 py-1 rounded ${theme==='dark'?'bg-blue-600':'bg-gray-700'}`}>{t('settings.theme.dark')}</button>
            <button onClick={()=>toggleTheme('light')} className={`px-3 py-1 rounded ${theme==='light'?'bg-blue-600':'bg-gray-700'}`}>{t('settings.theme.light')}</button>
          </div>
        </section>

        <section className="bg-gray-800 rounded-lg p-4">
          <h2 className="font-semibold">{t('settings.language')}</h2>
          <div className="mt-2">{t('settings.language.tr')}</div>
        </section>
      </div>
    </div>
  )
}

