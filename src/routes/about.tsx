import { createFileRoute } from '@tanstack/react-router';
import { About } from '@/components/lungcare/public';
export const Route = createFileRoute('/about')({
  head: () => ({ meta: [{ title: 'About LungCare AI — Research and limitations' }, { name: 'description', content: 'Learn about the academic lung CT classification project and its limitations.' }, { property: 'og:title', content: 'About LungCare AI — Research and limitations' }, { property: 'og:description', content: 'Learn about the academic lung CT classification project and its limitations.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <About/>; }
