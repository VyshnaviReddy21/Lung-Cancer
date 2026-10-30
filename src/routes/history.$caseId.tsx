import { createFileRoute } from '@tanstack/react-router';
import { CasePage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/history/$caseId')({
  head: () => ({ meta: [{ title: 'Case details — LungCare AI' }, { name: 'description', content: 'Private case image, analysis, review, and report.' }, { property: 'og:title', content: 'Case details — LungCare AI' }, { property: 'og:description', content: 'Private case image, analysis, review, and report.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <CasePage caseId={Route.useParams().caseId}/>; }
