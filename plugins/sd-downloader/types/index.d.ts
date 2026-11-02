// Valeurs du bandeau de lancement (hooks/register.tsx).
export type Lang = string

declare module 'claude-code' {
  interface PluginState {
    'sd-downloader': {
      /** Réglage fait (config écrite ou vérifiée par djdl). */
      isReady: boolean
      /** Langue choisie au réglage (fr, en, es, it…), vide tant qu'inconnue. */
      lang: Lang
      /** Bandeau masqué pour cette session. */
      isHidden: boolean
    }
  }
}
