import { createFileRoute } from '@tanstack/react-router';
import { ReportsPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/reports')({
  head: () => ({ meta: [{ title: 'Academic reports — LungCare AI' }, { name: 'description', content: 'Access your private academic PDF reports.' }, { property: 'og:title', content: 'Academic reports — LungCare AI' }, { property: 'og:description', content: 'Access your private academic PDF reports.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <ReportsPage/>; }
