import { createFileRoute } from '@tanstack/react-router';
import { AuthPage } from '@/components/lungcare/public';
export const Route = createFileRoute('/doctor/login')({
  head: () => ({ meta: [{ title: 'Doctor sign in — LungCare AI' }, { name: 'description', content: 'Access the academic demonstration doctor review portal.' }, { property: 'og:title', content: 'Doctor sign in — LungCare AI' }, { property: 'og:description', content: 'Access the academic demonstration doctor review portal.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <AuthPage doctor/>; }
