import { createFileRoute } from '@tanstack/react-router';
import { Contact } from '@/components/lungcare/public';
export const Route = createFileRoute('/contact')({
  head: () => ({ meta: [{ title: 'Contact — LungCare AI' }, { name: 'description', content: 'Contact the LungCare AI academic project team.' }, { property: 'og:title', content: 'Contact — LungCare AI' }, { property: 'og:description', content: 'Contact the LungCare AI academic project team.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <Contact/>; }
