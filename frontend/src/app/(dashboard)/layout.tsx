/**
 * Dashboard layout with sidebar placeholder.
 * Layout do dashboard com placeholder de sidebar.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar placeholder / Placeholder da sidebar */}
      <aside className="w-64 bg-gray-900 p-4 text-white">
        <h2 className="mb-8 text-xl font-bold">TeamPrincipal</h2>
        <nav>
          <ul className="space-y-2">
            <li>
              <a
                href="/dashboard"
                className="block rounded px-3 py-2 hover:bg-gray-800"
              >
                Dashboard
              </a>
            </li>
            <li>
              <a
                href="/championships"
                className="block rounded px-3 py-2 hover:bg-gray-800"
              >
                Championships / Campeonatos
              </a>
            </li>
            <li>
              <a
                href="/drivers"
                className="block rounded px-3 py-2 hover:bg-gray-800"
              >
                Drivers / Pilotos
              </a>
            </li>
          </ul>
        </nav>
      </aside>
      {/* Main content / Conteudo principal */}
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
