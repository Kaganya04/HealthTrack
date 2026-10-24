async function request(url, options = {}) {
  const response = await fetch(url, options)
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = body?.detail
    const message = Array.isArray(detail)
      ? detail.map(item => item.msg).join('; ')
      : typeof detail === 'string' ? detail : 'Request failed. Try again.'
    throw new Error(message)
  }
  return body
}

export function saveSymptom(entry) {
  return request('/api/symptoms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  })
}

export function getSymptoms(startDate, endDate) {
  const query = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  })
  return request(`/api/symptoms?${query}`)
}


export function getSummary(startDate, endDate) {
  const query = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  })
  return request(`/api/summary?${query}`)
}