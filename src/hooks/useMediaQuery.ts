import { useCallback, useSyncExternalStore } from 'react'

export function useMediaQuery(query: string): boolean {
  // React resubscribes whenever this function changes, so keep it stable.
  const subscribe = useCallback(
    (onChange: () => void) => {
      const list = window.matchMedia(query)
      list.addEventListener('change', onChange)
      return () => list.removeEventListener('change', onChange)
    },
    [query],
  )

  return useSyncExternalStore(subscribe, () => window.matchMedia(query).matches)
}
