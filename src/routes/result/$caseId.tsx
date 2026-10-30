import { createFileRoute } from '@tanstack/react-router';
import { CasePage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/result/$caseId')({
  head: () => ({ meta: [{ title: 'Analysis result — LungCare AI' }, { name: 'description', content: 'Private CNN probabilities, explanations, and demonstration review.' }, { property: 'og:title', content: 'Analysis result — LungCare AI' }, { property: 'og:description', content: 'Private CNN probabilities, explanations, and demonstration review.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <CasePage caseId={Route.useParams().caseId}/>; }
