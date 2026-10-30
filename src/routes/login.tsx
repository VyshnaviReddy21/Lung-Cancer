import { createFileRoute } from '@tanstack/react-router';
import { AuthPage } from '@/components/lungcare/public';
export const Route = createFileRoute('/login')({
  head: () => ({ meta: [{ title: 'Patient sign in — LungCare AI' }, { name: 'description', content: 'Secure access to your personal LungCare AI workspace.' }, { property: 'og:title', content: 'Patient sign in — LungCare AI' }, { property: 'og:description', content: 'Secure access to your personal LungCare AI workspace.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <AuthPage/>; }
