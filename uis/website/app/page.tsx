import { EvidenceSection } from '@/components/nexova/evidence-section'
import { FinalDeclaration } from '@/components/nexova/final-declaration'
import { GrainOverlay } from '@/components/nexova/grain-overlay'
import { HeroTransition } from '@/components/nexova/hero-transition'
import { ManifestoSection } from '@/components/nexova/manifesto-section'
import { MidPageSection } from '@/components/nexova/mid-page-section'
import { SiteFooter } from '@/components/nexova/site-footer'
import { SiteHeader } from '@/components/nexova/site-header'

export default function Page() {
  return (
    <main className="relative bg-obsidian">
      <GrainOverlay />
      <SiteHeader />
      <HeroTransition />
      <ManifestoSection />
      <MidPageSection />
      <EvidenceSection />
      <FinalDeclaration />
      <SiteFooter />
    </main>
  )
}
