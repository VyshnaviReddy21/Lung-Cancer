import { createFileRoute } from '@tanstack/react-router';
import { HistoryPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/history/')({
  head: () => ({ meta: [{ title: 'Case history — LungCare AI' }, { name: 'description', content: 'Search and follow your private case history.' }, { property: 'og:title', content: 'Case history — LungCare AI' }, { property: 'og:description', content: 'Search and follow your private case history.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <HistoryPage/>; }
