import { createFileRoute } from '@tanstack/react-router';
import { Dashboard } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/admin/dashboard')({
  head: () => ({ meta: [{ title: 'Coordinator overview — LungCare AI' }, { name: 'description', content: 'Academic case coordination overview.' }, { property: 'og:title', content: 'Coordinator overview — LungCare AI' }, { property: 'og:description', content: 'Academic case coordination overview.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <Dashboard role="admin"/>; }
