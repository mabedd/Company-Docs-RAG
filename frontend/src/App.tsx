import { useState } from 'react'
import { AdminPanel } from './components/AdminPanel'
import { ChatPanel } from './components/ChatPanel'
import { IngestPanel } from './components/IngestPanel'
import { Layout, type Tab } from './components/Layout'
import { useHealth } from './hooks/useHealth'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('ask')
  const { health, loading, error, refresh } = useHealth()

  const panel = (() => {
    switch (activeTab) {
      case 'ingest':
        return <IngestPanel onIndexedChange={refresh} />
      case 'admin':
        return <AdminPanel onIndexedChange={refresh} />
      default:
        return <ChatPanel onIndexedChange={refresh} />
    }
  })()

  return (
    <Layout
      activeTab={activeTab}
      onTabChange={setActiveTab}
      healthOnline={health?.status === 'ok'}
      documentsIndexed={health?.documents_indexed ?? null}
      healthLoading={loading}
      healthError={error}
      onRefreshHealth={refresh}
    >
      {panel}
    </Layout>
  )
}

export default App
