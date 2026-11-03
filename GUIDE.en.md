# First steps: you've never used Claude

*[Version française](GUIDE.md) · Interactive guide, one question at a time: [open](https://louidj.github.io/dj-downloader/)*

Setup: ~15 minutes, once. After that, one sentence each time. No code to write.

## 0. What you need

- A **Mac** or a **Windows PC** (10 or 11), with **Google Chrome**.
- A **paid Claude plan** (Pro or Max): the plugin runs in the Claude app (Cowork), and the Chrome extension needs it too.
- Recommended: a **second SoundCloud account** for the gates (they ask you to follow, repost, comment). Your main account stays clean.

## 1. Install the Claude app

1. Download the app from [claude.ai/download](https://claude.ai/download) and install it: on Mac, drag it into Applications; on Windows, run the installer.
2. Open it and sign in. You land on the main screen (speech-bubble icon at the top left): that's where everything happens.

> **Talking to Claude**: you type at the bottom, in the text box, like in a messaging app, then Enter. A message starting with `/` is a command: type `/` and the list shows up.

## 2. Get Chrome ready

1. Open the [**Claude**](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) extension on the Chrome Web Store (publisher: Anthropic) and click **Add to Chrome**.
2. Pin the extension (puzzle icon at the top right).
3. Sign in to the extension with **the same Claude account** as in the app.
4. In this Chrome, sign in to **SoundCloud with the account for the gates**.

During downloads, keep Chrome open and don't touch the tabs Claude opened (they're grouped and colored).

## 3. Install the plugin

1. In the app, on the main screen, click **Customize** in the left sidebar, then **Plugins**.
2. Click **Add**, then the option to add a marketplace, and paste `LouidJ/dj-downloader`.
3. Install **SD Downloader** from the list.

## 4. Before every task: your folders and Auto mode

Do this for **every** new SD Downloader task (setup included):

1. Click **Create** at the top left: a new task opens.
2. Click **+** next to the text box, then **Add folder**, and pick **Downloads**. Do it again for the folder where your tracks go (for example **Music**).
3. At the bottom right of the text box, click **Manual** and pick **Auto**.

> **Why Auto?** In Manual mode, Claude asks permission for every batch of clicks in Chrome: dozens of pop-ups. In Auto, it acts on its own for routine actions and only asks for risky ones. Don't use the mode that skips all permissions.

## 5. Your settings

In the task, type `/sd-downloader:setup`.

Claude asks for your **language**: everything else happens in that language. Then it finds **on its own** the Chrome where SoundCloud is open, the account signed in, your email and first name: nothing to type. It files the tracks in the folder you added (in Music, it creates "SoundCloud Downloads"). A **↩️ Go back** button always lets you change your mind.

The rest is set for you: your account's likes, the Extended version (before the Radio one), and tracks already in your folder are never downloaded again. Your settings and history stay in your music folder (hidden `.sd-downloader` folder).

At the end, Claude offers once, **no obligation**, to follow the plugin's author on SoundCloud, then shows a 2-line summary and a **🚀 Launch** button. The summary warns you: on every download, Claude will do the gates (follow, like, repost, comment) with your account, without asking again. If you'd rather it asks each time, say "ask me before the gates".

> **The pop-ups to accept, once**: for soundcloud.com, hypeddit.com and droploud.com, pick **Always allow for this site**; for the connection to your Chrome, **Allow**.

## 6. First download

Click **🚀 Launch** at the end of setup. Claude asks which tracks (*All my likes*, *Liked today*, *My last 20 likes*, *The tracks of this playlist*). For a very first try, pick *Other* and type "last 3".

Then:
1. Claude skips tracks already in your folder.
2. It goes through everything on its own. In Chrome, you see it open pages and click. Page sound is muted.
3. At the end, a short report: how many new tracks, and one table. The files are already in your folder.

It asks nothing during the run. Only exceptions: a CAPTCHA (you do it yourself), a password, a payment, the wrong account signed in, or more than 30 gates at once (SoundCloud could limit your account: you choose).

## Day to day

New task, your two folders with **+**, **Auto** mode, then type "download my new likes". Claude takes everything you liked since last time.

For anything else, say it in your own words: "download what I liked since Monday", "download my playlist", "download this playlist: link".

**The playlist trick**: create a "To download" playlist on SoundCloud. While you dig, add tracks to it. In the evening, say "download my playlist". Tracks already downloaded are never done twice.

Other phrases: "remove #12 from the list", "keep the radio versions too", "WAV only", "show the report". The **⚙️ Settings** choice (from the 2nd launch on) sets formats (WAV, AIFF, MP3, one or several, or any), versions (Extended, Radio or both), file name cleaning (V2, master…) and zips (Trash or kept). If the artist only offers another format, the track is kept and flagged in the report.

## Reading the report

- **downloaded**: the file is in your folder.
- **already there**: you already had it, same version.
- **long set skipped**: longer than 45 minutes.
- **missing**: no free download (Beatport, Bandcamp…) or the gate is blocked. The reason is written next to it.
- **to retry**: done again automatically on the next run.

## You also have Claude Code?

The plugin works in the **Code** tab (`</>`) too: `/plugin install sd-downloader --marketplace LouidJ/dj-downloader`, then the **🎧** button above the text box. There you get fewer permission pop-ups, a short chime at the end, and an **📂 Open folder** button. **Windows**: the app may ask for **Git for Windows**, and Claude may ask for **Python** ([python.org](https://www.python.org/downloads/), tick "Add python.exe to PATH").

## If you get stuck

- **Claude is waiting**: look under its last message for choices or a **Go** button to click. If it has stopped, type "keep going until the end".
- **A pop-up on every click**: the task is in Manual mode. Switch it to **Auto**, at the bottom right.
- **Claude can't find your folder**: click **+**, then **Add folder**, and pick it. Then "done".
- **Chrome isn't connected**: Chrome open, Claude extension signed in to the same account, then "try again".
- **The Chrome connection keeps dropping** (mostly on Droploud): during a download, only one Claude conversation in Chrome at a time; keep the Chrome window open and the Mac/PC awake; update Chrome and the Claude extension. If a gate is stuck on "Drop unlocked!", click **Download** yourself, then say "file it".
- **"Not set up yet"**: type `/sd-downloader:setup`.
- **CAPTCHA**: do it yourself in the tab, then "done".
- **Stop everything**: Stop button next to the text box (or Esc). Nothing is lost, the next run picks up where it left off.
- **A free track marked missing**: "Download this track: link".

## What Claude does in your name

- With the gates account: follow, like, repost, short comment, only when a gate requires it.
- Give your first name and email to gates that ask for them.
- Never: type a password, create an account, pay, open a link found in a downloaded file.
- Your settings and tracking stay in your music folder. Your audio files stay in your folder, even if you uninstall the plugin.

Respect the artists: only download what they give away for free.
