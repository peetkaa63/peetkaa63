<div align="center">

# Petr Kabanov

**Web apps · Telegram bots · AI automation · Digital products**

[**Portfolio Website**](https://peetkaa63.github.io/peetkaa63/) · [**Telegram / Contact**](https://t.me/rove63) · [**Repositories**](https://github.com/peetkaa63?tab=repositories)

</div>

---

### About me

I'm a Financial University student exploring software engineering, AI-assisted development and practical digital products.

I work on web applications, Telegram services and automation projects. I'm interested in turning ideas into usable products, with clear requirements, maintainable code and reliable delivery.

### Selected projects

| Project | What it does | Notes |
| --- | --- | --- |
| **StudHubMeet** | Student profiles, matching and communication through a Telegram bot and Mini App | Team project; contributed to bot, API, Mini App and admin workflows. Private source code |
| **Предложка ФУ** | Telegram bot for student submissions, moderation and scheduled channel posts | Team project; worked on moderation, publication queues and notification reliability. Private source code |
| [TestOps Copilot](https://github.com/peetkaa63/TestOps-Copilot) | AI-assisted tooling for software testing and QA workflows | Explore the architecture, services and documentation in the repository |
| [Smart Warehouse](https://github.com/peetkaa63/smart-warehouse) | Warehouse management platform prototype with dashboards, analytics and automation components | Collaborative / forked project |
| [Commit to Learn](https://github.com/peetkaa63/pcbweb) | Educational web platform for students and instructors | Team project; repository README credits my backend contribution |

> Some of these repositories are collaborative forks. See each project's README for team credits and implementation details. A repository description is not a guarantee that every feature is deployed or production-ready.

### Currently exploring

- Web applications and APIs
- Telegram bots and mini apps
- AI-powered workflows and process automation
- Secure development, testing and CI/CD

### Let's talk

If you have an idea for a website, web app, Telegram bot or automation, feel free to reach out:

**[Message me on Telegram →](https://t.me/rove63)**

---

<sub>Based in Moscow · Learning, building and improving real projects.</sub>

### Portfolio development

The portfolio is a static, Russian-language site in `docs/`, published with GitHub Pages from `main` → `/docs`. No build step, API keys, paid services, or runtime dependencies are required. Keep the current Pages source when merging changes.

The project section starts with StudHubMeet and Предложка ФУ. Their cards describe the product, stack and contribution, and mark the source as closed. A keyboard-accessible project index links directly to all five cards and also works without JavaScript. These cards use text and decorative icons; the existing gallery continues to show the three sourced screenshots of the open projects.

To preview locally from the repository root:

```sh
python3 -m http.server 4173 --directory docs
```

Open `http://localhost:4173`. The site uses relative asset URLs and also works under the GitHub Pages project path `/peetkaa63/`. JavaScript progressively adds the mobile menu, section reveals, active section navigation, a screenshot gallery and copying for the Telegram handle and message template. Navigation, project details and contact guidance remain usable without JavaScript; screenshot links then open the original images. The gallery supports Escape, arrow keys, horizontal touch/pen swipes and focus return. Vertical and cancelled gestures keep the current image. Project context is based on each repository's README and keeps team credits explicit.

The gallery links each screenshot to its case study, or to the source repository when no case is available. It reserves the image area during loading, reports failures and offers a retry. Each selection owns its loading callbacks, so slow responses from an older selection or a closed dialog cannot overwrite the current view. Changing between mobile and desktop navigation transfers keyboard focus to the equivalent visible control.

Clipboard writes are serialized across the copy controls. While an OS write is pending, the controls expose `aria-disabled` and the active control exposes `aria-busy`; keyboard focus stays in place. After success or failure, copying is available again. Editing the brief while copying still produces the existing warning to copy the updated text.

The homepage leads with my name, development focus, education and selected projects. Service cards link to concrete project examples, while the about section groups technologies by backend/data, interfaces/Telegram and engineering practice. Contact copy supports project enquiries and team or job proposals without claiming availability or a response time.

The “Печать / сохранить в PDF” button opens the browser's native print dialog. The homepage's print-only stylesheet reuses the profile, education, stack and all five project cards, and puts GitHub/Telegram URLs below the name. It removes navigation, screenshots, forms and interactive controls, and uses a white background in either theme. The browser's Print command also works without JavaScript; the button is then hidden. No separate copy of the CV or PDF file needs to be maintained.

The homepage introduces the real Commit to Learn request path with a four-stage code explorer. Native radio controls switch between pinned source excerpts using CSS, including without JavaScript; arrow keys change the selected stage. It is a reading aid for the team codebase, not a running API demo.

A header button switches between the original dark theme and a light palette on every page. Only the light/dark preference is saved under `portfolio-theme` in localStorage. A small local head script restores it before paint and keeps open tabs and restored pages in sync. Storage errors do not prevent switching in the current page. Without JavaScript the original dark theme remains available.

The system's reduced-motion preference disables animation. The footer also offers a manual motion toggle, saved locally when browser storage is available. The head script restores that choice before the first animation; changes sync between open tabs and restored pages. The optional contact brief builds a message from the selected service and any details the visitor enters. Service links preselect a format, open the brief and keep the focused task field visible on short screens. Restored form values refresh the message on `pageshow`. Input is kept only in the current page; it is not persisted, sent to a server, or added to the Telegram URL. Visitors copy the message (or select the preview manually) and send it themselves. Without JavaScript, the contact guide and direct Telegram links remain available.

Before opening a Pull Request, run:

```sh
python3 scripts/check_portfolio.py
node --check docs/assets/main.js
node --check docs/assets/theme.js
```

Project images show public login screens from the linked repositories, not client work or authenticated dashboards. See [screenshot sources](docs/assets/projects/README.md) for their origin. Manrope is hosted locally under the [SIL Open Font License](docs/assets/fonts/OFL.txt).

The [Commit to Learn case study](docs/projects/commit-to-learn.html) explains the documented backend role, a verified request path and the data model. Source links are pinned to the reviewed commit. The page describes the team codebase without attributing individual modules to a person or claiming a production result.

The [TestOps Copilot case study](docs/projects/testops-copilot.html) follows the generation request from the frontend through the gateway and Core Agent into Celery. It explains status responses and the TaskRecord / TaskArtifact storage model, with links pinned to source commit `005db456da6225d6044f4d9a22c85c9ac68334c1`. It describes the team codebase; runtime availability and AI output quality were not evaluated. The reused login screenshot has its own source version documented in `docs/assets/projects/README.md`. Both case studies link to each other, and the TestOps case links back to the contact brief.

`scripts/check_portfolio.py` validates every HTML file under `docs/`, including links between pages, directory/query links, one primary heading, nonempty titles and the targets of labels and ARIA references. It also checks `docs/sitemap.xml` against the canonical URLs of all pages. The sitemap can be submitted to search engines at `https://peetkaa63.github.io/peetkaa63/sitemap.xml`. Its regression tests run with `python3 -B -m unittest discover -s scripts -p 'test_*.py'` and are included in Portfolio CI.

The homepage's “Обсудить проект” button opens the contact brief. Service links preselect the format and focus the task field while preserving entered details. The direct `#project-brief` link also opens the brief with JavaScript; without it, the same link reaches the native disclosure and contact guide. Section navigation transfers keyboard focus to the destination. A theme selected when browser storage is blocked remains active when the current page is restored.

Browser checks discover every HTML page under `docs/` and check them at 320, 390, 760 and 1440 pixels in both themes. They also cover short/landscape screens, keyboard navigation, the gallery, brief generation, clipboard races/fallback, blocked storage, restored pages, case navigation, privacy and the no-JavaScript version. axe-core checks WCAG 2 A/AA, 2.1 AA, 2.2 AA and best-practice rules in both themes, with the brief and gallery open as well. To run them locally:

```sh
python3 -m pip install -r tests/browser/requirements.txt
npm ci --prefix tests/browser --ignore-scripts --no-audit --no-fund
python3 -m playwright install chromium
python3 -B -m unittest discover -s tests/browser -p 'test_*.py' -v
```

The test suite starts a temporary local server; no application backend or external service is required. To use an existing Chromium installation, set `PORTFOLIO_CHROMIUM` to its executable path for the test command. Browser test packages are development dependencies only; the published site still has no runtime dependencies.

CI preserves the `browser-checks` Chromium job and adds separate Firefox and WebKit jobs. For another engine locally, install it with `python3 -m playwright install --with-deps firefox` (or `webkit`) and set `PORTFOLIO_BROWSER=firefox` for the unittest command. When `PORTFOLIO_ARTIFACTS` points to a directory, failed scenarios save screenshots; CI uploads those as artifacts. See [the audit report](AUDIT.md) for the scope, reproduced bugs, fixes and limits of verification.
