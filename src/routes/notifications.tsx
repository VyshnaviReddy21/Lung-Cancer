import { createFileRoute } from '@tanstack/react-router';
import { NotificationsPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/notifications')({
  head: () => ({ meta: [{ title: 'Notifications — LungCare AI' }, { name: 'description', content: 'Your private case and review updates.' }, { property: 'og:title', content: 'Notifications — LungCare AI' }, { property: 'og:description', content: 'Your private case and review updates.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <NotificationsPage/>; }
