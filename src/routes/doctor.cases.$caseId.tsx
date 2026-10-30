import { createFileRoute } from '@tanstack/react-router';
import { CasePage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/doctor/cases/$caseId')({
  head: () => ({ meta: [{ title: 'Doctor case review — LungCare AI' }, { name: 'description', content: 'Review an assigned case and submit an academic assessment.' }, { property: 'og:title', content: 'Doctor case review — LungCare AI' }, { property: 'og:description', content: 'Review an assigned case and submit an academic assessment.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <CasePage role="doctor" caseId={Route.useParams().caseId}/>; }
