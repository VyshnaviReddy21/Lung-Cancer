import { createFileRoute } from '@tanstack/react-router';
import { RestrictedPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/unauthorized')({
  head: () => ({ meta: [{ title: 'Access restricted — LungCare AI' }, { name: 'description', content: 'This workspace requires an authorized account.' }, { property: 'og:title', content: 'Access restricted — LungCare AI' }, { property: 'og:description', content: 'This workspace requires an authorized account.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <RestrictedPage/>; }
