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

To preview locally from the repository root:

```sh
python3 -m http.server 4173 --directory docs
```

Open `http://localhost:4173`. The site uses relative asset URLs and also works under the GitHub Pages project path `/peetkaa63/`. JavaScript progressively adds the mobile menu, section reveals, active section navigation, a screenshot gallery and copying for the Telegram handle and message template. Navigation, project details and contact guidance remain usable without JavaScript; screenshot links then open the original images. The gallery supports Escape, arrow keys and focus return. Project context is based on each repository's README and keeps team credits explicit.

The homepage introduces the real Commit to Learn request path with a four-stage code explorer. Native radio controls switch between pinned source excerpts using CSS, including without JavaScript; arrow keys change the selected stage. It is a reading aid for the team codebase, not a running API demo.

A header button switches between the original dark theme and a light palette on both pages. Only the light/dark preference is saved under `portfolio-theme` in localStorage. A small local head script restores it before paint and keeps open tabs and restored pages in sync. Storage errors do not prevent switching in the current page. Without JavaScript the original dark theme remains available.

The system's reduced-motion preference disables animation. The footer also offers a manual motion toggle, saved locally when browser storage is available. The optional contact brief builds a message from the selected service and any details the visitor enters. Service links preselect a format and open the brief. Input is kept only in the current page; it is not persisted, sent to a server, or added to the Telegram URL. Visitors copy the message (or select the preview manually) and send it themselves. Without JavaScript, the contact guide and direct Telegram links remain available.

Before opening a Pull Request, run:

```sh
python3 scripts/check_portfolio.py
node --check docs/assets/main.js
node --check docs/assets/theme.js
```

Project images show public login screens from the linked repositories, not client work or authenticated dashboards. See [screenshot sources](docs/assets/projects/README.md) for their origin. Manrope is hosted locally under the [SIL Open Font License](docs/assets/fonts/OFL.txt).

The [Commit to Learn case study](docs/projects/commit-to-learn.html) explains the documented backend role, a verified request path and the data model. Source links are pinned to the reviewed commit. The page describes the team codebase without attributing individual modules to a person or claiming a production result.

`scripts/check_portfolio.py` validates every HTML file under `docs/`, including links between pages. Its regression tests run with `python3 -B -m unittest discover -s scripts -p 'test_*.py'` and are included in Portfolio CI.
