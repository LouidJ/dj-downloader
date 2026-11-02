// Bandeau au-dessus de la zone de saisie : un bouton lance le réglage, puis le téléchargement,
// sans taper de commande. Il apprend que le réglage est fait (et la langue) en regardant les
// commandes djdl du plugin, et le garde d'une session à l'autre ($.store).
import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

const isReady = atom({ plugin: 'sd-downloader', key: 'isReady' } as const, false)
const lang = atom({ plugin: 'sd-downloader', key: 'lang' } as const, '')
const isHidden = atom({ plugin: 'sd-downloader', key: 'isHidden' } as const, false)

type Labels = { setup: string; download: string; ask: string; hide: string; done: (n: number) => string }

const LABELS: Record<string, Labels> = {
  fr: { setup: '🎧 Installer SD Downloader', download: '🎧 Télécharger mes nouveaux likes', ask: 'mes nouveaux likes', hide: 'Masquer',
        done: n => `✅ Téléchargement terminé : ${n} son${n > 1 ? 's' : ''}` },
  en: { setup: '🎧 Set up SD Downloader', download: '🎧 Download my new likes', ask: 'my new likes', hide: 'Hide',
        done: n => `✅ Download finished: ${n} track${n > 1 ? 's' : ''}` },
  es: { setup: '🎧 Instalar SD Downloader', download: '🎧 Descargar mis nuevos likes', ask: 'mis nuevos likes', hide: 'Ocultar',
        done: n => `✅ Descarga terminada: ${n} tema${n > 1 ? 's' : ''}` },
  it: { setup: '🎧 Installa SD Downloader', download: '🎧 Scarica i miei nuovi like', ask: 'i miei nuovi like', hide: 'Nascondi',
        done: n => `✅ Download completato: ${n} bran${n > 1 ? 'i' : 'o'}` },
}
// Langue encore inconnue (avant le réglage) : un libellé que tout le monde comprend
const UNKNOWN: Labels = { setup: '🎧 SD Downloader : installer / set up', download: '🎧 SD Downloader', ask: 'new likes', hide: '✕',
  done: n => `✅ SD Downloader : ${n}` }

const DJDL = /djdl\.py/

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const ready = (await $.store.get('isReady')) === true
    const saved = await $.store.get('lang')
    await update($, isReady, () => ready)
    await update($, lang, () => (typeof saved === 'string' ? saved : ''))

    return next(e)
  })

  // Le réglage est fait quand djdl écrit la config (init) ou la trouve complète (check).
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    if (!DJDL.test(e.command) || ran.deny !== undefined || ran.isError === true) {
      return ran
    }
    const out = ran.result && 'stdout' in ran.result ? String(ran.result.stdout) : ''
    const isInit = /\binit\b/.test(e.command) && out.includes('Config écrite')
    const isCheckOk = /\bcheck\b/.test(e.command) && /(^|\n)OK\s*$/.test(out)
    if (isInit || isCheckOk) {
      await $.store.set('isReady', true)
      await update($, isReady, () => true)
    }
    // Fin d'un run : le bilan (report --last) → son « réussi » et notification avec le nombre de sons
    if (/\breport\b/.test(e.command) && /--last\b/.test(e.command) && out.startsWith('BILAN')) {
      const n = Number(out.match(/^\s*téléchargé\s+(\d+)/m)?.[1] ?? 0)
      const t = LABELS[await read($, lang)] ?? UNKNOWN
      $.ui.toast(t.done(n))
      await $.audio.play({ asset: 'sounds/done.wav' }).catch(() => undefined)
    }
    const chosen = e.command.match(/--language\s+"?([a-z]{2})/) ?? e.command.match(/\bconfig\s+language\s+"?([a-z]{2})/)
    if (chosen && (isInit || /\bconfig\b/.test(e.command))) {
      await $.store.set('lang', chosen[1])
      await update($, lang, () => chosen[1])
    }

    return ran
  }).catch(($, e, next) => next(e)) // il ne fait qu'observer : en cas d'erreur, la commande suit son cours

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || e.props.isWorking || (await read($, isHidden))) {
      return next(e)
    }
    const ready = await read($, isReady)
    const code = await read($, lang)
    const t = LABELS[code] ?? UNKNOWN
    const { Box, Button } = $.ui.resolve(e)

    return (
      <Box gap="md">
        <Button
          key="go"
          label={ready ? t.download : t.setup}
          onPress={async () => {
            // Prêt : télécharge directement les nouveaux likes, sans menu
            await $.command.run(ready ? { command: 'sd-downloader:download-likes', args: t.ask } : { command: 'sd-downloader:setup' })
          }}
        />
        <Button key="hide" label={t.hide} onPress={() => update($, isHidden, () => true)} />
      </Box>
    )
  })
}
