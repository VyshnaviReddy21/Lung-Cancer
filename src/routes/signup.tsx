import { createFileRoute } from '@tanstack/react-router';
import { AuthPage } from '@/components/lungcare/public';
export const Route = createFileRoute('/signup')({
  head: () => ({ meta: [{ title: 'Create an account — LungCare AI' }, { name: 'description', content: 'Create a private patient account for academic CT analysis.' }, { property: 'og:title', content: 'Create an account — LungCare AI' }, { property: 'og:description', content: 'Create a private patient account for academic CT analysis.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <AuthPage signup/>; }
