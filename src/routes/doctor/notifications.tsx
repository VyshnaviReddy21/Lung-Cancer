import { createFileRoute } from '@tanstack/react-router';
import { NotificationsPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/doctor/notifications')({
  head: () => ({ meta: [{ title: 'Doctor notifications — LungCare AI' }, { name: 'description', content: 'Your private case assignment and session updates.' }, { property: 'og:title', content: 'Doctor notifications — LungCare AI' }, { property: 'og:description', content: 'Your private case assignment and session updates.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <NotificationsPage role="doctor"/>; }
