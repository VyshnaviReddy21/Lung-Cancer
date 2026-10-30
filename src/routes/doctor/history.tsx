import { createFileRoute } from '@tanstack/react-router';
import { HistoryPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/doctor/history')({
  head: () => ({ meta: [{ title: 'Doctor review history — LungCare AI' }, { name: 'description', content: 'Your persisted academic review history.' }, { property: 'og:title', content: 'Doctor review history — LungCare AI' }, { property: 'og:description', content: 'Your persisted academic review history.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <HistoryPage role="doctor" reviewHistory/>; }
