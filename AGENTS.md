<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

## Application architecture
- Keep TanStack Start file routing for the React frontend because the managed hosting bootstrap requires it; each content route owns metadata and shared screens live outside the routes directory.
- Keep all Flask, MongoDB, TensorFlow, and private file operations in the separately deployed `backend/` Python application, never in the Worker import graph, because these dependencies require a Python server.
- Route browser requests through one API client using `VITE_API_BASE_URL`, credentialed HTTP-only cookie sessions and an origin-checked CSRF header; no browser token or patient-data persistence.
- Require a verified model manifest alongside the complete SavedModel before enabling inference; explanation generation requires exported feature/gradient access and must otherwise report unavailable rather than approximate it.
- Keep Flask liveness separate from dependency readiness; enforce production MongoDB TLS and transaction-capable topology before database workflows, because a running process or ping alone cannot prove safe persistence.
