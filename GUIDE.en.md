# First steps: you've never used Claude

*[Version française](GUIDE.md) · Interactive guide, one question at a time: [open](https://louidj.github.io/dj-downloader/)*

Setup takes about 20 minutes, one time only. After that, it's one sentence each time. No code to write.

## 0. What you need

- A **Mac** or a **Windows PC** (10 or 11), with **Google Chrome**.
- A **paid Claude subscription** (Pro or Max): it gives you access to the "Code" tab of the app, where the plugin lives.
- Recommended: a **second SoundCloud account** for the gates (they ask you to follow, repost, comment). Your main account stays clean.
- Your **SoundCloud email**: you give it once during setup; the gates pass it on to the artists.

## 1. Install the Claude app

1. Download the app from [claude.ai/download](https://claude.ai/download) and install it. On Mac, drag it into Applications. On Windows, run the installer.
2. Open it and log in.
3. At the top of the window, click the **Code** tab. This is where everything happens.
4. If the app asks for a working folder, create a folder called `DJ` in Documents and choose it. Your music won't go there.
5. **Windows**: if the app asks you to install **Git for Windows**, accept and follow the installation it offers (default options). It needs it to run commands.

> **Talking to Claude**: you type at the bottom, in the text box, like in a messaging app, then press Enter. A message that starts with `/` is a command: when you type `/`, the list appears.

## 2. Get Chrome ready

1. Open the [**Claude**](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) extension on the Chrome Web Store (publisher: Anthropic) and click **Add to Chrome**.
2. Pin the extension (puzzle icon at the top right).
3. Log in to the extension with **the same Claude account** as in the app.
4. In this Chrome, log in to **SoundCloud with the account for the gates**.

While downloads are running, keep Chrome open and don't touch the tabs Claude has opened (they're grouped and colored).

## 3. Install the plugin

In the Code tab, open a new session and paste:

```
Install the sd-downloader plugin from the GitHub repo LouidJ/dj-downloader, turn on auto-update, then tell me when it's ready.
```

1. Claude asks for permission to change its settings: click **Allow**. It does everything else.
2. When it's ready, **open a new session**: the plugin loads at startup.

In the terminal (Claude Code), one command is enough: `/plugin install sd-downloader --marketplace LouidJ/dj-downloader`.

## 4. Your settings: two clicks, that's it

Click the **🎧 Set up SD Downloader** button above the box where you type (or type `/sd-downloader:setup`). If it doesn't show up, open another new session. Claude first checks that everything is ready. **On Windows**, it may ask you to install **Python**: on [python.org](https://www.python.org/downloads/), click Download Python, run the installer and **tick "Add python.exe to PATH"** before clicking Install. Then open a new session and type the command again.

It first asks for your **language**: everything else happens in your language. Next, Claude **figures out on its own** which SoundCloud account is logged in to Chrome, your email and your first name: nothing to type. It only asks **one question to click**: where to save the tracks (Music, a new folder on the Desktop, or a folder you pick in a window). After your first download, it will suggest the "To download" playlist trick once.

The rest is set for you: your account's likes, the Extended version (before the Radio one), and tracks already in your folder are never downloaded again. Change anything with one sentence ("also keep the radio versions", "my email is …").

At the end, Claude offers once, **with no obligation**, to follow the plugin's author on SoundCloud, then shows a 2-line summary and a **🚀 Launch** button. The summary tells you: on every download, Claude does the gates (follow, like, repost, comment) with your account, without asking again. If you'd rather it asks each time, say "ask me before the gates".

> **Just one permission.** At the start of setup, Claude warns you, then shows **a single** pop-up: click **Allow**. It covers the plugin for good, even after updates. Then the Chrome extension asks for access to soundcloud.com, hypeddit.com and droploud.com: each time, pick the option that **always** allows the site. On a Mac, if the system asks for access to Downloads or Music, allow it. After that, no more pop-ups while downloading.

## 5. First download

Click **🚀 Launch** at the end of setup. Claude asks which tracks (*All my likes*, *Liked today*, *My last 20 likes*, *Tracks from this playlist*). For your very first try, choose *Other* and type "last 3".

Then:
1. Claude skips the tracks already in your folder.
2. It keeps going on its own. In Chrome, you can see it open pages and click. The sound on the pages is muted.
3. At the end, a short chime, then a short report: how many new tracks, and one table. The files are already filed away. A **📂 Open the folder** button shows you the tracks; you can also have it open on its own next time.

It asks you nothing during the run. The only exceptions: a CAPTCHA (you do it yourself), a password, a payment, the wrong account being logged in, or more than 30 gates at once (SoundCloud could limit your account: you choose).

## Day to day

Click the **🎧 Download my new likes** button above the box where you type. That's it: Claude takes everything you've liked since last time.

For anything else, say it in your own words: "download what I've liked since Monday", "download my playlist", "download this playlist: link".

**The playlist trick**: create a "To download" playlist on SoundCloud. While you dig, add tracks to it. In the evening, say "download my playlist". Tracks you've already downloaded are never done again.

Other phrases: "remove #12 from the list", "also keep the radio versions", "WAV only", "show the report". The **⚙️ Settings** choice (from the 2nd launch) sets the formats (WAV, AIFF, MP3, one or several, or any), the versions (Extended, Radio or both), file-name cleaning (V2, master…) and zips (Trash or kept). If the artist only offers another format, the track is kept and flagged in the report.

## Reading the report

- **downloaded**: the file is in your folder.
- **already there**: you already had it, same version.
- **long set skipped**: longer than 45 minutes.
- **missing**: no free download (Beatport, Bandcamp…) or the gate is blocked. The reason is written next to it.
- **to retry**: done again automatically on the next run.

## Without Claude Code: with Cowork

In the Claude app, on the main screen (not the `</>` tab): **Customize → Plugins → Add**, marketplace `LouidJ/dj-downloader`, install **SD Downloader**. Open a new task, pick your music folder in **Project or folder**, then type `/sd-downloader:setup`.

- During setup, Claude asks for access to **Downloads** and your music folder: click **Allow** for each. Your settings and history stay in your music folder (hidden `.sd-downloader` folder).
- For websites, choose **Always allow for this site** (SoundCloud, Hypeddit, Droploud).
- Differences from Claude Code: no button above the text box and no end chime, and the folder doesn't open on its own (Claude tells you its name).

## If you get stuck

- **Claude is waiting**: look under its last message for choices or a **Go** button to click. If it has stopped, type "keep going until the end".
- **A permission window appears**: read it and click **Allow**. If it's Chrome asking for access to a site, pick the option that **always** allows it.
- **Chrome not connected**: Chrome open, Claude extension logged in to the same account, then "try again".
- **The Chrome connection keeps dropping** (especially on Droploud): during a download, only one Claude conversation in Chrome at a time; keep the Chrome window open and your Mac/PC awake; update Chrome and the Claude extension. If a gate is left on "Drop unlocked!", click **Download** yourself, then type "file it".
- **"Not installed yet"**: type `/sd-downloader:setup`.
- **CAPTCHA**: do it yourself in the tab, then type "done".
- **Stop everything**: Stop button next to the text box (or Esc). Nothing is lost, the next run picks up where it left off.
- **A free track marked as missing**: "Download this track: link".

## What Claude does in your name

- With the gates account: follow, like, repost, short comment, only when a gate requires it and after your "go".
- Give your first name and email to the gates that ask for them.
- Never: type a password, create an account, pay.
- Your settings and your tracking stay on your computer. Your audio files stay in your folder, even if you uninstall the plugin.

Respect the artists: only download what they offer for free.
