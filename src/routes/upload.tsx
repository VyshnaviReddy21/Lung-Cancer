import { createFileRoute } from '@tanstack/react-router';
import { UploadPage } from '@/components/lungcare/workspace';
export const Route = createFileRoute('/upload')({
  head: () => ({ meta: [{ title: 'Upload a CT image — LungCare AI' }, { name: 'description', content: 'Securely upload a CT image for trained CNN analysis.' }, { property: 'og:title', content: 'Upload a CT image — LungCare AI' }, { property: 'og:description', content: 'Securely upload a CT image for trained CNN analysis.' }, { property: 'og:type', content: 'website' }, { name: 'twitter:card', content: 'summary_large_image' }] }),
  component: Page,
});
function Page() { return <UploadPage/>; }
