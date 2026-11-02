# First steps: you've never used Claude

*[Version française](GUIDE.md) · Interactive guide, one question at a time: [open](https://louidj.github.io/dj-downloader/)*

Setup takes about 20 minutes, one time only. After that, it's one sentence each time. No code to write.

## 0. What you need

- A **Mac** or a **Windows PC** (10 or 11), with **Google Chrome**.
- A **paid Claude subscription** (Pro or Max): it gives you access to the "Code" tab of the app, where the plugin lives.
- Recommended: a **second SoundCloud account** for the gates (they ask you to follow, repost, comment). Your main account stays clean.
- Recommended: a **secondary email address**: the gates pass it on to the artists.

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

## 4. Your settings: you just tick boxes

Type `/sd-downloader:setup`. It shows up as soon as you type `/` and then "sd". If it doesn't show up, open another new session. Claude first checks that everything is ready. **On Windows**, it may ask you to install **Python**: on [python.org](https://www.python.org/downloads/), click Download Python, run the installer and **tick "Add python.exe to PATH"** before clicking Install. Then open a new session and type the command again.

Next, Claude **figures out on its own** which SoundCloud account is logged in to Chrome, your artist name and the folders where you already have tracks. It offers everything as **choices to click**:
- the account for the gates and the profile whose likes it downloads;
- the Droploud box: whether it can accept the artist's news emails for you when a gate requires it (otherwise, those tracks are marked as missing);
- Radio and Extended: only the Extended, or both;
- where to save the tracks, and which folders to search for the ones you already have, so nothing gets downloaded twice;
- your artist name, so it never downloads your own tracks;
- optionally, a "To download" playlist.

At the end, Claude offers, **with no obligation**, to follow the plugin's author on SoundCloud. It offers again after a big playlist, unless you pick "Don't ask again". If you already follow him, it doesn't ask.

The only thing to type: **your email and your first name** for the gates. A secondary address is recommended.

> **Just one permission.** At the start of setup, Claude warns you, then shows **a single** pop-up: click **Allow**. It covers the plugin for good, even after updates. Then the Chrome extension asks for access to soundcloud.com, hypeddit.com and droploud.com: each time, pick the option that **always** allows the site. On a Mac, if the system asks for access to Downloads or Music, allow it. After that, no more pop-ups while downloading.

## 5. First test

Type `/sd-downloader:download-likes` (or just write "download"). Claude shows choices: **nothing to type, you tick, then click Go**.

- **Which tracks do I download?** The choices are *My new likes*, *Liked today*, *My last 20 likes* and *My playlist*. With *Other*, you can type a number or a date, or paste a link.
- **Do I run everything through to the report?** The choices are **Go** and *Show me first*.

For your very first try, choose *Other* and type "last 3".

After you click **Go**:
1. Claude compares with the tracks already on your computer and tells you which ones it skips.
2. It keeps going on its own. In Chrome, you can see it open pages and click. The sound on the pages is muted.
3. At the end, it gives you the report. The files are already filed away.

The Go button covers the whole run. Its description says what Claude will do in your name: follow, like, repost, comment, give your email. After that, it doesn't ask you anything until the report. The only exceptions: a CAPTCHA (you do it yourself), a password, a payment or the wrong account being logged in.

## Day to day

Always the same: `/sd-downloader:download-likes`, you tick, you click **Go**.

If you'd rather type, Claude understands your own words too, and then only asks you the Go question. For example: "download what I've liked since Monday", "download this playlist: link". Add "go for everything" and it starts without even showing the button.

**The playlist trick**: create a "To download" playlist on SoundCloud. While you dig, add tracks to it. In the evening, tick *My playlist*. Tracks you've already downloaded are never done again.

Other phrases: "remove #12 from the list", "also compare with my USB stick", "also keep the radio versions", "show the report".

## Reading the report

- **downloaded**: the file is in your folder.
- **already there**: you already had it, same version.
- **long set skipped**: longer than 45 minutes.
- **your own track**: left aside.
- **missing**: no free download (Beatport, Bandcamp…) or the gate is blocked. The reason is written next to it.
- **to retry**: done again automatically on the next run.

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
