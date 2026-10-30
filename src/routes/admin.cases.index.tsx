import { createFileRoute } from '@tanstack/react-router';
import { HistoryPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/admin/cases/')({
  head: () => ({ meta: [{ title: 'Case management — LungCare AI' }, { name: 'description', content: 'Coordinate authorized case assignments.' }, { property: 'og:title', content: 'Case management — LungCare AI' }, { property: 'og:description', content: 'Coordinate authorized case assignments.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <HistoryPage role="admin"/>; }
