import { createFileRoute } from '@tanstack/react-router';
import { HistoryPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/doctor/cases/')({
  head: () => ({ meta: [{ title: 'Assigned cases — LungCare AI' }, { name: 'description', content: 'Your authorized academic review queue.' }, { property: 'og:title', content: 'Assigned cases — LungCare AI' }, { property: 'og:description', content: 'Your authorized academic review queue.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <HistoryPage role="doctor"/>; }
