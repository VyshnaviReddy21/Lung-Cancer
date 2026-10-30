import { createFileRoute } from '@tanstack/react-router';
import { Home } from '@/components/lungcare/public';
export const Route = createFileRoute('/')({
  head: () => ({ meta: [{ title: 'LungCare AI — AI-assisted lung health' }, { name: 'description', content: 'CT image classification, explainable AI, and academic doctor review.' }, { property: 'og:title', content: 'LungCare AI — AI-assisted lung health' }, { property: 'og:description', content: 'CT image classification, explainable AI, and academic doctor review.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <Home/>; }
