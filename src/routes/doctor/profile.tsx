import { createFileRoute } from '@tanstack/react-router';
import { ProfilePage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/doctor/profile')({
  head: () => ({ meta: [{ title: 'Doctor profile — LungCare AI' }, { name: 'description', content: 'Manage your demonstration doctor profile.' }, { property: 'og:title', content: 'Doctor profile — LungCare AI' }, { property: 'og:description', content: 'Manage your demonstration doctor profile.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <ProfilePage role="doctor"/>; }
