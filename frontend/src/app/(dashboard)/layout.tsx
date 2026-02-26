/**
 * Dashboard layout with sidebar.
 * Layout do dashboard com sidebar.
 */
import NotificationBadge from "@/components/layout/NotificationBadge";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar / Barra lateral */}
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
            <li>
              <a
                href="/standings"
                className="block rounded px-3 py-2 hover:bg-gray-800"
              >
                Standings / Classificacao
              </a>
            </li>
          </ul>
          {/* Admin section / Secao admin */}
          <div className="mt-6 border-t border-gray-700 pt-4">
            <p className="mb-2 px-3 text-xs font-semibold uppercase text-gray-400">
              Admin
            </p>
            <ul className="space-y-2">
              <li>
                <a
                  href="/admin/users"
                  className="block rounded px-3 py-2 hover:bg-gray-800"
                >
                  Users / Usuarios
                </a>
              </li>
              <li>
                <a
                  href="/admin/roles"
                  className="block rounded px-3 py-2 hover:bg-gray-800"
                >
                  Roles / Papeis
                </a>
              </li>
              <li>
                <a
                  href="/admin/permissions"
                  className="block rounded px-3 py-2 hover:bg-gray-800"
                >
                  Permissions / Permissoes
                </a>
              </li>
            </ul>
          </div>
        </nav>
      </aside>
      {/* Main content / Conteudo principal */}
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
