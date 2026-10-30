import { createFileRoute } from '@tanstack/react-router';
import { CasePage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/admin/cases/$caseId')({
  head: () => ({ meta: [{ title: 'Coordinator case details — LungCare AI' }, { name: 'description', content: 'Inspect case workflow and authorize reassignment.' }, { property: 'og:title', content: 'Coordinator case details — LungCare AI' }, { property: 'og:description', content: 'Inspect case workflow and authorize reassignment.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <CasePage role="admin" caseId={Route.useParams().caseId}/>; }
