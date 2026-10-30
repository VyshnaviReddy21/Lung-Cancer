import { createFileRoute } from '@tanstack/react-router';
import { ProfilePage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/profile')({
  head: () => ({ meta: [{ title: 'Patient profile — LungCare AI' }, { name: 'description', content: 'Manage your LungCare AI patient profile.' }, { property: 'og:title', content: 'Patient profile — LungCare AI' }, { property: 'og:description', content: 'Manage your LungCare AI patient profile.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <ProfilePage/>; }
