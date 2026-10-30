import { createFileRoute } from '@tanstack/react-router';
import { ProfilePage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/doctor/availability')({
  head: () => ({ meta: [{ title: 'Doctor availability — LungCare AI' }, { name: 'description', content: 'Manage your availability for new case assignments.' }, { property: 'og:title', content: 'Doctor availability — LungCare AI' }, { property: 'og:description', content: 'Manage your availability for new case assignments.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <ProfilePage role="doctor" availability/>; }
