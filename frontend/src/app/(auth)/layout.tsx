/**
 * Auth layout — centered card for login/register pages.
 * Layout de autenticacao — card centralizado para paginas de login/registro.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-lg">
        {children}
      </div>
    </div>
  );
}
