import { createFileRoute } from '@tanstack/react-router';
import { AdminPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/admin/sessions')({
  head: () => ({ meta: [{ title: 'Review sessions — LungCare AI' }, { name: 'description', content: 'Durable two-hour academic review sessions.' }, { property: 'og:title', content: 'Review sessions — LungCare AI' }, { property: 'og:description', content: 'Durable two-hour academic review sessions.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <AdminPage view="sessions"/>; }
