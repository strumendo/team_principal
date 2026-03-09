/**
 * Loading state component with spinner animation.
 * Componente de estado de carregamento com animacao de spinner.
 */

interface LoadingStateProps {
  message?: string;
}

export default function LoadingState({ message = "Loading... / Carregando..." }: LoadingStateProps) {
  return (
    <div className="flex items-center gap-3 py-8">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
      <p className="text-gray-500">{message}</p>
    </div>
  );
}
