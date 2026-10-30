import { createFileRoute } from '@tanstack/react-router';
import { Dashboard } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/dashboard')({
  head: () => ({ meta: [{ title: 'Patient overview — LungCare AI' }, { name: 'description', content: 'Your private case and review overview.' }, { property: 'og:title', content: 'Patient overview — LungCare AI' }, { property: 'og:description', content: 'Your private case and review overview.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <Dashboard/>; }
