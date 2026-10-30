import { createFileRoute } from '@tanstack/react-router';
import { AdminPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/admin/doctors')({
  head: () => ({ meta: [{ title: 'Demo doctors — LungCare AI' }, { name: 'description', content: 'Academic doctor accounts and active workloads.' }, { property: 'og:title', content: 'Demo doctors — LungCare AI' }, { property: 'og:description', content: 'Academic doctor accounts and active workloads.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <AdminPage view="doctors"/>; }
