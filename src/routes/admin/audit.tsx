import { createFileRoute } from '@tanstack/react-router';
import { AdminPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/admin/audit')({
  head: () => ({ meta: [{ title: 'Audit trail — LungCare AI' }, { name: 'description', content: 'Sensitive operation audit history.' }, { property: 'og:title', content: 'Audit trail — LungCare AI' }, { property: 'og:description', content: 'Sensitive operation audit history.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <AdminPage view="audit"/>; }
