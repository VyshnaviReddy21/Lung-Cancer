import { createFileRoute } from '@tanstack/react-router';
import { Dashboard } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/doctor/dashboard')({
  head: () => ({ meta: [{ title: 'Doctor overview — LungCare AI' }, { name: 'description', content: 'Personalized academic doctor case workload.' }, { property: 'og:title', content: 'Doctor overview — LungCare AI' }, { property: 'og:description', content: 'Personalized academic doctor case workload.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <Dashboard role="doctor"/>; }
