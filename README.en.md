# SD Downloader — download your SoundCloud likes and playlists automatically

**🇫🇷 Français : [README.md](README.md)** · Setup asks for your language: everything then happens in your language.

A free Claude plugin for DJs on Mac and Windows. You like tracks on SoundCloud, or put them in a playlist, and Claude downloads them for you:

- **direct SoundCloud download** when the artist allows it;
- **Hypeddit and Droploud gates**: follow, like, repost, comment, email… Claude does every step;
- **filing**: each file goes straight into your folder. For a zip, it keeps the best version (the cut you chose, WAV/AIFF before MP3) and throws away the rest. Extended, Radio or both: you choose during setup, or later ("keep the radio versions too"). Duplicates go to the trash;
- **report** at the end: what was downloaded, already there, skipped (long sets, duplicates) and what is missing, with the reason;
- **no duplicates**: before downloading, Claude looks in your folder and skips tracks you already have in the same version; the report tells you which file you had;
- **never the same track twice**: each track is tracked from one run to the next, even if it comes back in a playlist;
- **adapts**: if a site changes, Claude finds the new button, finishes, and notes the change for next time.

**Never used Claude?** Step-by-step guide, one question at a time: [louidj.github.io/dj-downloader](https://louidj.github.io/dj-downloader/). Text version: [GUIDE.en.md](GUIDE.en.md).

## What you need

- A Mac or a Windows PC, with Google Chrome.
- The Claude app (Cowork), with a paid Claude plan.
- The [**Claude in Chrome**](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) extension, signed in.
- Your SoundCloud account signed in to that Chrome. Claude reads your email and first name from it for the gates.

## Install

In the Claude app, main screen: **Customize → Plugins → Add**, marketplace `LouidJ/dj-downloader`, then install **SD Downloader**.

For every new task: add your **Downloads** folder and your music folder with **+ → Add folder**, then switch to **Auto** mode (bottom right, instead of **Manual**). For setup, type `/sd-downloader:setup`.

One question to click: your language. The browser, SoundCloud account, email and first name are found on their own. It never asks for a password: you sign in yourself. At the end, a button starts your first download.

With Claude Code (Code tab or terminal): `/plugin install sd-downloader --marketplace LouidJ/dj-downloader`, then the **🎧 Set up SD Downloader** button. Python 3 is needed (on Windows, from python.org, ticking "Add python.exe to PATH").

## Usage

Type "download my new likes" (with Claude Code: the **🎧 Download my new likes** button): Claude takes everything you've liked since last time, does the gates with your account (you agreed once during setup), files everything and gives you the report.

You can also say what you want in your own words, in any language:

| You say | Claude takes |
|---|---|
| "Download my new likes" | everything you liked since last time |
| "Download the last 20" | your last 20 likes |
| "Download what I liked today" | today's likes (also works with "yesterday", "since Monday", "since October 20") |
| "Download my playlist" | your "To download" playlist (offered after your first download) |
| "Download this playlist: <link>" | a whole playlist, even a private one with its private link |
| "Download these tracks: <links>" | the pasted tracks |

Or `/sd-downloader:download-likes last 20`.

**The easiest way to choose**: create a SoundCloud playlist "To download", public or private with its private link. Add tracks as you go, then say "download my playlist". Tracks already downloaded are never redone: no need to empty the playlist.

Afterwards:

- "remove #12 from the list": this track will never be offered again;
- "show the report";
- "try again tomorrow": for a track to retry later;
- "my download playlist is <link>": to change it;
- "ask me before the gates": Claude asks for your OK on every download again.

## Good to know

- Droploud gates sometimes require signing up for the artist's news to give you the track: Claude ticks the box, as you would.
- Optional: at the end of setup, Claude offers once to follow the plugin's author on SoundCloud. It only follows if you say yes, and asks nothing if you already follow.
- No limit: take 5 tracks or 500, Claude goes all the way. If SoundCloud blocks a direct download (SoundCloud's own limit), Claude goes straight through the Hypeddit / Droploud gate when there is one.
- Beatport, Bandcamp and other paid stores are never touched: those tracks are listed as missing.
- Your settings and tracking stay on your computer (`~/.claude/plugins/data/`). They are deleted if you uninstall the plugin. Your audio files stay in your folder.
- Respect the artists: only download what they offer for free.

MIT License.
