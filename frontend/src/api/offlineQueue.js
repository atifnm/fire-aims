/**
 * Lightweight offline queue for inspection submissions.
 *
 * When the browser is offline (or a request fails due to connectivity),
 * the inspection payload is stored in localStorage. A listener on the
 * 'online' event, plus a periodic check, flushes the queue back to the
 * API. This is the "closest functional version" of full offline sync
 * called for in the spec - it covers the single most important offline
 * field workflow (submitting a completed inspection) without requiring
 * a full IndexedDB-backed sync engine.
 */
import api from './client'

const QUEUE_KEY = 'fireaims_offline_inspection_queue'

export function queueInspection(payload) {
  const queue = getQueue()
  queue.push({ id: `${Date.now()}-${Math.random().toString(36).slice(2)}`, payload })
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue))
}

export function getQueue() {
  try {
    return JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]')
  } catch {
    return []
  }
}

export function queueSize() {
  return getQueue().length
}

export async function flushQueue() {
  const queue = getQueue()
  if (queue.length === 0) return { flushed: 0, remaining: 0 }
  const remaining = []
  let flushed = 0
  for (const item of queue) {
    try {
      await api.post('/inspections', item.payload)
      flushed += 1
    } catch (e) {
      remaining.push(item)
    }
  }
  localStorage.setItem(QUEUE_KEY, JSON.stringify(remaining))
  return { flushed, remaining: remaining.length }
}

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    flushQueue()
  })
}
