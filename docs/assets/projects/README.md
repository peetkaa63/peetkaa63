# Screenshot sources

These are screenshots of the actual public `/login` pages, rendered locally from the linked repositories in Chromium at **1440 × 1000**, then saved as WebP. The application source and authentication behavior were not modified. Forms were left empty; no account, credentials, API call, test mode, or login submission was used. Each capture used a fresh browser context and waited for fonts and entrance animations.

| File | Source | Source commit |
| --- | --- | --- |
| `testops.webp` | [TestOps Copilot](https://github.com/peetkaa63/TestOps-Copilot) | `f0550a75623408291de9033b9e17ed0d1289dbae` |
| `warehouse.webp` | [Smart Warehouse](https://github.com/peetkaa63/smart-warehouse) | `f94721eea274ee2835d82b079bfd75f2a25edcac` |
| `learn.webp` | [Commit to Learn](https://github.com/peetkaa63/pcbweb) | `1131d863b4cdad217886f525ca6fbe192b75d0c6` |

All three repositories are collaborative forks. Only Commit to Learn explicitly credits Petr Kabanov as Backend Developer. Logos visible within the application screenshots are part of those interfaces; they do not imply personal client relationships or endorsements.

## Capture notes

- **TestOps Copilot:** Vite development preview. The current dependency resolution required installing the missing `@snack-uikit/locale` peer in the temporary checkout with `--no-save`. No browser errors in the final capture.
- **Smart Warehouse:** the committed lockfile and package manifest disagree on `@react-spring`, so a normal dependency install replaced `npm ci` in the temporary checkout. Motion versions matched the original lockfile (`framer-motion` 12.23.24, `motion-dom` 12.23.23, `motion-utils` 12.23.6). The screenshot uses the standard production build, because the development preview throws a Motion spring/keyframe invariant. No browser errors in the final capture.
- **Commit to Learn:** CRA development preview. Its proxy configuration required a local host-header configuration adjustment, limited to the temporary preview server. No browser errors in the final capture.

No changes were pushed to the source project repositories. These source-project dependencies are **not** dependencies of the portfolio: it serves the resulting static images only.
